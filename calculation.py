import pandas as pd
import numpy as np

class Calculations:
    """
    A class to perform calculations comparing training functions to ideal functions, including SSD calculation, 
    identifying top ideal functions, calculating deviations, and determining the best matches for test functions.

    Attributes:
        df_train (pd.DataFrame): DataFrame containing training function data sorted by 'X'.
        df_ideal (pd.DataFrame): DataFrame containing ideal function data sorted by 'X'.
        df_test (pd.DataFrame): DataFrame containing test function data.
    
    Methods:
        calculate_criteria1(): Calculates the SSD for each training function against all ideal functions and identifies the top ideal function for each training function.
        
        get_ssd_sums(): Returns the dictionary containing SSD sums for each training function comparison with ideal functions.
        
        get_top_four_ideal_functions(): Returns the list of top four ideal functions with the lowest SSD for each training function.
        
        deviations(): Calculates maximum deviations for each ideal function against training functions and adjusts them by a factor of sqrt(2).
        
        get_adjusted_deviation(): Returns the dictionary containing adjusted maximum deviations for each ideal function.
        
        results(): Determines the best match for each test function based on the deviations and the selected top ideal functions. Stores the results in `test_results`.
        
        get_test_results(): Returns the list of dictionaries containing test results with best matches.
    """
    def __init__(self, df_train, df_ideal, df_test):
        
        """
        Initializes the Calculations class with training, ideal, and test data.
        """
        self.df_train = df_train.sort_values(by='X')
        self.df_ideal = df_ideal.sort_values(by='X')
        self.df_test = df_test
        self.ssd_sums = {}
        self.top_four_ideal_functions = []
        self.adjusted_deviations = {}
        self.test_results = []

    def calculate_criteria1(self):
        """
        Calculates the sum of squared differences (SSD) between each training function and all ideal functions.
        Identifies the top ideal function with the lowest SSD for each training function.
        """
        for j in range(1, 5):  # Assuming df_train has columns like 'Y1', 'Y2', 'Y3', 'Y4' for training functions
            ssd_sums1 = {}
            for i in range(1, 51):  # Assuming 50 ideal functions
                col_name = f'Y{i} (ideal func)'
                ssd = ((self.df_train.iloc[:, j] - self.df_ideal[col_name])**2).sum()
                ssd_sums1[col_name] = ssd
            self.ssd_sums[f'Y{j} (training func)'] = ssd_sums1
            # Sort and find the ideal function with the lowest SSD
            self.top_four_ideal_functions.append(sorted(ssd_sums1, key=ssd_sums1.get)[0])
        print("Top ideal function for each training function:", self.top_four_ideal_functions)

    def get_ssd_sums(self):
        """
        Returns the dictionary of SSD sums for each training function.
        """
        return self.ssd_sums

    def get_top_four_ideal_functions(self):
        """
        Returns the list of top four ideal functions based on SSD sums.
        """
        return self.top_four_ideal_functions
    
    def deviations(self):
        """
        Calculates maximum deviations for each ideal function across all training functions and adjusts them
        by a factor of sqrt(2).
        """
        top_four_ideal_functions = self.top_four_ideal_functions
        # Assuming the training function columns are named 'Y1 (training func)', 'Y2 (training func)', etc.
        training_function_columns = ['Y1 (training func)', 'Y2 (training func)', 'Y3 (training func)', 'Y4 (training func)']

        max_deviations = {}
        for ideal_func in top_four_ideal_functions:
            all_deviations = []
            for train_func in training_function_columns:
                # Here, we calculate deviations for each training function against the current ideal function
                deviations = np.abs(self.df_train[train_func] - self.df_ideal[ideal_func])
                all_deviations.append(deviations)
            
            # Combine deviations from all training functions for the current ideal function
            combined_deviations = np.concatenate(all_deviations)
            max_deviations[ideal_func] = np.max(combined_deviations)

        # Adjust max deviations by factor sqrt(2)
        adjustment_factor = np.sqrt(2)
        self.adjusted_deviations = {func: deviation * adjustment_factor for func, deviation in max_deviations.items()}

    def get_adjusted_deviation(self):
        """
        Returns the dictionary of adjusted deviations for each ideal function.
        """
        return self.adjusted_deviations
    
    def results(self):
        """
        Finds the best match for each test function based on deviations and stores the results.
        """
        def find_best_match(x_val, y_val, chosen_functions, df_ideal, adjusted_deviations):
            best_match = {'func': None, 'deviation': np.inf}
            
            for func in chosen_functions:
                ideal_y_val = df_ideal.loc[df_ideal['X'] == x_val, func].iloc[0]
                deviation = np.abs(ideal_y_val - y_val)
                
                if deviation < adjusted_deviations[func] and deviation < best_match['deviation']:
                    best_match = {'func': func, 'deviation': deviation}
            
            return best_match

        for index, row in self.df_test.iterrows():
            match = find_best_match(row['X (test func)'], row['Y (test func)'], self.top_four_ideal_functions, self.df_ideal, self.adjusted_deviations)
            self.test_results.append({
                'X (test func)': row['X (test func)'],
                'Y (test func)': row['Y (test func)'],
                'Delta Y (test func)': match['deviation'] if match['func'] else None,
                'No. of ideal func': match['func']
                
            })
            
    def get_test_results(self):
        """
        Returns the list of test results containing the best matches for the test functions.
        """
        return self.test_results


