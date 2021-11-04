import pandas as pd
import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler , RobustScaler
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.ensemble import ExtraTreesClassifier,ExtraTreesRegressor
from sklearn.decomposition import PCA


class FeatureEngineering:
    def __init__(self):
        pass

    def train_test_Split(self, cleanedData, label, test_size, random_state):

        X_train, X_test, y_train, y_test = train_test_split(cleanedData,
                                                            label,
                                                            test_size=test_size,
                                                            random_state=random_state)
        return X_train, X_test, y_train, y_test

    def scaler_(self, data, typ):
        if typ == 'MinMaxScaler':
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        elif typ == 'StandardScaler':
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        elif typ == 'RobustScaler':
            scaler = RobustScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        else:
            return 'Please Specify type correclty'

    def encodings(self, df, cols, kind: str):
        if kind == 'Label/Ordinal Encoder':
            label = ce.OrdinalEncoder(cols=cols)
            label_df = label.fit_transform(df)
            return label_df

        elif kind == 'One Hot Encoder':
            onehot = ce.OneHotEncoder(cols=cols)
            onehot_df = onehot.fit_transform(df)
            return onehot_df

        elif kind == 'Hash Encoder':
            hash_ = ce.HashingEncoder(cols=cols)
            hash_df = hash_.fit_transform(df)
            return hash_df

        elif kind == 'Target Encoder':
            target = ce.TargetEncoder(cols=cols)
            target_df = target.fit_transform(df)
            return target_df

        else:
            return 'Please Specify type correclty'

    def handleDatetime(self, frame, cols):
        year = pd.DataFrame()
        day = pd.DataFrame()
        month = pd.DataFrame()
        count = 0
        for col in cols:
            frame[col] = pd.to_datetime(frame[col])

            year[f'{col}_{count}'] = pd.to_datetime(frame[col]).dt.year
            count += 1
            day[f'{col}_{count}'] = pd.to_datetime(frame[col]).dt.day
            count += 1
            month[f'{col}_{count}'] = pd.to_datetime(frame[col]).dt.month
            count += 1

        frame = pd.concat([frame, year, day, month], axis=1)
        return frame

    def feature_selection(self, features, target, typ, k=None):
        important_features = pd.DataFrame()
        if typ == 'SelectKBest':
            # chi2 + anova test
            best_features = SelectKBest(score_func=chi2, k=k)
            imp = best_features.fit(features, target)
            important_features['score'] = imp.scores_
            important_features['columns'] = features.columns

            return important_features.sort_values('scores', ascending=False)

        elif typ == 'Extra Trees Classifier':

            best_features = ExtraTreesClassifier()
            best_features.fit(features, target)
            important_features['score'] = best_features.feature_importances_
            important_features['columns'] = features.columns

            return important_features.sort_values('scores', ascending=False)

        elif typ == 'Extra Trees Regressor':
            best_features = ExtraTreesRegressor()
            best_features.fit(features, target)
            important_features['score'] = best_features.feature_importances_
            important_features['columns'] = features.columns

            return important_features.sort_values('scores', ascending=False)
        else:
            return 'Please Specify type correclty'

    def dimenstion_reduction(self, features, target, comp):
        model = PCA(n_components=comp)
        features = model.fit_transform(features)
        return pd.concat([features, target], axis=1)