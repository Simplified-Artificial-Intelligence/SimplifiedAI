import pandas as pd
import numpy as np

"""[summary]
Class for EDA Operations
Returns:
    [type]: [description]
"""
class EDA:
    @staticmethod
    def five_point_summary(dataframe):
        """[summary]
        Return 5 Point Summary For Given  Dataset
        Args:
            dataframe ([type]): [description]

        Returns:
            [type]: DataFrame/ Exception
        """
        my_dict = {'Features': [], 'Min': [], 'Q1': [], 'Median': [], 'Q3': [],
                    'Max': []}
        for column in dataframe.select_dtypes(include=np.number).columns:
            try:
                column_data=dataframe[pd.to_numeric(dataframe[column], errors='coerce').notnull()][column]
                q1 = np.percentile(column_data, 25)
                q3 = np.percentile(column_data, 75)
                
                my_dict['Features'].append(column)
                my_dict['Min'].append(np.min(column_data))
                my_dict['Q1'].append(q1)
                my_dict['Median'].append(np.median(column_data))
                my_dict['Q3'].append(q3)
                my_dict['Max'].append(np.max(column_data))

            except Exception as e:
                print(e)

        return pd.DataFrame(my_dict).sort_values(by=['Features'], ascending=True)
    
    @staticmethod
    def correlation_report(dataframe,method='pearson'):
        try:
            return dataframe.corr(method=method)
        except Exception as e:
                print(e)
    
    @staticmethod
    def get_no_records(dataframe,count=100,order='top'):
        try:
            if order=='top':
                return dataframe.head(count)
            else:
                return dataframe.tail(count)
        except Exception as e:
                print(e)