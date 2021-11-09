import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class ModelTrain_Classification:
    def __init__(self, X_train, X_test, y_train, y_test, start: bool):
        self.frame = pd.DataFrame(columns=['Model_Name', 'Accuracy', 'Precision', 'Recall', 'F1_Score'])
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

        if start:
            self.LogisticRegression_()
            self.SVC_()
            self.KNeighborsClassifier_()
            self.DecisionTreeClassifier_()
            self.RandomForestClassifier_()
            self.GradientBoostingClassifier_()
            self.AdaBoostClassifier_()

    def LogisticRegression_(self):
        model = LogisticRegression()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'LogisticRegression', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def SVC_(self):
        model = SVC()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'SVC', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def KNeighborsClassifier_(self):
        model = KNeighborsClassifier()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'KNeighborsClassifier', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def DecisionTreeClassifier_(self):
        model = DecisionTreeClassifier()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'DecisionTreeClassifier', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def RandomForestClassifier_(self):
        model = RandomForestClassifier()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'RandomForestClassifier', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def GradientBoostingClassifier_(self):
        model = GradientBoostingClassifier()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'GradientBoostingClassifier', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def AdaBoostClassifier_(self):
        model = AdaBoostClassifier()
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1_score_ = f1_score(self.y_test, y_pred)
        self.frame = self.frame.append(
            {'Model_Name': 'AdaBoostClassifier', 'Accuracy': accuracy, 'Precision': precision, 'Recall': recall,
             'F1_Score': f1_score_}, ignore_index=True)

    def results(self):
        return self.frame.sort_values('F1_Score')
