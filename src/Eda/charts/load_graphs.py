"""
This file is the framework for generating multiple Streamlit applications
through an object oriented framework.
"""

# Import necessary libraries
import streamlit as st


# Define the multipage class to manage the multiple apps in our program
class LoadGraph:
    """Framework for combining multiple streamlit applications."""

    def __init__(self, title) -> None:
        self.graphs = []
        self.title = title

    def add_graph(self, title, func) -> None:
        self.graphs.append({
            "title": title,
            "function": func
        })

    def select(self):
        # Drodown to select the graph to run
        self.graph = st.sidebar.selectbox(
            self.title,
            self.graphs,
            format_func=lambda graphObj: graphObj['title']
        )
        return self.graph['title']

    def plot(self, df, x=None, y=None, z=None):
        # run the app function
        self.graph['function'](df, x=x, y=y, z=z)
