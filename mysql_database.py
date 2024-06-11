import mysql.connector
import csv
import pandas as pd
from bokeh.plotting import figure, output_file, show
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import numpy as np
import unittest

class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass

class CSVImportError(Exception):
    """Custom exception for CSV import errors."""
    pass

class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass

class DatabaseConnector:
    """
    A class used to connect to a MySQL database.
    """
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database.")
        except mysql.connector.Error as err:
            raise DatabaseConnectionError(f"Database connection failed: {err}")

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Disconnected from the database.")

class CSVImporter(DatabaseConnector):
    """
    A class used to import CSV data into a MySQL database table, inheriting from DatabaseConnector.
    """
    def __init__(self, host, user, password, database):
        super().__init__(host, user, password, database)

    def import_csv_to_db(self, csv_file_path, table_name):
        try:
            with open(csv_file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  # Skip the header row if present
                for row in csvreader:
                    values = ', '.join(['"' + str(val) + '"' for val in row])
                    query = f"INSERT INTO {table_name} VALUES (NULL, {values})"
                    self.cursor.execute(query)
            self.connection.commit()
            print("Data imported successfully.")
        except FileNotFoundError as e:
            raise CSVImportError(f"CSV file not found: {e}")
        except mysql.connector.Error as err:
            raise CSVImportError(f"Error importing CSV to database: {err}")

class DataProcessor(DatabaseConnector):
    """
    A class used to process test data, match it with ideal functions, and save the results.
    """
    def __init__(self, host, user, password, database):
        super().__init__(host, user, password, database)
        self.engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

    def find_best_fit_functions(self, train_data, ideal_data):
        best_fit_funcs = {}
        for i in range(1, 5):
            min_error = float('inf')
            best_func = None
            for col in ideal_data.columns[1:]:
                error = np.sum((train_data[f'y{i}'] - ideal_data[col]) ** 2)
                if error < min_error:
                    min_error = error
                    best_func = col
            best_fit_funcs[f'y{i}'] = best_func
        return best_fit_funcs

    def process_test_data(self, test_csv_file_path, ideal_functions_table, result_table, best_fit_funcs):
        try:
            test_data = pd.read_csv(test_csv_file_path)
            ideal_data = pd.read_sql(f"SELECT * FROM {ideal_functions_table}", self.engine)

            for _, row in test_data.iterrows():
                x, y = row['x'], row['y']
                min_deviation = float('inf')
                chosen_function = None

                for func in best_fit_funcs.values():
                    ideal_y = ideal_data.loc[ideal_data['x'] == x, func].values[0]
                    deviation = abs(y - ideal_y)
                    if deviation < min_deviation:
                        min_deviation = deviation
                        chosen_function = func

                if chosen_function:
                    threshold = np.sqrt(2) * min_deviation
                    if min_deviation <= threshold:
                        result_query = f"INSERT INTO {result_table} (x, y, ideal_function, deviation) VALUES ({x}, {y}, '{chosen_function}', {min_deviation})"
                        self.cursor.execute(result_query)

            self.connection.commit()
            print("Test data processed and results saved successfully.")
        except FileNotFoundError as e:
            raise CSVImportError(f"CSV file not found: {e}")
        except mysql.connector.Error as err:
            raise CSVImportError(f"Error processing test data: {err}")
        except Exception as e:
            raise DataProcessingError(f"Unexpected error: {e}")

class DataVisualizer(DatabaseConnector):
    """
    A class used to visualize data from a MySQL database table, inheriting from DatabaseConnector.
    """
    def __init__(self, host, user, password, database):
        super().__init__(host, user, password, database)
        self.engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

    def visualize_data(self, train_table, test_table, result_table, best_fit_funcs):
        try:
            train_data = pd.read_sql(f"SELECT * FROM {train_table}", self.engine)
            test_data = pd.read_sql(f"SELECT * FROM {test_table}", self.engine)
            result_data = pd.read_sql(f"SELECT * FROM {result_table}", self.engine)

            output_file("data_visualization.html")
            p = figure(title="Data Visualization", x_axis_label='X', y_axis_label='Y')

            for i in range(1, 5):
                p.line(train_data['x'], train_data[f'y{i}'], legend_label=f"Train y{i}", line_width=2)

            for func in best_fit_funcs.values():
                p.line(train_data['x'], train_data[func], legend_label=f"Ideal {func}", line_width=2)

            p.circle(test_data['x'], test_data['y'], legend_label="Test Data", size=10, color='red', alpha=0.5)
            p.square(result_data['x'], result_data['y'], legend_label="Result Data", size=10, color='green', alpha=0.5)

            show(p)
        except SQLAlchemyError as e:
            raise DatabaseConnectionError(f"Database query failed: {e}")

def main():
    """
    The main function to execute the database operations and visualize data.
    """
    try:
        host = "localhost"
        user = "root"
        password = "none"
        database = "edrissa_jallow_database"

        # Create and connect to the database
        db_connector = DatabaseConnector(host, user, password, "")
        db_connector.connect()
        cursor = db_connector.cursor

        sql_queries = [
            "DROP DATABASE IF EXISTS edrissa_jallow_database",
            "CREATE DATABASE edrissa_jallow_database ",
            "CREATE TABLE edrissa_jallow_database.train (id INT AUTO_INCREMENT PRIMARY KEY, x FLOAT, y1 FLOAT, y2 FLOAT, y3 FLOAT, y4 FLOAT)",
            "CREATE TABLE edrissa_jallow_database.test (id INT AUTO_INCREMENT PRIMARY KEY, x FLOAT, y FLOAT)",
            "CREATE TABLE edrissa_jallow_database.best_fit_func (id INT AUTO_INCREMENT PRIMARY KEY, x INT(255), y INT(255))",
            "CREATE TABLE edrissa_jallow_database.mapping (id INT AUTO_INCREMENT PRIMARY KEY, x INT(255), y INT(255), ideal_function VARCHAR(255), deviation FLOAT)",
            "CREATE TABLE edrissa_jallow_database.ideal (id INT AUTO_INCREMENT PRIMARY KEY, x INT(255))",
            *[f"ALTER TABLE edrissa_jallow_database.ideal ADD COLUMN y{i+1} INT;" for i in range(0, 50)]
        ]

        for query in sql_queries:
            cursor.execute(query)

        db_connector.disconnect()

        # Import CSV data
        importer = CSVImporter(host, user, password, database)
        importer.connect()

        csv_file_path = r"path\laragon\www\python assignment LR\test.csv"
        train_csv_file_path = r"path\laragon\www\python assignment LR\train.csv"
        ideal_csv_file_path = r"path\laragon\www\python assignment LR\ideal.csv"

        table_name = "edrissa_jallow_database.test"
        train_table_name = "edrissa_jallow_database.train"
        ideal_table_name = "edrissa_jallow_database.ideal"
        result_table_name = "edrissa_jallow_database.mapping"

        importer.import_csv_to_db(csv_file_path, table_name)
        importer.import_csv_to_db(train_csv_file_path, train_table_name)
        importer.import_csv_to_db(ideal_csv_file_path, ideal_table_name)

        # Process test data and save results
        processor = DataProcessor(host, user, password, database)
        processor.connect()

        train_data = pd.read_sql(f"SELECT * FROM {train_table_name}", processor.engine)
        ideal_data = pd.read_sql(f"SELECT * FROM {ideal_table_name}", processor.engine)

        best_fit_funcs = processor.find_best_fit_functions(train_data, ideal_data)
        processor.process_test_data(csv_file_path, ideal_table_name, result_table_name, best_fit_funcs)
        processor.disconnect()

        # Visualize data
        visualizer = DataVisualizer(host, user, password, database)
        visualizer.connect()

if __name__ == "__main__":
    main()
