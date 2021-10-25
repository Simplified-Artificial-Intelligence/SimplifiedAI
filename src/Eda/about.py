import numpy as np
import pandas as pd
import os
import streamlit as st
#import excelpage
# @st.cache

#from DataTransfer.src.resource import *


def app():
    html_temp3 = """<div style="background-color:#98AFC7;padding:10px">
            <h4 style="color:white;text-align:center;">Exploratory Data Analysis</h4>
            <h6 style="color:white;text-align:center;">Exploratory Data Analysis refers to the critical process of
            performing initial investigations on data so as to discover patterns,to spot anomalies,
            to test hypothesis and to check assumptions with the help of summary statistics and graphical
            representations.</h6>
            </div><br></br>"""
    st.markdown(html_temp3, unsafe_allow_html=True)
