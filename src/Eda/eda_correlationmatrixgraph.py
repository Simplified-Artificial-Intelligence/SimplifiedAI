import pandas as pd
import streamlit as st
# import sqlite3
# from sqlite3 import Connection
# from . import excelpage,dashboard
# from .resource import *
# from multipage import MultiPage
import numpy as np
import pandas as pd
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from utils.data_helper import load_data as cassandra_load_data
#import excelpage
# @st.cache

#from DataTransfer.src.resource import *


def app():
    st.title("Correlation Operation")

    @st.cache
    def load_data():
        data =cassandra_load_data()
        return data, data.columns

    def generate_matrix_graph(chosen_method, graph_matrix,data):
        st.write(chosen_method.capitalize() + " Correlation Matrix")
        if graph_matrix == 'Matrix':
            try:
                st.write(data.corr(method=chosen_method))
            except Exception as e:
                pass
        else:
            fig = px.imshow(data.corr( method=chosen_method))
            st.plotly_chart(fig)

    def generate_label_correlation(chosen_method, data, label):
        st.subheader(chosen_method.capitalize() + " Correlation Matrix wrt Target " + label + " method- " + chosen_method)
        st.write(data.corr(method=chosen_method)[label])

        st.subheader("\n\nCorrelation Graph - " + chosen_method + " Method")
        write = data.corr(method=chosen_method)[[label]].sort_values(by=label, ascending=False)
        fig = px.imshow(write)
        st.plotly_chart(fig)

    def description():
        expander = st.expander("Pearson")
        expander.write(""" The Pearson's correlation coefficient (r) is a measure of 
      linear correlation between two variables. It's value lies between
      -1 and +1, -1 indicating total negative linear correlation, 0 indicating 
       no linear correlation and 1 indicating total positive linear correlation.
       Furthermore, r is invariant under separate changes in location and scale 
       of the two variables, implying that for a linear function the angle to the
       x-axis does not affect r.To calculate r for two variables X and Y, one divides
       the covariance of X and Y by the product of their standard deviations.""")
        expander = st.expander("Spearman")
        expander.write(""" The Spearman's rank correlation coefficient (ρ) 
      is a measure of monotonic correlation between two variables, 
      and is therefore better in catching nonlinear monotonic correlations 
      than Pearson's r. It's value lies between -1 and +1, -1 indicating 
      total negative monotonic correlation, 0 indicating no monotonic 
      correlation and 1 indicating total positive monotonic correlation.
      To calculate ρ for two variables X and Y, one divides the covariance
      of the rank variables of X and Y by the product of their standard deviations.""")
        expander = st.expander("Kendell")
        expander.write(""" Similarly to Spearman's rank correlation coefficient,
      the Kendall rank correlation coefficient (τ) measures ordinal
      association between two variables. It's value lies between
      -1 and +1, -1 indicating total negative correlation,
      0 indicating no correlation and 1 indicating total
      positive correlation.To calculate τ for two variables
      X and Y, one determines the number of concordant and
      discordant pairs of observations. τ is given by the
      number of concordant pairs minus the discordant pairs
      divided by the total number of pairs""")


    # user_choice = st.sidebar.radio("Choose",("View Correlation for all Columns", "View Correlation of any two column","View Correlation w.r.t Target column"))

    user_choice = st.sidebar.radio("Choose",("View Correlation for all Columns","View Correlation w.r.t Target column"))

    if user_choice =="View Correlation for all Columns":
        chosen_method = st.sidebar.selectbox('Select the method: ',('pearson', 'spearman', 'kendall'))
        graph_matrix_choice = st.selectbox("", ('Graph', 'Matrix'))
        generate_matrix_graph(chosen_method,graph_matrix_choice,load_data()[0])
        st.header("Check Description")
        description()
    # elif user_choice == "View Correlation of any two column":
    #     columnlist = load_data()[0].columns
    #     column1 = st.sidebar.selectbox("Select the column for x axis",tuple(columnlist))
    #     if column1:
    #         column2 = st.sidebar.selectbox("Select the column for y axis",tuple(columnlist))
    #         if column1!=column2:
    #             if column2:
    #                 choice_method = st.sidebar.selectbox('Select the method: ',('pearson', 'spearman', 'kendall'))
    #                 if user_choice:
    #                     try:
    #                         desired_data  = load_data()[0].loc[:,[column1,column2]]
    #                         generate_matrix_graph(choice_method,'Graph',desired_data)
    #                         generate_matrix_graph(choice_method, 'Matrix', desired_data)
    #                         st.header("Check Description")
    #                         description()
    #                     except:
    #                         pass
    #                 else:
    #                     st.write("Select columns for  axes")
    #                     st.header("Check Description")
    #                     description()

    else:
        data_type = load_data()[0].dtypes

        select_label = st.sidebar.selectbox('select your label col',
            ([i for i in load_data()[0].columns if data_type[i] == 'float64' or data_type[i] == 'int64']))
        if select_label:
            chosen_method = st.sidebar.selectbox('choose correlation type',('pearson', 'spearman','kendall'))
            if chosen_method:
                generate_label_correlation(chosen_method, load_data()[0], select_label)
                description()
