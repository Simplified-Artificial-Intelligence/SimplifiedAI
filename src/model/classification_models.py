
from os import stat
from sklearn.linear_model  import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle

class ClassificationModels:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def custom_train_test_split(
        self,
        test_size=None,
        train_size=None,
        random_state=None,
        shuffle=True,
        stratify=None):

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.x, self.y, train_size=train_size, test_size=test_size, random_state=random_state, shuffle=shuffle, stratify=stratify)


    def logistic_regression(
        self, 
        penalty='l2',
        dual=False,
        tol=0.0001,
        C=1.0,
        fit_intercept=True,
        intercept_scaling=1,
        class_weight=None,
        random_state=None,
        solver='lbfgs',
        max_iter=100,
        multi_class='auto',
        verbose=0,
        warm_start=False,
        n_jobs=None,
        l1_ratio=None):

        logr = LogisticRegression(
            penalty=penalty,
            dual=dual,
            tol=tol,
            C=C,
            fit_intercept=fit_intercept,
            intercept_scaling=intercept_scaling,
            class_weight=class_weight,
            random_state=random_state,
            solver=solver,
            max_iter=max_iter,
            multi_class=multi_class,
            verbose=verbose,
            warm_start=warm_start,
            n_jobs=n_jobs,
            l1_ratio=l1_ratio)

        logr.fit(self.X_train, self.y_train)

        ClassificationModels.save_model(logr)

    
    @staticmethod
    def save_model(model):
        with open(f'E:/iNeuron/Full Stack Data Science/Internship/Projectathon/artifacts/models'+ '/modelForPrediction.sav', 'wb') as f:
            pickle.dump(model, f)
