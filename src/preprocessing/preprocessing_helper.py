import pandas as pd
import numpy as np
import category_encoders as ce
import seaborn as sns
from sklearn.preprocessing import normalize
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN, RandomOverSampler, SMOTENC, SVMSMOTE
from imblearn.under_sampling import TomekLinks, NearMiss, RandomUnderSampler

class Preprocessing():

    @staticmethod
    def get_data(filepath):
        try:
            data = filepath
            df = pd.read_csv(data)
            return df
        except Exception as e:
            return e
        
    @staticmethod
    def col_seperator(df, typ: str):
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
        
    @staticmethod
    def delete_col(df, cols:list):

        temp_list = []
        for i in cols:
            if i in df.columns:
                temp_list.append(i)
            else:
                return 'Column Not Found'

        try:
            df = df.drop(temp_list, axis=1)
            return df
        except Exception as e:
            return e
        
    @staticmethod
    def missing_values(df):
        try:
            columns = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False).index
            values = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False).values

            mv_df = pd.DataFrame(columns, columns=['Columns'])

            mv_df['Missing_Values'] = values
            mv_df['Percentage'] = np.round((values / len(df)) * 100, 2)

            return columns, values, mv_df

        except Exception as e:
            return e
        
    @staticmethod
    def fill_numerical(df, typ, cols):
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
        
    @staticmethod
    def fill_categorical(df, typ=None, col=None, value=None):
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
    @staticmethod
    def Unique(df, percent):
        percent = percent/25
        holder = []
        for column in df.columns:
            if df[column].nunique() > int(len(df) * percent / 4):
                print(column, '+', df[column].unique())
                holder.append(column)
        return holder

            

    #https://www.analyticsvidhya.com/blog/2020/08/types-of-categorical-data-encoding/
    @staticmethod
    def encodings(df, cols, kind: str):
        if kind == 'One Hot Encoder':
            onehot=ce.OneHotEncoder(cols=cols)
            onehot_df = onehot.fit_transform(df)
            return onehot_df
        elif kind == 'Dummy Encoder':
            dummy_df = pd.get_dummies(data=cols, drop_first=True)
            return dummy_df
        elif kind == 'Effective Encoder':
            target = ce.TargetEncoder(cols=cols)
            target_df = target.fit_transform(df)
            return target_df
        elif kind == 'Binary Encoder':
            binary = ce.BinaryEncoder(cols=cols,return_df=True)
            binary_df = binary.fit_transform(df)
            return binary_df
        elif kind == 'Base N Encoder':
            basen = ce.BaseNEncoder(cols=cols)
            basen_df = basen.fit_transform(df)
            return basen_df
        else:
            "Wrong Input!!"

    @staticmethod
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
    @staticmethod
    def drop_duplicate(df, cols: list):
        df = df.drop_duplicates(subset=cols, inplace=True)
        return df

    @staticmethod
    def handle_low_variance(df, var_range):
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
    
    @staticmethod
    def handle_high_variance(df, var_range):
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
    
    @staticmethod
    def under_sample(dataframe, target_col, ratio=None):
        X = dataframe.drop(columns=[target_col])
        y = dataframe[target_col]
        
        if ratio:
             ns=NearMiss(sampling_strategy=ratio)
             X_resampled, y_resampled = ns.fit_resample(X, y)
        else:  
            ns=NearMiss()
            X_resampled, y_resampled = ns.fit_resample(X, y)
        
        resampled_dataset = X_resampled.join(y_resampled)
            
        return resampled_dataset 
    
    @staticmethod
    def over_sample(dataframe, target_col, ratio=None):
    
        X = dataframe.drop(columns=[target_col])
        y = dataframe[target_col]
        
        if ratio:
                ros = RandomOverSampler(sampling_strategy=ratio)
                X_resampled, y_resampled = ros.fit_resample(X, y)
        else:  
            ros = RandomOverSampler()
            X_resampled, y_resampled = ros.fit_resample(X, y)
        
        resampled_dataset = X_resampled.join(y_resampled)
            
        return resampled_dataset 
    
    @staticmethod
    def smote_technique(dataframe, target_col, ratio=None):
    
        X = dataframe.drop(columns=[target_col])
        y = dataframe[target_col]
        
        if ratio:
            sm = SMOTE(sampling_strategy=ratio)
            X_resampled, y_resampled = sm.fit_resample(X, y)
        else:  
            sm = SMOTE()
            X_resampled, y_resampled = sm.fit_resample(X, y)
        
        resampled_dataset = X_resampled.join(y_resampled)
            
        return resampled_dataset 