import pandas as pd
import os
import sys
from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass
from src.components.preprocessor import  Preprocessor
#from

@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('artifacts', "raw_data.csv")


class DataIngestion:


    def __init__(self):
        self.ingestion_config= DataIngestionConfig()


    def initiate_data_ingestion(self):

        logging.info("Entered the data ingestion component")
        
        try:
            df = pd.read_csv('data/drugs_train.csv')

            def format_dtypes(df):
    
                 df['drug_id'] = df['drug_id'].astype(str)
                 df['description'] = df['description'].astype(str)
                 df['administrative_status'] = df['administrative_status'].astype(str)
                 df['approved_for_hospital_use'] = df['approved_for_hospital_use'].astype(str)
                 df['reimbursement_rate'] = df['reimbursement_rate'].astype(str)
                 df['dosage_form'] = df['dosage_form'].astype(str)
                 df['route_of_administration'] = df['route_of_administration'].astype(str)
                 df['marketing_authorization_status'] = df['marketing_authorization_status'].astype(str)
                 df['marketing_declaration_date'] = df['marketing_declaration_date'].astype(int)
                 df['marketing_authorization_date'] = df['marketing_authorization_date'].astype(int)
                 df['marketing_authorization_process'] = df['marketing_authorization_process'].astype(str)
                 df['pharmaceutical_companies'] = df['pharmaceutical_companies'].astype(str)
                 df['price'] = df['price'].astype(float)
              
                 return df
            
            df = format_dtypes(df)

            logging.info("Load the dataset as dataframe")
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok= True)
            df.to_csv(self.ingestion_config.raw_data_path, index = False, header= True)

            logging.info("Ingestion is completed")
            return(
                self.ingestion_config.raw_data_path
            )

        except Exception as e:
            raise CustomException(e, sys)

if __name__=="__main__":
    obj = DataIngestion()
    df_path = obj.initiate_data_ingestion()

    data_transformation = Preprocessor()
    train = data_transformation.preprocess_dataframe(df_path)
     