#!/usr/bin/env python
# coding: utf-8

import pandas as pd 
import numpy as np 
from sklearn.preprocessing import StandardScaler 
from sklearn.linear_model  import LogisticRegression
from sklearn.model_selection import train_test_split
from statsmodels.stats.outliers_influence import variance_inflation_factor 
import classification_models as cm



df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv')

df.head()

df['BMI'] = df['BMI'].replace(0, df['BMI'].mean())

df['BloodPressure'] = df['BloodPressure'].replace(0, df['BloodPressure'].mean())

df['Insulin'] = df['Insulin'].replace(0, df['Insulin'].mean())

df['Glucose'] = df['Glucose'].replace(0, df['Glucose'].mean())

df['SkinThickness'] = df['SkinThickness'].replace(0, df['SkinThickness'].mean())


q = df['Insulin'].quantile(q=0.98)
df_new = df[df['Insulin'] < q]

q = df['Pregnancies'].quantile(q=0.98)
df_new = df[df['Pregnancies'] < q]

q = df_new['BMI'].quantile(q=0.99)
df_new = df_new[df_new['BMI'] < q]

q = df_new['SkinThickness'].quantile(q=0.99)
df_new = df_new[df_new['SkinThickness'] < q]

q = df_new['Insulin'].quantile(q=0.95)
df_new = df_new[df_new['Insulin'] < q]

q = df_new['DiabetesPedigreeFunction'].quantile(q=0.99)
df_new = df_new[df_new['DiabetesPedigreeFunction'] < q]

q = df_new['Age'].quantile(q=0.99)
df_new = df_new[df_new['Age'] < q]

def outlier_removal(self,data):
        def outlier_limits(col):
            Q3, Q1 = np.nanpercentile(col, [75,25])
            IQR= Q3-Q1
            UL= Q3+1.5*IQR
            LL= Q1-1.5*IQR
            return UL, LL

        for column in data.columns:
            if data[column].dtype != 'int64':
                UL, LL= outlier_limits(data[column])
                data[column]= np.where((data[column] > UL) | (data[column] < LL), np.nan, data[column])

        return data

y = df_new["Outcome"]
X = df_new.drop(columns="Outcome")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

pd.DataFrame([[df_new.columns[i], variance_inflation_factor(X_scaled, i)] for i in range(X_scaled.shape[1])], columns=["Feature", "vif"])


model = cm.ClassificationModels(X_scaled, y)

model.custom_train_test_split(test_size=.20, random_state=144)

model.logistic_regression()

# X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=.20, random_state=144)

# logr = LogisticRegression(verbose=1)

# logr.fit(X_train, y_train)

# y_pred = logr.predict(X_test)
# y_pred

# logr.predict([X_test[0]])

