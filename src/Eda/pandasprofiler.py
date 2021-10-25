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
    pr = ProfileReport(df, explorative=True, minimal=True,correlations={"cramers": {"calculate": False}})
    st.write('---')
    st.header('*Exploratory Data Analysis Report*')
    st_profile_report(pr)
