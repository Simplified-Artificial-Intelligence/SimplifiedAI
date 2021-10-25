from logging import PlaceHolder
from os import write
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pandas.io.pytables import Table
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
from streamlit.script_request_queue import RerunData
from streamlit.script_runner import RerunException
# from utils.data_helper import load_data

class EDA_missingvalue():

    """This class returns table of dataset and this table shows
    missing values,percentage of missing values, mean, median,
    mode with respective to each column available in dataset.
    and also graphical presentation of missing values. """

    data_types = ['bool', "int_", "int8", "int16", "int32", "int64", "uint8", "uint16",
                 "uint32", "uint64", "float_","float16", "float32", "float64" ]
                  #, "pandas.core.frame.DataFrame", "pandas.core.series.Series"]

    @st.cache()
    def __init__(self):
        print("Loading DataFrame")

    @st.cache
    def get_data(self, data):
        data = "src/streamlit/data/train.csv"
        df = pd.read_csv(data)
        return df


    st.cache(allow_output_mutation=True)
    def find_dtypes(self, df3):
        l = []
        for i in df3.columns:
            yield str(df3[i].dtypes)

    @st.cache(allow_output_mutation=True)
    def find_mode(self, df3):
        l = []
        for i in df3.columns:
            yield str(df3[i].mode()[0])

    @st.cache(allow_output_mutation=True)
    def find_mean(self, df3):
        for i in df3.columns:
            if df3[i].dtypes in self.data_types:
                yield str(round(df3[i].mean(), 2))
            else:
                yield str('-')

    @st.cache(allow_output_mutation=True)
    def find_median(self, df3):
        for i in df3.columns:
            if df3[i].dtypes in self.data_types:
                yield str(round(df3[i].median(), 2))
            else:
                yield str('-')

    @st.cache(suppress_st_warning=True)
    def missing_cells_table(self, df):
        df = df[[col for col in df.columns if df[col].isnull().any()]]

        missing_value_df = pd.DataFrame({'Missing values': df.isnull().sum(),
                                         'Missing values (%)': (df.isnull().sum()/ len(df)) * 100,
                                         'Mean': self.find_mean(df),
                                         'Median': self.find_median(df),
                                         'Mode': self.find_mode(df),
                                         'Datatype': self.find_dtypes(df)
                                         })
        return missing_value_df

    
    @st.cache
    def plot_barchart(self,ss,options):
        fg = pd.DataFrame(ss[options].astype('object'))
        fig1 = px.bar(x=fg.columns, y=fg.isnull().sum(),color=fg.columns)
        fig1.update_layout(
            title="Visualize Missing Cells",
            xaxis_title="Columns with Missing Values",
            yaxis_title="Missing Values Count",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        return fig1

    @st.cache
    def plot_piechart(self,df1):
        px.pie()
        values = round((df1.isnull().sum()/ len(df1)) * 100, 2)
        # df1 = ss[[col for col in ss.columns if ss[col].isnull().any()]]
        fig = px.pie(df1, values=values, names=df1.columns, labels=df1.columns, title="Missing Values")
        fig.update_traces(textposition='inside', textinfo='label+percent', insidetextorientation='radial')
        # fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
        fig.update_layout(uniformtext_minsize=12)
        fig.update_layout(
            title="Visualize Missing Cells",
            xaxis_title="Columns with Missing Cells",
            yaxis_title="Missing Values Count",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        return fig

def app():
    data = EDA_missingvalue()
    df = data.get_data(data)


    st.subheader("Missing Values Analysis")
    activities1 = ["Tabular Report", "Bar Chart", "Pie Chart"]
    sub_choice = st.sidebar.radio("Choose an option", activities1)
    ss = df[[col for col in df.columns if df[col].isnull().any()]]

    if sub_choice=="Tabular Report":

        ss = df[[col for col in df.columns if df[col].isnull().any()]]
        st.write("Total Missing Values", df.isnull().sum().sum())
        st.write("Total Missing Values (%)", round(df.isnull().sum() / df.index.size, 2).sum())
        st.write(data.missing_cells_table(df))

    elif sub_choice == "Pie Chart":

        options=list(ss.columns)
        options.insert(0, 'ALL')
        options = st.multiselect(label='Select Columns to Visualize', options=options)

        if st.button('Show') :
            if 'ALL' in options:
                st.plotly_chart(data.plot_piechart(ss))
            else:
                st.plotly_chart(data.plot_piechart(ss[options]))

    elif sub_choice == "Bar Chart" :
        
        options=list(ss.columns)
        options.insert(0, 'ALL')
        options = st.multiselect(label='Select Columns to Visualize', options=options)

        if options :
            if st.button('Show') :
                if 'ALL' in options:
                    st.plotly_chart(data.plot_barchart(ss, ss.columns))
                else:
                    st.plotly_chart(data.plot_barchart(ss,options))

    else:
        st.error("Something has gone terribly wrong.")
                    