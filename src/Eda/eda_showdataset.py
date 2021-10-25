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
    st.header('Explore Your Dataset')
    st.markdown("Filter Your Result")
    form = st.form(key='my-form')
    features = list(df.columns)
    features_selected = form.multiselect('Select features ', features)
    
    count = form.slider('No of records to show', min_value=1, max_value=len(df), value=5, step=5)
    order = form.radio("Select order", options=["Show Top Rows", "Show Bottom Row"], help="Select do you wanna dsiplay rows from top or bottom")
    submit = form.form_submit_button('Show')
    
    df_show=df if len(features_selected)==0 else df.loc[:,features_selected]
    
    if order=="Show Top Rows":
        df_show=df_show.head(count)
    else:
        df_show=df_show.tail(count)
        
    
    st.write(df_show)
