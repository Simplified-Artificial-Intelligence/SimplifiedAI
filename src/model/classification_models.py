from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
import pickle


def save_model(model, path):
    pickle.dump(model, path)


class ClassificationModels:
    def __init__(self, X_train, X_test, y_train, y_test, path):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.path = path

    def logistic_regression_classifier(self, penalty='l2', dual=False, tol=0.0001, C=1.0, fit_intercept=True,
                                       intercept_scaling=1, class_weight=None, random_state=None, solver='lbfgs',
                                       max_iter=100, multi_class='auto', verbose=0,

                                       warm_start=False, n_jobs=None, l1_ratio=None):
        model = LogisticRegression(penalty=penalty, dual=dual, tol=tol, C=C, fit_intercept=fit_intercept,
                                   intercept_scaling=intercept_scaling, class_weight=class_weight,
                                   random_state=random_state, solver=solver, max_iter=max_iter,
                                   multi_class=multi_class, verbose=verbose, warm_start=warm_start, n_jobs=n_jobs,
                                   l1_ratio=l1_ratio)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def decision_tree_classifier(self, criterion='gini', splitter='best', max_depth=None, min_samples_split=2,
                                 min_samples_leaf=1, min_weight_fraction_leaf=0.0,
                                 max_features=None, random_state=None, max_leaf_nodes=None,
                                 min_impurity_decrease=0.0, class_weight=None, ccp_alpha=0.0):
        model = DecisionTreeClassifier(criterion=criterion, splitter=splitter, max_depth=max_depth,
                                       min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                                       min_weight_fraction_leaf=min_weight_fraction_leaf,
                                       max_features=max_features, random_state=random_state,
                                       max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=min_impurity_decrease,
                                       class_weight=class_weight, ccp_alpha=ccp_alpha)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def k_neighbors_classifier(self, n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2,
                               metric='minkowski', metric_params=None, n_jobs=None):
        model = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm,
                                     leaf_size=leaf_size, p=p, metric=metric,
                                     metric_params=metric_params, n_jobs=n_jobs)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def support_vector_classifier(self, C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0,
                                  shrinking=True, probability=False, tol=0.001, cache_size=200,
                                  class_weight=None, verbose=False, max_iter=-1, decision_function_shape='ovr',
                                  break_ties=False, random_state=None):
        model = SVC(C=C, kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, shrinking=shrinking,
                    probability=probability, tol=tol, cache_size=cache_size, class_weight=class_weight,
                    verbose=verbose, max_iter=max_iter, decision_function_shape=decision_function_shape,
                    break_ties=break_ties, random_state=random_state)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def random_forest_classifier(self, n_estimators=100, criterion='gini', max_depth=None, min_samples_split=2,
                                 min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto',
                                 max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=True, oob_score=False,
                                 n_jobs=None, random_state=None, verbose=0, warm_start=False, class_weight=None,
                                 ccp_alpha=0.0, max_samples=None):
        model = RandomForestClassifier(n_estimators=n_estimators, criterion=criterion,
                                       max_depth=max_depth, min_samples_split=min_samples_split,
                                       min_samples_leaf=min_samples_leaf,
                                       min_weight_fraction_leaf=min_weight_fraction_leaf,
                                       max_features=max_features, max_leaf_nodes=max_leaf_nodes,
                                       min_impurity_decrease=min_impurity_decrease,
                                       bootstrap=bootstrap, oob_score=oob_score,
                                       n_jobs=n_jobs, random_state=random_state, verbose=verbose,
                                       warm_start=warm_start, class_weight=class_weight,
                                       ccp_alpha=ccp_alpha, max_samples=max_samples)

        model.fit(self.X_train, self.y_train)

        save_model(model, self.path)
        return model.predict(self.X_test)
