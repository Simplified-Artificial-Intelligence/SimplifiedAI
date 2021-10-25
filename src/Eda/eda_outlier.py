import pandas as pd
import streamlit as st
# import sqlite3
# from sqlite3 import Connection
# from . import excelpage,dashboard
# from .resource import *
# from multipage import MultiPage
from math import floor
import numpy as np
import pandas as pd
from utils.data_helper import load_data
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import plotly.figure_factory as ff

#import excelpage
# @st.cache

#from DataTransfer.src.resource import *

def app():
    df = load_data()

    outlier_temp = """<div style="background-color:#98AFC7;padding:10px"><h4 style="color:white;text-align:center;">Outlier</h4>
                <h6 style="color:white;text-align:center;">In statistics, an outlier is a data point that differs significantly from other observations. 
                An outlier may be due to variability in the measurement or it may indicate experimental error; the latter are sometimes excluded from the data set. 
                An outlier can cause serious problems in statistical analyses.</h6></div><br></br>"""
    st.markdown(outlier_temp, unsafe_allow_html=True)

    def outlier_detection_iqr(dataframe):
        my_dict = {'Features': [], 'IQR': [], 'Q3 + 1.5*IQR': [], 'Q1 - 1.5*IQR': [], 'Upper outlier count': [],
                   'Lower outlier count': [], 'Total outliers': [], 'Outlier percent': []}
        for column in dataframe.select_dtypes(include=np.number).columns:
            try:
                upper_count = 0
                lower_count = 0
                q1 = np.percentile(dataframe[column].fillna(dataframe[column].mean()), 25)
                q3 = np.percentile(dataframe[column].fillna(dataframe[column].mean()), 75)
                IQR = round(q3 - q1)
                upper_limit = floor(q3 + (IQR * 1.5))
                lower_limit = round(q1 - (IQR * 1.5))

                for element in dataframe[column].fillna(dataframe[column].mean()):
                    if element > upper_limit:
                        upper_count += 1
                    elif element < lower_limit:
                        lower_count += 1

                my_dict['Features'].append(column)
                my_dict['IQR'].append(IQR)
                my_dict['Q3 + 1.5*IQR'].append(upper_limit)
                my_dict['Q1 - 1.5*IQR'].append(lower_limit)
                my_dict['Upper outlier count'].append(upper_count)
                my_dict['Lower outlier count'].append(lower_count)
                my_dict['Total outliers'].append(upper_count + lower_count)
                my_dict['Outlier percent'].append(round((upper_count + lower_count) / len(dataframe[column]) * 100, 2))

            except Exception as e:
                print(e)

        return pd.DataFrame(my_dict).sort_values(by=['Total outliers'], ascending=False)

    def z_score_outlier_detection(dataframe):
        my_dict = {"Features": [], "Mean": [], "Standard deviation": [], 'Upper outlier count': [],
                   'Lower outlier count': [], 'Total outliers': [], 'Outlier percent': []}

        for column in dataframe.select_dtypes(include=np.number).columns:
            try:
                upper_outlier = 0
                lower_outlier = 0
                col_mean = np.mean(dataframe[column].fillna(dataframe[column].mean()))
                col_std = np.std(dataframe[column].fillna(dataframe[column].mean()))

                for element in dataframe[column].fillna(dataframe[column].mean()):
                    z = (element - col_mean) / col_std
                    if z > 3:
                        upper_outlier += 1
                        continue
                    elif z < -3:
                        lower_outlier += 1

                my_dict["Features"].append(column)
                my_dict["Mean"].append(col_mean)
                my_dict["Standard deviation"].append(col_std)
                my_dict["Upper outlier count"].append(upper_outlier)
                my_dict["Lower outlier count"].append(lower_outlier)
                my_dict["Total outliers"].append(upper_outlier + lower_outlier)
                my_dict["Outlier percent"].append(round((upper_outlier + lower_outlier) / len(dataframe[column]) * 100, 2))

            except Exception as e:
                print(e)
        return pd.DataFrame(my_dict).sort_values(by=['Total outliers'], ascending=False)

    def standardize(dataframe):
        try:
            data = dataframe.select_dtypes(include=np.number)
            scaler = StandardScaler()
            scaler.fit(data)
            scaled_dataframe = pd.DataFrame(scaler.fit_transform(data), columns=list(data.columns))
            return scaled_dataframe
        except Exception as e:
            print(e)


    active_tab = st.sidebar.selectbox('Select your outlier detection test', ['IQR Test', 'Z-Score Test'])

    if active_tab == "IQR Test":
        st.markdown("""A IQR test rule says that a data point is an outlier if it is more than 1.5 * IQR above the 
                    third quartile or below the first quartile in other words low outliers are below Q1 - 1.5 IQR and high
                    outliers are above Q3 + 1.5 * IQR""")
        iqr_outlier = outlier_detection_iqr(df)
        fig1 = px.bar(iqr_outlier, x='Features', y='Total outliers')
        fig1.update_layout(width=1100)
        st.write(fig1)
        st.write(iqr_outlier)

        option = st.selectbox('How would you like to be visualize?', ('Boxplot', 'Scatter plot'))
        features = list(df.select_dtypes(include=np.number).columns);features.insert(0, 'ALL')
        if option == "Boxplot":
            form1 = st.form(key='box-plot')
            with form1:
                features_selected = st.multiselect('Select features ', features)
                submit1 = form1.form_submit_button('Submit')
            if submit1:
                if 'ALL' not in features_selected:
                    for feature in features_selected:
                        try:
                            info = outlier_detection_iqr(df[[feature]])
                            fig5 = px.box(df, y=feature)
                            fig5.update_layout(width=1100, font_family="Courier New, monospace",font_color="RebeccaPurple",
                                               font_size=15)
                            st.plotly_chart(fig5)
                            st.write(info)
                        except Exception as e:
                            print(e)

                elif 'ALL' in features_selected:
                    for column in df.select_dtypes(include=np.number).columns:
                        try:
                            info = outlier_detection_iqr(df[[column]])
                            fig6 = px.box(df, y=column)
                            fig6.update_layout(width=1100, font_family="Courier New, monospace",font_color="RebeccaPurple",
                                               font_size=15)
                            st.plotly_chart(fig6)
                            st.write(info)
                        except Exception as e:
                            print(e)

        elif option == "Scatter plot":
            st.write("An outlier for a scatter plot is the point or points that are farthest from the regression line.")
            form2 = st.form(key='scatter-plot')
            with form2:
                target_features = list(df.select_dtypes(include=np.number).columns)
                target_variable = st.selectbox("Select target feature", target_features)
                x_axis_features = st.multiselect("Select feature on x axis", target_features)
                submit2 = form2.form_submit_button('Submit')
            if submit2:
                for feature in x_axis_features:
                    try:
                        fig7 = px.scatter(df, x=feature, y=target_variable, trendline="ols")
                        fig7.update_layout(width=1100)
                        st.write(fig7)
                    except ValueError as e:
                        print(e)

    elif active_tab == "Z-Score Test":
        st.markdown("""Z-scores can quantify the unusualness of an observation when your data follow the normal distribution. 
        Z-scores are the number of standard deviations above and below the mean that each value falls, the value 
        return z-score grater or less than +3 & -3 respectively are considered as outliers""")
        zscore_outlier = z_score_outlier_detection(df)
        fig2 = px.bar(zscore_outlier, x='Features', y='Total outliers')
        fig2.update_layout(width=1100)
        st.write(fig2)
        st.write(zscore_outlier)

        option = st.selectbox('How would you like to be visualize?', ('Distplot', 'Scatter plot'))
        features = list(df.select_dtypes(include=np.number).columns);
        features.insert(0, 'ALL')
        if option == 'Distplot':
            form3 = st.form(key='distplot')
            with form3:
                features_selected = st.multiselect('Select features ', features)
                submit3 = form3.form_submit_button('Submit')
            if submit3:
                scaled_data = standardize(df)
                if 'ALL' not in features_selected:
                    for feature in features_selected:
                        try:
                            info = z_score_outlier_detection(df[[feature]])
                            fig3 = ff.create_distplot([scaled_data[feature].fillna(0)], [feature], bin_size=.1,
                                                      show_rug=False,
                                                      curve_type='kde')
                            fig3.update_layout(width=1100, height=400, bargap=0.01, template='plotly_dark',
                                               xaxis=dict(title=f'-----{feature}-----'))
                            st.write(fig3)
                            st.write(info)
                        except Exception as e:
                            print(e)

                elif 'ALL' in features_selected:
                    for column in df.select_dtypes(include=np.number).columns:
                        try:
                            info = z_score_outlier_detection(df[[column]])
                            fig4 = ff.create_distplot([scaled_data[column].fillna(0)], [column],
                                                      bin_size=.1, show_rug=False, curve_type='kde')
                            fig4.update_layout(width=1100, height=400,
                                               bargap=0.01, template='plotly_dark', xaxis=dict(title=f'-----{column}-----'))
                            st.write(fig4)
                            st.write(info)
                        except Exception as e:
                            print(e)

        elif option == "Scatter plot":
            st.write("An outlier for a scatter plot is the point or points that are farthest from the regression line.")
            form4 = st.form(key='scatter-plot2')
            with form4:
                target_features = list(df.select_dtypes(include=np.number).columns)
                target_variable = st.selectbox("Select target feature", target_features)
                x_axis_features = st.multiselect("Select feature on x axis", target_features)
                submit4 = form4.form_submit_button('Submit')
            if submit4:
                for feature in x_axis_features:
                    try:
                        fig7 = px.scatter(df, x=feature, y=target_variable, trendline="ols")
                        fig7.update_layout(width=1100)
                        st.write(fig7)
                    except ValueError as e:
                        print(e)

    else:
        st.error("Something has gone terribly wrong.")


#fig3.update_layout(template='plotly_dark')