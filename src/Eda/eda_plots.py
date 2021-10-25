import numpy as np
import pandas as pd
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pages.charts.load_graphs import LoadGraph
from pages.charts import graphs
from utils.data_helper import load_data

#import excelpage
# @st.cache

#from DataTransfer.src.resource import *

def app():
    html_temp3 = """<div style="background-color:#98AFC7;padding:10px">
            <h4 style="color:white;text-align:center;">Exploratory Data Analysis</h4>
            <h6 style="color:white;text-align:center;">As a Data scientist, data is our biggest asset. Using data we assist in the process of decision making which could benefit the business. But data always comes in huge quantities and looking at raw data becomes hard for even a veteran Data scientist to draw meaningful inferences let alone a nontechnical person. For this, we often resort to visualizing data by using various plots which can explain the data.</h6>
            </div><br></br>"""
    st.markdown(html_temp3, unsafe_allow_html=True)
    df=load_data()
    graph_type = st.sidebar.radio("Select Graph Type:", ("2D", "3D"))
    graph_val = []
    if graph_type == "2D":
        two_d_selected = st.sidebar.selectbox("Select Plot:", ("Bar Graph", "Histogram" ,"Scatter Plot", "Pie-Chart",   "Line Chart"))
        graph_val.append(two_d_selected)
    elif graph_type == "3D":
        three_d_selected = st.sidebar.selectbox("Select Plot:", ("Axes", "Scatter Chart", "Bubble Chart", "Surface Plot"))
        graph_val.append(three_d_selected)

    if graph_val[0] == "Scatter Plot":
        columns = df.columns
        
        col1, col2 = st.columns(2)
        feature_x = col1.selectbox('X', columns)
        
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y',columns)
        y_axis = list(df[feature_y])
        # plot the value
        fig = px.scatter(df,x=x_axis,y=y_axis)
    
    elif graph_val[0] == "Bar Graph":
        columns = df.columns
        col1, col2 = st.columns(2)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y', columns)
        y_axis = list(df[feature_y])
        # plot the value
        fig = px.bar(df, x=x_axis, y=y_axis)
        
    elif graph_val[0] == "Histogram":
        columns = df.columns
        col1, col2 = st.columns(2)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y', columns)
        y_axis = list(df[feature_y])
        bin = st.slider("Select the bin", 1, 50, 20)
        # plot the value
        fig = px.histogram(df, x=x_axis, y=y_axis, nbins=bin)
        
    
    elif graph_val[0] == "Pie-Chart":
        columns = df.columns
        feature_x = st.selectbox('X', columns)
        starting_row = st.slider("Select the starting row", 1, len(df))
        end_row = st.slider("Select the ending row", starting_row+1, len(df))
        x_axis = list(df[feature_x])
        fig = px.pie(df, values=x_axis[starting_row:end_row+1])
        # st.plotly_chart(fig)

    elif graph_val[0] == "Line Chart":
        columns = df.columns
        col1, col2 = st.columns(2)
        feature_x =  col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y', columns)
        y_axis = list(df[feature_y])
        fig = px.line(df, x=x_axis, y=y_axis)
        
    elif graph_val[0] == "Axes":
        columns = df.columns
        col1, col2,col3 = st.columns(3)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y',columns)
        y_axis = list(df[feature_y])
        feature_z = col3.selectbox('Z', columns)
        z_axis = list(df[feature_z])
        fig = go.Figure(data=[go.Mesh3d(x=x_axis, y=y_axis, z=z_axis, opacity=0.5, color='rgba(244,22,100,0.6)')])

    elif three_d_selected == "Scatter Chart":
        columns = df.columns
        col1, col2,col3 = st.columns(3)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y',columns)
        y_axis = list(df[feature_y])
        feature_z = col3.selectbox('Z', columns)
        z_axis = list(df[feature_z])
        fig = px.scatter_3d(df, x=x_axis, y=y_axis, z=z_axis)
        
        
    elif three_d_selected == "Bubble Chart":
        columns = df.columns
        col1, col2,col3 = st.columns(3)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y',columns)
        y_axis = list(df[feature_y])
        feature_z = col3.selectbox('Z', columns)
        z_axis = list(df[feature_z])
        feature_size = st.selectbox('Size', columns)
        size = list(df[feature_size])
        fig = px.scatter_3d(df, x=x_axis, y=y_axis, z=z_axis, size=size)
        
        # surface plot
    elif three_d_selected == "Surface Plot":
        columns = df.columns
        col1, col2,col3 = st.columns(3)
        feature_x = col1.selectbox('X', columns)
        x_axis = list(df[feature_x])
        feature_y = col2.selectbox('Y',columns)
        y_axis = list(df[feature_y])
        feature_z = col3.selectbox('Z', columns)
        z_axis = list(df[feature_z])
        
        numerical_columns = df.select_dtypes([np.number]).columns
        z_axis=df[numerical_columns].values
        sh_0, sh_1 = z_axis.shape
        x_axis, y_axis = np.linspace(0, 1, sh_0), np.linspace(0, 1, sh_1)
        fig = go.Figure(data=[go.Surface(z=z_axis, x=x_axis, y=y_axis)])
        fig.update_layout(autosize=False,
#                   scene_camera_eye=dict(x=1.87, y=0.88, z=-0.64),
                  width=500, height=500,
                  margin=dict(l=65, r=50, b=65, t=90)
)
       
        
    button = st.button("Plot")
    if button:

        st.plotly_chart(fig)
        