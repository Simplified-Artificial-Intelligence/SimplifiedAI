from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
import pickle


# Save Model In artifacts
def save_model(model, path):
    pickle.dump(model, path)


# Regression Class for custom training
class RegressionModels:
    def __init__(self, X_train, X_test, y_train, y_test, path):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.path = path

    def linear_regression_regressor(self, fit_intercept=True, copy_X=True,
                                    n_jobs=None, positive=False):
        model = LinearRegression(fit_intercept=fit_intercept, copy_X=copy_X, n_jobs=n_jobs, positive=positive)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def ridge_regressor(self, alpha=1.0, fit_intercept=True, copy_X=True,
                        max_iter=None, tol=0.001, solver='auto', positive=False, random_state=None):
        model = Ridge(alpha=alpha, fit_intercept=fit_intercept, copy_X=copy_X,
                      max_iter=max_iter, tol=tol, solver=solver, positive=positive, random_state=random_state)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def lasso_regressor(self, alpha=1.0, fit_intercept=True, precompute=False, copy_X=True, max_iter=1000,
                        tol=0.0001, warm_start=False, positive=False, random_state=None, selection='cyclic'):
        model = Lasso(alpha=alpha, fit_intercept=fit_intercept, precompute=precompute, copy_X=copy_X,
                      max_iter=max_iter, tol=tol, warm_start=warm_start, positive=positive,
                      random_state=random_state, selection=selection)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def elastic_net_regressor(self, alpha=1.0, l1_ratio=0.5, fit_intercept=True,
                              precompute=False, max_iter=1000, copy_X=True, tol=0.0001, warm_start=False,
                              positive=False, random_state=None, selection='cyclic'):
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, fit_intercept=fit_intercept, precompute=precompute,
                           copy_X=copy_X, max_iter=max_iter, tol=tol, warm_start=warm_start, positive=positive,
                           random_state=random_state, selection=selection)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def decision_tree_regressor(self, criterion='squared_error', splitter='best', max_depth=None,
                                min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0,
                                max_features=None, random_state=None, max_leaf_nodes=None,
                                min_impurity_decrease=0.0, ccp_alpha=0.0):
        model = DecisionTreeRegressor(criterion=criterion, splitter=splitter, max_depth=max_depth,
                                      min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                                      min_weight_fraction_leaf=min_weight_fraction_leaf,
                                      max_features=max_features, random_state=random_state,
                                      max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=min_impurity_decrease,
                                      ccp_alpha=ccp_alpha)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def random_forest_regressor(self, n_estimators=100, criterion='squared_error', max_depth=None,
                                min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0,
                                max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0,
                                bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0,
                                warm_start=False, ccp_alpha=0.0, max_samples=None):
        model = RandomForestRegressor(n_estimators=n_estimators, criterion=criterion, max_depth=max_depth,
                                      min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                                      min_weight_fraction_leaf=min_weight_fraction_leaf,
                                      max_features=max_features, max_leaf_nodes=max_leaf_nodes,
                                      min_impurity_decrease=min_impurity_decrease, bootstrap=bootstrap,
                                      oob_score=oob_score, n_jobs=n_jobs, random_state=random_state,
                                      verbose=verbose, warm_start=warm_start, ccp_alpha=ccp_alpha,
                                      max_samples=max_samples)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def support_vector_regressor(self, kernel='rbf', degree=3, gamma='scale', coef0=0.0, tol=0.001, C=1.0,
                                 epsilon=0.1, shrinking=True, cache_size=200, verbose=False, max_iter=- 1):
        model = SVR(kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, tol=tol, C=C, epsilon=epsilon,
                    shrinking=shrinking, cache_size=cache_size, verbose=verbose, max_iter=max_iter)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def ada_boost_regressor(self, base_estimator=None, n_estimators=50, learning_rate=1.0, loss='linear',
                            random_state=None):
        model = AdaBoostRegressor(base_estimator=base_estimator, n_estimators=n_estimators,
                                  learning_rate=learning_rate, loss=loss, random_state=random_state)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def gradient_boosting_regressor(self, loss='squared_error', learning_rate=0.1, n_estimators=100,
                                    subsample=1.0, criterion='friedman_mse', min_samples_split=2,
                                    min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_depth=3,
                                    min_impurity_decrease=0.0, init=None, random_state=None, max_features=None,
                                    alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False,
                                    validation_fraction=0.1, n_iter_no_change=None, tol=0.0001, ccp_alpha=0.0):
        model = GradientBoostingRegressor(loss=loss, learning_rate=learning_rate, n_estimators=n_estimators,
                                          subsample=subsample, criterion=criterion, min_samples_split=min_samples_split,
                                          min_samples_leaf=min_samples_leaf,
                                          min_weight_fraction_leaf=min_weight_fraction_leaf,
                                          max_depth=max_depth, min_impurity_decrease=min_impurity_decrease, init=init,
                                          random_state=random_state, max_features=max_features, alpha=alpha,
                                          verbose=verbose,
                                          max_leaf_nodes=max_leaf_nodes, warm_start=warm_start,
                                          validation_fraction=validation_fraction,
                                          n_iter_no_change=n_iter_no_change, tol=tol, ccp_alpha=ccp_alpha)
