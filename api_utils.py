
import sys
import os
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
from typing import Union
from sklearn.model_selection import train_test_split
from datetime import datetime
import pandas as pd
import numpy as np
import pickle
import logging


@dataclass
class DataTransformationConfig:
    pass

class PreprocessData:
   
    def impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:

        try:
            # numerical columns
            categorical_cols = df.select_dtypes(include='object').columns
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_cols] = categorical_imputer.fit_transform(df[categorical_cols])
            
            # categorical columns
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            numeric_imputer = SimpleImputer(strategy='mean')
            df[numeric_cols] = numeric_imputer.fit_transform(df[numeric_cols])
            
            return df
        
        except Exception as e:
            logging.error(e)
            raise e

    

class FeatureEngineering:

    def feature_enrichment(self, df: pd.DataFrame) -> pd.DataFrame:

        data_dir = os.path.join(os.path.dirname(__file__), 'api_artifacts')

        features_path = os.path.join(data_dir, 'drug_label_feature_eng.csv')
        routes_path = os.path.join(data_dir, 'global_route_admon.csv')
        additives_path = os.path.join(data_dir, 'final_drugs_label.csv')

        
        features = pd.read_csv(features_path)
        routes = pd.read_csv(routes_path)
        aditives = pd.read_csv(additives_path)
        
        merge1 = pd.merge(df, aditives, how='left', on='drug_id')
        merge2 = pd.merge(merge1, routes, how='left', on='route_of_administration')
        merge3 = pd.merge(merge2, features, how='left', on='description')
        
        return merge3
    
    def format_date(self, date_str):
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%Y-%m-%d')
    
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:

     
        class_frequencies = df['pharmaceutical_companies'].value_counts()
        cumulative_proportion = class_frequencies.cumsum() / class_frequencies.sum()
        labels = []
        
        for company in df['pharmaceutical_companies']:
            proportion = cumulative_proportion[company]
            if proportion <= 0.4:
                labels.append('share_40%')
            elif proportion <= 0.6:
                labels.append('share_60%')
            elif proportion <= 0.8:
                labels.append('share_80%')
            elif proportion <= 0.95:
                labels.append('share_95%')
            else:
                labels.append('share_100%')
                
        # Agregar las etiquetas al DataFrame
        df['pareto_companies'] = labels
        
        # Convertir formatos de fecha
        df['marketing_declaration_date'] = df['marketing_declaration_date'].astype(str)
        df['marketing_authorization_date'] = df['marketing_authorization_date'].astype(str)
    
        df['declaration_date'] = df['marketing_declaration_date'].apply(self.format_date)
        df['authorization_date'] = df['marketing_authorization_date'].apply(self.format_date)
    
         # Calcular la diferencia en años
        df['authorization_date'] = pd.to_datetime(df['authorization_date'])
        df['declaration_date'] = pd.to_datetime(df['declaration_date'])
    
        df['year_of_wait'] = (df['declaration_date'].dt.year - df['authorization_date'].dt.year)
    
        return df


    def normalize_numeric_features(self, df: pd.DataFrame) -> pd.DataFrame:

        try:
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            scaler = MinMaxScaler()
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            return df
        
        except Exception as e:
            logging.error(e)
            raise e
        

    def drop_columns(self, df: pd.DataFrame): # -> pd.DataFrame:
        try:
            df = df.drop(["authorization_date", "marketing_authorization_date",
                      "declaration_date", "marketing_declaration_date",
                      "pharmaceutical_companies", "dosage_form", "drug_id",
                      "description", "route_of_administration", "active_ingredients"], axis=1)
            return df
        
        except Exception as e:
            logging.error(e)
            raise e 


class Preprocessor(PreprocessData, FeatureEngineering):

    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def format_dtypes(self,df):
        df['drug_id'] = df['drug_id'].astype(str)
        df['description'] = df['description'].astype(str)
        df['administrative_status'] = df['administrative_status'].astype(str)
        df['marketing_status'] = df['marketing_status'].astype(str)
        df['approved_for_hospital_use'] = df['approved_for_hospital_use'].astype(str)
        df['reimbursement_rate'] = df['reimbursement_rate'].astype(str)
        df['dosage_form'] = df['dosage_form'].astype(str)
        df['route_of_administration'] = df['route_of_administration'].astype(str)
        df['marketing_authorization_status'] = df['marketing_authorization_status'].astype(str)
        df['marketing_declaration_date'] = df['marketing_declaration_date'].astype(int)
        df['marketing_authorization_date'] = df['marketing_authorization_date'].astype(int)
        df['marketing_authorization_process'] = df['marketing_authorization_process'].astype(str)
        df['pharmaceutical_companies'] = df['pharmaceutical_companies'].astype(str)
        
        return df

    def preprocess_dataframe(self, input_df):

        df = self.format_dtypes(input_df)
        enriched_df = self.feature_enrichment(df)
        engineered_df = self.feature_engineering(enriched_df)
        normalized_df = self.normalize_numeric_features(engineered_df)
        dropped_df = self.drop_columns(normalized_df)
        preprocessed_df = self.impute_missing_values(dropped_df)

        return preprocessed_df 



def load_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    
    except Exception as e:
        logging.error(e)
        raise e
    
