import logging
import optuna
import pandas as pd
from catboost import CatBoostRegressor


class Hyperparameter_Optimization:

    """
    Class for doing hyperparameter optimization

    """

    def __init__(
        self, X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> None:
        """Initialize the class with the training and test data."""
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def optimize_catboost_regressor(self, trial: optuna.Trial) -> float:

        categorical_columns = self.X_train.select_dtypes(include=['object']).columns
        cat_feature_indices = [self.X_train.columns.get_loc(col) for col in categorical_columns]


        param = {
            "max_depth": trial.suggest_int("max_depth", 1, 15),
            "learning_rate": trial.suggest_loguniform("learning_rate", 1e-7, 5.0),
            "n_estimators": trial.suggest_int("n_estimators", 1, 200),
            "cat_features": cat_feature_indices
        }
        reg = CatBoostRegressor(**param)
        reg.fit(self.X_train, self.y_train)
        score = reg.score(self.X_test, self.y_test)

        return score