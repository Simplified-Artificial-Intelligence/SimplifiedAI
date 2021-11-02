from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle


class RegressionModels:
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
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.x, self.y, train_size=train_size,
                                                                                test_size=test_size,
                                                                                random_state=random_state,
                                                                                shuffle=shuffle, stratify=stratify)

    def linearRegression(self,):
        pass

    model = LinearRegression()
    @staticmethod
    def save_model(model):
        with open(
                f'E:/iNeuron/Full Stack Data Science/Internship/Projectathon/artifacts/models' + '/modelForPrediction.sav',
                'wb') as f:
            pickle.dump(model, f)
