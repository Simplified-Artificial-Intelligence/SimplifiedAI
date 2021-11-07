import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error


class ModelTrain_Regression:
    def __init__(self, X_train, X_test, y_train, y_test, start: bool):
        self.frame = pd.DataFrame(columns=['Model_Name', 'MAE', 'RMSE'])
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

        if start:
            self.linear_regression_()
            self.Lasso_()
            self.ridge_()
            self.ElasticNet_()
            self.SVR_()
            self.KNeighborsRegressor_()
            self.DecisionTreeRegressor_()
            self.RandomForestRegressor_()
            self.AdaBoostRegressor_()
            self.GradientBoostingRegressor_()

    def linear_regression_(self):
        model = LinearRegression()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'LinearRegression', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def ridge_(self):
        model = Ridge()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'Ridge', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def Lasso_(self):
        model = Lasso()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'Lasso', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def ElasticNet_(self):
        model = ElasticNet()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'ElasticNet', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def SVR_(self):
        model = SVR()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'SVR', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def KNeighborsRegressor_(self):
        model = KNeighborsRegressor()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'KNeighborsRegressor', 'MAE': MAE, 'RMSE': RMSE},
                                       ignore_index=True)

    def DecisionTreeRegressor_(self):
        model = DecisionTreeRegressor()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'DecisionTreeRegressor', 'MAE': MAE, 'RMSE': RMSE},
                                       ignore_index=True)

    def RandomForestRegressor_(self):
        model = RandomForestRegressor()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'RandomForestRegressor', 'MAE': MAE, 'RMSE': RMSE},
                                       ignore_index=True)

    def AdaBoostRegressor_(self):
        model = AdaBoostRegressor()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'AdaBoostRegressor', 'MAE': MAE, 'RMSE': RMSE}, ignore_index=True)

    def GradientBoostingRegressor_(self):
        model = GradientBoostingRegressor()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        MAE = mean_absolute_error(self.y_test, y_pred)
        RMSE = np.sqrt(mean_squared_error(self.y_test, y_pred))
        self.frame = self.frame.append({'Model_Name': 'GradientBoostingRegressor', 'MAE': MAE, 'RMSE': RMSE},
                                       ignore_index=True)

    def results(self):
        return self.frame.sort_values('MAE')