
import streamlit as st
import numpy as np


def radio_callback(df, col_type):

    columns = df.columns

    # numerical_columns = df._get_numeric_data().columns
    numerical_columns = df.select_dtypes([np.number]).columns
    categorical_columns = list(set(columns) - set(numerical_columns))

    col1, col2 = st.columns(2)

    with col1:
        feature_x = st.selectbox('x', columns)
        x_axis = list(df[feature_x])

    with col2:
        if col_type == 'Numerical':
            feature_y = st.selectbox('y', numerical_columns)
        elif col_type == 'Categorical':
            feature_y = st.selectbox('y', categorical_columns)
        y_axis = list(df[feature_y])

    return x_axis, y_axis
