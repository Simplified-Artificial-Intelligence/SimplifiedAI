# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression, Ridge, Lasso, RidgeCV, LassoCV, ElasticNet, ElasticNetCV, LassoLars
# from sklearn.metrics import mean_squared_error, r2_score
# import pickle
#
#
# class LinearModels:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     def custom_train_test_split(self, test_size=None, train_size=None, random_state=None, shuffle=True, stratify=None):
#         self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.x, self.y, train_size=train_size,
#                                                                                 test_size=test_size,
#                                                                                 random_state=random_state,
#                                                                                 shuffle=shuffle, stratify=stratify)
#
#     @staticmethod
#     def adj_r2(x, y, r2):
#         n = x.shape[0]
#         p = x.shape[1]
#         adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
#         return adjusted_r2
#
#     def Linear_Regression(self, fit_intercept=True, normalize=False, copy_X=True, n_jobs=None, v_positive=False):
#         model = LinearRegression(fit_intercept=fit_intercept, normalize=normalize, copy_X=copy_X, n_jobs=n_jobs)
#         # Training the model
#         model.fit(self.X_train, self.y_train)
#
#         y_pred = model.predict(self.X_test)
#         r2 = model.score(self.X_test, self.y_test)
#         # Evaluating Model
#         print("Model Evaluation : ")
#         print("coef_ : ", model.coef_)
#         print("intercept_ : %.4f" % model.intercept_)
#         print("Score :  %.4f" % model.score(self.X_test, self.y_test))
#         print("Adjusted R2 :  %.4f" % LinearModels.adj_r2(self.X_test, self.y_test, r2))
#         print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
#         print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))
#         LinearModels.save_model(model, "Linear_Regression")
#
#     def Ridge_Regression(self, cv=10, fit_intercept=True, normalize=False, copy_X=True, max_iter=None, tol=0.001,
#                          solver='auto', v_positive=False, random_state=None):
#         ridgecv = RidgeCV(alphas=np.random.uniform(0, 10, 50), cv=cv, normalize=normalize)
#         ridgecv.fit(self.X_train, self.y_train)
#
#         model = Ridge(alpha=ridgecv.alpha_, fit_intercept=fit_intercept, normalize=normalize, copy_X=copy_X,
#                       max_iter=max_iter, tol=tol, solver=solver, random_state=random_state)
#
#         # Training the model
#         model.fit(self.X_train, self.y_train)
#
#         y_pred = model.predict(self.X_test)
#         r2 = model.score(self.X_test, self.y_test)
#         # Evaluating Model
#         print("Model Evaluation : ")
#         print("coef_ : ", model.coef_)
#         print("intercept_ : %.4f" % model.intercept_)
#         print("Score :  %.4f" % model.score(self.X_test, self.y_test))
#         print("Adjusted R2 :  %.4f" % LinearModels.adj_r2(self.X_test, self.y_test, r2))
#         print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
#         print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))
#
#         # Saving model file
#         LinearModels.save_model(model, "Ridge_Regression")
#
#     def Lasso_Regression(self, cv=50, fit_intercept=True, normalize=False, precompute=False, copy_X=True, max_iter=1000,
#                          tol=0.0001, warm_start=False, v_positive=False, random_state=None, selection='cyclic'):
#         lassocv = LassoCV(alphas=None, cv=cv, max_iter=max_iter, normalize=normalize)
#         lassocv.fit(self.X_train, self.y_train)
#
#         model = Lasso(alpha=lassocv.alpha_, fit_intercept=fit_intercept, normalize=normalize, precompute=precompute,
#                       copy_X=copy_X, max_iter=max_iter, tol=tol, warm_start=warm_start, positive=v_positive,
#                       random_state=random_state, selection=selection)
#
#         # Training the model
#         model.fit(self.X_train, self.y_train)
#
#         y_pred = model.predict(self.X_test)
#         r2 = model.score(self.X_test, self.y_test)
#         # Evaluating Model
#         print("Model Evaluation : ")
#         print("coef_ : ", model.coef_)
#         print("intercept_ : %.4f" % model.intercept_)
#         print("Score :  %.4f" % model.score(self.X_test, self.y_test))
#         print("Adjusted R2 :  %.4f" % LinearModels.adj_r2(self.X_test, self.y_test, r2))
#         print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
#         print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))
#
#         # Saving model file
#         LinearModels.save_model(model, "Lasso_Regression")
#
#     def ElasticNet_Regression(self, cv=10, alpha=1.0, l1_ratio=0.5, fit_intercept=True, normalize=False):
#         elastic = ElasticNetCV(alphas=None, cv=cv)
#         elastic.fit(self.X_train, self.y_train)
#
#         model = ElasticNet(alpha=elastic.alpha_, l1_ratio=elastic.l1_ratio_, fit_intercept=fit_intercept,
#                            normalize=normalize)
#
#         # Training the model
#         model.fit(self.X_train, self.y_train)
#
#         y_pred = model.predict(self.X_test)
#         r2 = model.score(self.X_test, self.y_test)
#         # Evaluating Model
#         print("Model Evaluation : ")
#         print("coef_ : ", model.coef_)
#         print("intercept_ : %.4f" % model.intercept_)
#         print("Score :  %.4f" % model.score(self.X_test, self.y_test))
#         print("Adjusted R2 :  %.4f" % LinearModels.adj_r2(self.X_test, self.y_test, r2))
#         print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
#         print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))
#
#         # Saving model file
#         LinearModels.save_model(model, "ElasticNet_Regression")
#
#     def save_model(model, filename):
#         # with open(f'E:/iNeuron/Full Stack Data Science/Internship/Projectathon/artifacts/models'+ '/modelForPrediction.sav', 'wb') as f:
#         with open(filename + 'modelForPrediction.sav', 'wb') as f:
#             pickle.dump(model, f)