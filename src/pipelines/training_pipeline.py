from sklearn.base import RegressorMixin
#import logging
import pandas as pd
import numpy as np
import mlflow
import os
import joblib
import optuna
from catboost import CatBoostRegressor
from urllib.parse import urlparse
import sys
#--------- Custom packages
from src.components.data_ingestion import DataIngestion
from src.components.preprocessor import Preprocessor, DataSpliter
from src.components.model_evaluation import Evaluation
from src.components.hyp_optimizer import Hyperparameter_Optimization
from src.components.reports import run_data_integrity_report,run_validation_train_test_split_report, run_validate_model_performance
from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

#************** START THE TRAINING PIPELINE  *******************

# -------------------- DATA INGESTION STEP 

def ingest_data() -> pd.DataFrame:
    """
    Args: None
    Returns: df: pd.DataFrame
    """
    try:
        obj = DataIngestion()
        df_path = obj.initiate_data_ingestion()

        data_report_path = run_data_integrity_report(df_path)
        if data_report_path:
            mlflow.log_artifact(data_report_path)

        return df_path
    
    except Exception as e:
            raise CustomException(e, sys)
        

  # --------------------DATA CLEANING SETP


def transform_data(df_path):
    """ Es una clase que preprocesa y divide los datos """
    try:
        
        # data preprocessing
        preprocessor = Preprocessor()
        df_proc = preprocessor.preprocess_dataframe(df_path)

        # data split
        data_spliter = DataSpliter()
        X_train, X_test, y_train, y_test = data_spliter.divide_data(df_proc)
        
        train_report_path = run_validation_train_test_split_report(X_train, y_train, X_test, y_test)
        if train_report_path:
            mlflow.log_artifact(train_report_path)

        return X_train, X_test, y_train, y_test
    
    except Exception as e:
        logging.error(e)
        raise CustomException(e, sys)

#-------------------------- MODEL TRAINING STEP


def train_model(
    X_train : pd.DataFrame,
    X_test : pd.DataFrame,
    y_train : pd.Series,
    y_test : pd.Series
):
    try:

        categorical_columns = X_train.select_dtypes(include=['object']).columns
        cat_feature_indices = [X_train.columns.get_loc(col) for col in categorical_columns]

        hy_opt = Hyperparameter_Optimization(X_train, y_train, X_test, y_test)
        study = optuna.create_study(direction = "maximize")
        study.optimize(hy_opt.optimize_catboost_regressor, n_trials = 30)
        trial = study.best_trial

        n_estimators = trial.params["n_estimators"]
        mlflow.log_param('n_estimators', n_estimators)

        learning_rate = trial.params["learning_rate"]
        mlflow.log_param('learning_rate', learning_rate)

        max_depth = trial.params["max_depth"]
        mlflow.log_param('max_depth', max_depth)

        model = CatBoostRegressor(
                n_estimators = n_estimators,
                learning_rate = learning_rate,
                max_depth = max_depth,
                cat_features = cat_feature_indices
                )
            
        model.fit(X_train, y_train)
            
        trained_model_file_path = os.path.join("api_artifacts", "model.pkl")
        save_object(
                file_path = trained_model_file_path,
                obj = model
            )

        # Registro del modelo en MLflow
        mlflow.log_artifact(trained_model_file_path)

        #model validation
        model_performance_report_path = run_validate_model_performance(X_train, y_train, X_test, y_test, model)
        if model_performance_report_path:
            mlflow.log_artifact(model_performance_report_path)

        return model
        
    except Exception as e:
        logging.error(e)
        raise CustomException(e, sys)

#--------------------- MODEL EVALUATION STEP


def evaluation(model: RegressorMixin, X_test: pd.DataFrame, y_test: pd.Series):
    
    "Args: model, x_test, y_test  and Returns: r2_score and rmse"

    try:
        prediction = model.predict(X_test)
        evaluation = Evaluation()

        r2_score = evaluation.r2_score(y_test, prediction)
        mlflow.log_metric("r2_score", r2_score)

        mse = evaluation.mean_squared_error(y_test, prediction)
        mlflow.log_metric("mse", mse)

        rmse = evaluation.root_mean_squared_error(y_test, prediction)  # Passing y_true and y_pred
        mlflow.log_metric("rmse", rmse)

        return mse, rmse
    
    except Exception as e:
        logging.error(e)
        raise CustomException(e, sys)

#- ------------------------- TRAINING PIPELINE

def train_pipeline():

    experiment_name = "Training Pipeline for Catboost Model"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name = "Catboost Model Tracking"):
        df_path = ingest_data()
        X_train, X_test, y_train, y_test = transform_data(df_path)
        model = train_model(X_train, X_test, y_train, y_test)
        mse, rmse = evaluation(model, X_test, y_test)
        print(mse)
        print(rmse)


if __name__ == "__main__":
 train_pipeline()