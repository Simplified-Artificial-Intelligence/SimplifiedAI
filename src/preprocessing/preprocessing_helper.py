import pandas as pd
import numpy as np
import category_encoders as ce
import seaborn as sns
from sklearn.preprocessing import normalize
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE

class Preprocessing():

    def get_data(self, filepath):
        try:
            data = filepath
            df = pd.read_csv(data)
            return df
        except Exception as e:
            return e

    def col_seperator(self, df, typ: str):
        try:
            if typ == 'Numerical_columns':
                Numerical_columns = df.select_dtypes(exclude='object')
                return Numerical_columns

            elif typ == 'Categorical_columns':
                Categorical_columns = df.select_dtypes(include='object')
                return Categorical_columns
            else:
                return 'Type Not Found'
        except Exception as e:
            return e

    def delete_col(self, df, cols:list):

        temp_list = []
        for i in cols:
            if i in df.cols:
                temp_list.append(i)
            else:
                return 'Column Not Found'

        try:
            df = df.drop(temp_list, axis=1)
            return df
        except Exception as e:
            return e

    def missing_values(self, df):
        try:
            columns = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False).index
            values = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False).values

            mv_df = pd.DataFrame(columns, columns=['Columns'])

            mv_df['Missing_Values'] = values
            mv_df['Percentage'] = np.round((values / len(df)) * 100, 2)

            return columns, values, mv_df

        except Exception as e:
            return e

    def fill_numerical(self, df, typ, cols):
        for i in cols:
            if i in df.cols:
                continue
            else:
                return 'Column Not Found'
        if typ == 'Mean':
            try:
                return df[cols].fillna(df[cols].mean())
            except Exception as e:
                return e
        elif typ == 'Median':
            try:
                return df[cols].fillna(df[cols].median())
            except Exception as e:
                return e

        elif typ == 'Interpolate':
            try:
                return df[cols].interpolate()
            except Exception as e:
                return e
        else:
            return 'Type Not present'

    def fill_categorical(self, df, typ=None, col=None, value=None):
        # Replace na with some meaning of na
        if typ == 'replace':
            temp_list = []
            for i in col:
                if i in df.cols:
                    temp_list.append(i)
                else:
                    return 'Column Not Found'

            if col and value is not None:
                return df[col].fillna(value)
            else:
                return 'Please give provide values and columns'
        elif typ == 'Mode':
            if col and value is not None:
                return df[col].fillna(df[col].mode()[0])
            else:
                return 'Please give provide values and columns'
        else:
            return 'Type not found'

    def Unique(self, df, percent):
        percent = percent/25
        holder = []
        for column in df.columns:
            if df[column].nunique() > int(len(df) * percent / 4):
                print(column, '+', df[column].unique())
                holder.append(column)
        return holder


    #https://www.analyticsvidhya.com/blog/2020/08/types-of-categorical-data-encoding/
    def encodings(self, df, cols, kind: str):
        if kind == 'Label/Ordinal Encoder':
            label = ce.OrdinalEncoder(cols=cols)
            label_df = label.fit_transform(df)
            return label_df
        elif kind == 'One Hot Encoder':
            onehot=ce.OneHotEncoder(cols=cols)
            onehot_df = onehot.fit_transform(df)
            return onehot_df
        elif kind == 'Hash Encoder':
            hash = ce.HashingEncoder(cols=cols)
            hash_df = hash.fit_transform(df)
            return hash_df
        elif kind == 'Target Encoder':
            target = ce.TargetEncoder(cols=cols)
            target_df = target.fit_transform(df)
            return target_df
        else:
            pass






    def balance_data(df, kind: str, target):
        if len(df[(df[target] == 0)]) >= df[(df[target] == 1)]:
            df_majority = df[(df[target] == 0)]
            df_minority = df[(df[target] == 1)]
        else:
            df_majority = df[(df[target] == 1)]
            df_minority = df[(df[target] == 0)]

        if kind == 'UnderSampling':
            df_majority_undersampled = resample(df_majority,
                                                    replace=True,
                                                    n_samples=len(df_minority),
                                                    random_state=42)

            return pd.concat([df_majority_undersampled, df_minority])

        elif kind == 'UpSampling':
            df_minority_upsampled = resample(df_minority,
                                                 replace=True,
                                                 n_samples=len(df_majority),
                                                 random_state=42)
            return pd.concat([df_minority_upsampled, df_majority])

        elif kind == 'Smote':
            sm = SMOTE(sampling_strategy='minority', random_state=42)
            oversampled_X, oversampled_Y = sm.fit_sample(df.drop(target, axis=1), df[target])
            oversampled = pd.concat([pd.DataFrame(oversampled_Y), pd.DataFrame(oversampled_X)], axis=1)
            return oversampled
        else:
            return 'Please specify correct mtd'

    def drop_duplicate(self, df, cols: list):
        df = df.drop_duplicates(subset=cols, inplace=True)
        return df

    #https://www.analyticsvidhya.com/blog/2021/04/beginners-guide-to-low-variance-filter-and-its-implementation/
    def handle_low_variance(self, df, var_range):
        Categorical_columns = df.select_dtypes(include='object')
        df = df.drop(Categorical_columns, axis=1, inplace=True)
        normalize_df = normalize(df)
        df_scaled = pd.DataFrame(normalize_df)
        variance = df_scaled.var()
        cols = df.columns
        variable = []
        for i in range(0, len(variance)):
            if variance[i] >= var_range:
                variable.append(cols[i])
        new_df = df[variable]
        return new_df

    def handle_high_variance(self,df, var_range):
        Categorical_columns = df.select_dtypes(include='object')
        df = df.drop(Categorical_columns, axis=1, inplace=True)
        normalize_df = normalize(df)
        df_scaled = pd.DataFrame(normalize_df)
        variance = df_scaled.var()
        cols = df.columns
        variable = []
        for i in range(0, len(variance)):
            if variance[i] <= var_range:
                variable.append(cols[i])
        new_df = df[variable]
        return new_df