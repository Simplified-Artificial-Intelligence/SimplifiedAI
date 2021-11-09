import pandas as pd
import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, PowerTransformer, MaxAbsScaler
from sklearn.feature_selection import SelectKBest, chi2, VarianceThreshold, mutual_info_classif
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.decomposition import PCA
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.tree import DecisionTreeClassifier
import numpy as np


class FeatureEngineering:
    def __init__(self):
        pass

    @staticmethod
    def change_column_name(df, column, new_name):
        """[summary]
        Change Column Name
        Args:
            df ([type]): [description]
            column ([type]): [description]
            new_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        df = df.rename(columns={column: new_name})
        return df

    @staticmethod
    def change_data_type(df, column, type_):
        """[summary]
        Change Column DataType
        Args:
            df ([type]): [description]
            column ([type]): [description]
            type_ ([type]): [description]

        Returns:
            [type]: [description]
        """
        df[column] = df[column].astype(type_)
        return df
    
    def train_test_Split(self, cleanedData, label, test_size, random_state):

        X_train, X_test, y_train, y_test = train_test_split(cleanedData,
                                                            label,
                                                            test_size=test_size,
                                                            random_state=random_state)
        return X_train, X_test, y_train, y_test

    @staticmethod
    def scaler(data, typ):
        if typ == 'MinMax Scaler':
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        elif typ == 'Standard Scaler':
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        elif typ == 'Robust Scaler':
            scaler = RobustScaler()
            scaled_data = scaler.fit_transform(data)

        elif typ == 'Power Transformer Scaler':
            scaler = PowerTransformer(method='yeo-johnson')
            scaled_data = scaler.fit_transform(data)

        elif typ == 'Max Abs Scaler':
            scaler = MaxAbsScaler()
            scaled_data = scaler.fit_transform(data)

            return scaled_data

        else:
            return 'Please Specify type correctly'

    @staticmethod
    def encodings(df, cols, kind: str, **kwarga):
        if kind == 'Label/Ordinal Encoder':
            label = ce.OrdinalEncoder(cols=cols, **kwarga)
            label_df = label.fit_transform(df)
            return label_df

        elif kind == 'One Hot Encoder':
            onehot = ce.OneHotEncoder(cols=cols)
            onehot_df = onehot.fit_transform(df)
            return onehot_df

        elif kind == 'Binary Encoder':
            onehot = ce.BinaryEncoder(cols=cols, **kwarga)
            onehot_df = onehot.fit_transform(df)
            return onehot_df

        elif kind == 'Base N Encoder':
            onehot = ce.BaseNEncoder(cols=cols)
            onehot_df = onehot.fit_transform(df)
            return onehot_df

        elif kind == 'Hash Encoder':
            hash_ = ce.HashingEncoder(cols=cols, **kwarga)
            hash_df = hash_.fit_transform(df)
            return hash_df

        elif kind == 'Target Encoder':
            target = ce.TargetEncoder(cols=cols)
            target_df = target.fit_transform(df, **kwarga)
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

    @staticmethod
    def feature_selection(features, target, typ, **kwargs):
        important_features = pd.DataFrame()
        if typ == 'SelectKBest':
            # chi2 + anova test
            best_features = SelectKBest(score_func=chi2, **kwargs)
            imp = best_features.fit(features, target)
            important_features['score'] = imp.scores_
            important_features['columns'] = features.columns

            return important_features.sort_values('scores', ascending=False)

        elif typ == 'Find Constant Features':
            # chi2 + anova test
            vari_thr = VarianceThreshold(**kwargs)
            imp = vari_thr.fit(features)
            return features.columns[imp.get_support()]

        elif typ == 'Extra Trees Classifier':

            best_features = ExtraTreesClassifier()
            best_features.fit(features, target)
            df = pd.DataFrame()
            df['Value'] = best_features.feature_importances_
            df['Feature'] = features.columns
            return df.sort_values(by='Value', ascending=False)

        elif typ == 'Extra Trees Regressor':
            best_features = ExtraTreesRegressor()
            best_features.fit(features, target)
            important_features['score'] = best_features.feature_importances_
            important_features['columns'] = features.columns

            return important_features.sort_values('scores', ascending=False)

        elif typ == 'Mutual Info Classification':
            importance = mutual_info_classif(features, target)
            df = pd.DataFrame()
            df['Value'] = importance
            df['Feature'] = features.columns
            return df.sort_values(by='Value', ascending=False)

        elif typ == 'Forward Selection':
            dclas = DecisionTreeClassifier()
            sfs = SequentialFeatureSelector(dclas, scoring='balanced_accuracy', **kwargs)
            sfs.fit(features, target)
            return list(features.columns[sfs.get_support()])

        elif typ == 'Backward Elimination':
            dclas = DecisionTreeClassifier()
            sfs = SequentialFeatureSelector(dclas, direction='backward', scoring='balanced_accuracy', **kwargs)
            sfs.fit(features, target)
            return list(features.columns[sfs.get_support()])
        else:
            return 'Please Specify type correctly'

    @staticmethod
    def dimenstion_reduction(data, comp):
        model = PCA(n_components=comp)
        pca = model.fit_transform(data)
        return pca, np.cumsum(model.explained_variance_ratio_)
