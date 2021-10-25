import numpy as np
import pandas as pd
import os
import streamlit as st
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
from utils.data_helper import load_data
#import excelpage
# @st.cache

#from DataTransfer.src.resource import *
  
def app():
    df=load_data()
    
    outlier_temp = """<div style="background-color:#98AFC7;padding:10px"><h4 style="color:white;text-align:center;">5 Points Summary</h4>
                <h6 style="color:white;text-align:center;">A summary consists of five values: the most extreme values
                in the data set (the maximum and minimum values), the lower and upper quartiles, and the median.
                These values are presented together and ordered from lowest to highest: minimum value,
                lower quartile (Q1), median value (Q2), upper quartile (Q3), maximum value.</h6></div><br></br>"""
    st.markdown(outlier_temp, unsafe_allow_html=True)
    
    def five_point_summary(dataframe):
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
    
    
    features = list(df.select_dtypes(include=np.number).columns)
    form3 = st.form(key='form')
    
    features_selected = st.multiselect('Select features ', features)
    
    
    if len(features_selected)>0:
        daf=df.loc[:,features_selected]
        
    df_show=five_point_summary(df if len(features_selected)==0 else df.loc[:,features_selected])
    st.write(df_show)
