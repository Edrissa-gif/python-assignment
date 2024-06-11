from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import gridplot
import numpy as np
from bokeh.layouts import column, row

class Plot:
        """
        A class to create visualizations for SSD sums and test results using Bokeh.
        
        Attributes:
            ssd_sums (dict): A dictionary containing the sums of squared differences (SSD) for each training function against ideal functions.
            test_results (DataFrame): A pandas DataFrame containing test results with columns for 'X (test func)', 'Y (test func)', 'Delta Y (test func)', and 'No. of ideal func'.
        
        Methods:
            ssd_plot(ssd_sums, title): Creates a bar plot for SSD values with the minimum SSD highlighted.
            scatter_test_results(df_test_results): Generates a scatter plot for test results, showing ideal function number and Delta Y on hover.
            dashboard(): Creates a comprehensive layout with SSD bar plots and a scatter plot of test results, then saves and displays it.
            ssd_plot_only(): Displays only the SSD bar plots for each training function in a layout.
            scatter_plot_only(): Displays only the scatter plot of test results in a layout.
        """
    
        def __init__(self, ssd_sums, test_results):
            """
            Initializes the Plot class with SSD sums and test results data.
            """
            self.ssd_sums = ssd_sums
            self.test_results = test_results
        
        def ssd_plot(self,ssd_sums, title):
            """
            Creates a bar plot of the SSD values for each ideal function, highlighting the function with the minimum SSD.

            Parameters:
                ssd_sums (dict): SSD sums for a specific training function.
                title (str): The title for the plot.

            Returns:
                Bokeh figure: A bar plot visualizing the SSD values.
            """, 
            # Calculate log10 of SSD values
            ssd_log = np.log10(list(ssd_sums.values()))
            
            # Find the minimum SSD value and its corresponding ideal function
            min_ssd_value = min(ssd_log)
            colors = ['green' if ssd == min_ssd_value else 'lightblue' for ssd in ssd_log]
            
            # Create a ColumnDataSource, now including a color field
            ssd_source_log = ColumnDataSource(data=dict(
                ideal_funcs=list(ssd_sums.keys()),
                ssd=ssd_log,
                colors=colors  # Add color information here
            ))
            
            # Create the figure
            p = figure(x_range=list(ssd_sums.keys()), title=title, width=700, height=350, tools="pan,wheel_zoom,box_zoom,reset,save")
            
            # Draw the bars, setting fill_color to use the colors from the source
            p.vbar(x='ideal_funcs', top='ssd', width=0.9, source=ssd_source_log, line_color='white', fill_color='colors')
            
            # Configure hover tool
            hover = HoverTool()
            hover.tooltips = [
                ("Ideal Function", "@ideal_funcs"),
                ("Log10(SSD)", "@ssd{0,0.00}")
            ]
            p.add_tools(hover)
            
            # Rotate x-axis labels for better visibility
            p.xaxis.major_label_orientation = "vertical"
            
            return p

    
        def scatter_test_results(self, df_test_results):

            """
            Creates a scatter plot of test results, showing the relationship between 'X (test func)' and 'Y (test func)' and displaying the ideal function number and Delta Y on hover.

            Parameters:
                df_test_results (DataFrame): A DataFrame containing test results.

            Returns:
                Bokeh figure: A scatter plot visualizing the test results.
            """

            # Generate a random color for each data point
            np.random.seed(42)  # For reproducibility
            colors = ['#' + ''.join([np.random.choice(list('0123456789ABCDEF')) for j in range(6)]) for i in range(len(df_test_results))]

            # Prepare the data
            source = ColumnDataSource(data={
                'x_test': df_test_results['X (test func)'].astype(float),
                'y_test': df_test_results['Y (test func)'].astype(float),
                'ideal_func': df_test_results['No. of ideal func'],
                'delta_y': df_test_results['Delta Y (test func)'],
                'colors': colors  # Add the generated colors to the source
            })

            # Create the figure
            p = figure(width=1400, height=600, title="Test Results Scatter Plot",
                    x_axis_label='X (test func)', y_axis_label='Y (test func)',
                    tools="pan,wheel_zoom,box_zoom,reset,save")

            # Add a scatter renderer with dynamic coloring
            p.scatter('x_test', 'y_test', color='colors', source=source, size=20, alpha=0.6)

            # Add a hover tool
            hover = HoverTool()
            hover.tooltips = [
                ("X (test func)", "@x_test"),
                ("Y (test func)", "@y_test"),
                ("No. of ideal func", "@ideal_func"),
                ("Delta Y", "@delta_y")
            ]

            p.add_tools(hover)

            # Show the result
            # Return the plot object
            return p
    
        def dashboard(self):
            """
            Combines SSD bar plots for each training function and a scatter plot of test results into a single dashboard layout and saves/shows it as an HTML file.
            """
            df_test_results = self.test_results
            ssd_sums= self.ssd_sums
            
            ssd_sums_y1 = ssd_sums['Y1 (training func)']
            ssd_sums_y2 = ssd_sums['Y2 (training func)']
            ssd_sums_y3 = ssd_sums['Y3 (training func)']
            ssd_sums_y4 = ssd_sums['Y4 (training func)']

            # Example usage: Print the ideal function with the lowest SSD for Y1 (training func)
            lowest_ssd_y1 = min(ssd_sums_y1, key=ssd_sums_y1.get)
            lowest_ssd_y2 = min(ssd_sums_y2, key=ssd_sums_y2.get)
            lowest_ssd_y3 = min(ssd_sums_y3, key=ssd_sums_y3.get)
            lowest_ssd_y4 = min(ssd_sums_y4, key=ssd_sums_y4.get)
            # Create a plot for each set of SSD sums
            p1 = self.ssd_plot(ssd_sums['Y1 (training func)'], f'SSD for Y1 (training func)-Log Sclae & The Function selected is {lowest_ssd_y1} @Value {ssd_sums_y1[lowest_ssd_y1]}')
            p2 = self.ssd_plot(ssd_sums['Y2 (training func)'], f'SSD for Y2 (training func)-Log Sclae & The Function selected is {lowest_ssd_y2} @Value {ssd_sums_y2[lowest_ssd_y2]}')
            p3 = self.ssd_plot(ssd_sums['Y3 (training func)'], f'SSD for Y3 (training func)-Log Sclae & The Function selected is {lowest_ssd_y3} @Value {ssd_sums_y3[lowest_ssd_y3]}')
            p4 = self.ssd_plot(ssd_sums['Y4 (training func)'], f'SSD for Y4 (training func)-Log Sclae & The Function selected is {lowest_ssd_y4} @Value {ssd_sums_y4[lowest_ssd_y4]}')
            p5 = self.scatter_test_results(df_test_results)

           # Combine p1 and p2 in one row, and p3 and p4 in another row
            top_row = row(p1, p2)
            middle_row = row(p3, p4)

            # Stack the two rows and the scatter plot vertically
            layout = column(top_row, middle_row, p5)
            
            # Specify the output file path
            output_file("dahboard.html")

            # Save the layout
            save(layout)

            # Show the layout
            show(layout)
        
        def ssd_plot_only(self):
            """
            Creates and shows a layout consisting only of SSD bar plots for each training function.
            """
            ssd_sums= self.ssd_sums
            
            ssd_sums_y1 = ssd_sums['Y1 (training func)']
            ssd_sums_y2 = ssd_sums['Y2 (training func)']
            ssd_sums_y3 = ssd_sums['Y3 (training func)']
            ssd_sums_y4 = ssd_sums['Y4 (training func)']

            # Example usage: Print the ideal function with the lowest SSD for Y1 (training func)
            lowest_ssd_y1 = min(ssd_sums_y1, key=ssd_sums_y1.get)
            lowest_ssd_y2 = min(ssd_sums_y2, key=ssd_sums_y2.get)
            lowest_ssd_y3 = min(ssd_sums_y3, key=ssd_sums_y3.get)
            lowest_ssd_y4 = min(ssd_sums_y4, key=ssd_sums_y4.get)
            # Create a plot for each set of SSD sums
            p1 = self.ssd_plot(ssd_sums['Y1 (training func)'], f'SSD for Y1 (training func)-Log Sclae & The Function selected is {lowest_ssd_y1} @Value {ssd_sums_y1[lowest_ssd_y1]}')
            p2 = self.ssd_plot(ssd_sums['Y2 (training func)'], f'SSD for Y1 (training func)-Log Sclae & The Function selected is {lowest_ssd_y2} @Value {ssd_sums_y2[lowest_ssd_y2]}')
            p3 = self.ssd_plot(ssd_sums['Y3 (training func)'], f'SSD for Y1 (training func)-Log Sclae & The Function selected is {lowest_ssd_y3} @Value {ssd_sums_y2[lowest_ssd_y3]}')
            p4 = self.ssd_plot(ssd_sums['Y4 (training func)'], f'SSD for Y1 (training func)-Log Sclae & The Function selected is {lowest_ssd_y4} @Value {ssd_sums_y2[lowest_ssd_y4]}')
            

           # Combine p1 and p2 in one row, and p3 and p4 in another row
            top_row = row(p1, p2)
            middle_row = row(p3, p4)

            # Stack the two rows and the scatter plot vertically
            layout = column(top_row, middle_row)

            # Show the layout
            show(layout)
            
        def scatter_plot_only(self):
            """
            Creates and shows a layout consisting only of the scatter plot of test results.
            """
            df_test_results = self.test_results
            
            
            p5 = self.scatter_test_results(df_test_results)

            # Stack the two rows and the scatter plot vertically
            layout = column(p5)

            # Show the layout
            show(layout)
    
    
