import pandas as pd
from connection_ms_sql import CreateDatabaseTable as cdt
from read_csv_save_data_ms_sql import ReadCsv as csv
from calculation import Calculations as cal
from ploting import Plot as plt

##Please have your Csv files and all of the project files with in the same forlder we are using Microsoft SQL Server 2022 


server = 'EDRISSA'  # e.g., 'localhost for my database server'
database_name = 'Assignment_python'  # Connect to the database to create  databases for assignments with consists of tables and columns
username = 'edrissa_jallow'  # SQL Server username, omit if using Windows authentication
password = 'none'  # SQL Server password, omit NoSql pasword required for database authentication
driver  = 'laragon  for SQL database Server' #driver used to connect with MS SQL laragon to create tables
port = 'none' #SQL Port
#Csv file train, test, and ideal Path
dataset_path = r'C:\Users\Edrissa\Documents\python practice\python assignment files" \\csv files'
#Names of Csv Files
file_names = ['train.csv','test.csv','ideal.csv']
# Dictionary in which key is table name to be created in SQL Server, then ('Coloumn Name, Data Type') of each Column
tabels_dic = table_name = "edrissa_jallow_database.test"
        train_table_name = "edrissa_jallow_database.train"
        ideal_table_name = "edrissa_jallow_database.ideal"
        result_table_name = "edrissa_jallow_database.mapping"
        }
#file Name to Table in SQL Server mappings
file_to_table_map = {
    'train.csv': 'train_table',
    'test.csv': 'test_table',
    'ideal.csv': 'ideal_table',
}
# Create an instance of Class CreateDatabaseTable
db_creator = cdt( server, 
                database_name, 
                username, 
                password, 
                driver, 
                port,
                tabels_dic)
# Create an instance of Class ReadCsv
# Paths to your CSV files
train_csv_file_path = r"c:\C:\Users\Edrissa\Documents\python practice\python assignment files\train.csv"
ideal_csv_file_path = r"c:\C:\Users\Edrissa\Documents\python practice\python assignment files\ideal.csv"
test_csv_file_path = r"c:\C:\Users\Edrissa\Documents\python practice\python assignment files\test.csv"

db_copy =    rcsv( server, 
                database_name, 
                username, 
                password, 
                driver, 
                port,
                dataset_path,
                file_names,
                tabels_dic,
                file_to_table_map)

# Create the new SQL Database with the name from database_name
db_creator.create_database()
# Create Tables in the SQL Server database
db_creator.create_tables()
# Copy the data from csv files to SQL Server
db_copy.read_csv_to_sql()

# Initialize the engine
db_copy.alchemy_connection()

# use db_conn.engine to perform database operations
engine = db_copy.engine

#Reading data from SQL Server into a pandas DataFrame
df_train = pd.read_sql_query("SELECT * FROM train_table", engine)
df_ideal = pd.read_sql_query("SELECT * FROM ideal_table", engine)
df_test = pd.read_sql_query("SELECT * FROM test_table", engine)

# Create an instance of Class Calculations
calculations = cal(df_train, df_ideal, df_test)

# Calculate SSD sums and find top four ideal functions
calculations.calculate_criteria1()

# Access the ssd_sums and top_four_ideal_functions directly from the instance
ssd_sums = calculations.get_ssd_sums()
top_four_ideal_functions = calculations.get_top_four_ideal_functions()

# Calculate Daviations
calculations.deviations()

#Calculate Final Results base on df_test
calculations.results()

#Access Test Resutls
test_results = calculations.get_test_results()

# Create a new DataFrame from the final results
df_test_results = pd.DataFrame(test_results)
df_test_results = df_test_results.sort_values(by='X (test func)')

# use db_conn.engine (initialized above) to perform database operations 
engine = db_copy.engine
table_name = 'test_results'
        
# Save the DataFrame to the SQL table
df_test_results.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
print(f'Data Copied to {table_name} in SQL')

# Create an instance of Class Plot
ssd = plt(ssd_sums,df_test_results)

#Plot the complete DashBoard
ssd.dashboard()
#ssd.ssd_plot_only()
#ssd.scatter_plot_only()
print(df_test_results)

