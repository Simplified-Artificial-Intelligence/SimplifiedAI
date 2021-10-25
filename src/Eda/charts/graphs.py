"""
This file is the framework for creating different graphs
through an object oriented framework.
"""

# Import necessary libraries
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def histogram(df, x, y=None, z=None) -> None:
    fig = px.histogram(df, x=x, y=y)
    st.plotly_chart(fig)

def bar(df, x, y=None, z=None) -> None:
    fig = px.bar(df, x=x, y=y)
    st.plotly_chart(fig)

def scatter(df, x, y=None, z=None) -> None:
    fig = px.scatter(df, x=x, y=y)
    st.plotly_chart(fig)

def pie(df, x, y=None, z=None) -> None:
    starting_row = st.slider("Select the starting row", 1, len(df))
    end_row = st.slider("Select the ending row", starting_row+1, len(df))
    fig = px.pie(df, values=x[starting_row:end_row+1], names=y, title='')
    st.plotly_chart(fig)


def axes3d(df, x, y=None, z=None) -> None:
    np.random.seed(1)
    N = 70

    fig = go.Figure(data=[go.Mesh3d(x=(70*np.random.randn(N)),
                   y=(55*np.random.randn(N)),
                   z=(40*np.random.randn(N)),
                   opacity=0.5,
                   color='rgba(244,22,100,0.6)'
                  )])

    fig.update_layout(
        scene = dict(
            xaxis = dict(nticks=4, range=[-100,100],),
                     yaxis = dict(nticks=4, range=[-50,100],),
                     zaxis = dict(nticks=4, range=[-100,100],),),
        width=700,
        margin=dict(r=20, l=10, b=10, t=10))

    st.plotly_chart(fig)
    
