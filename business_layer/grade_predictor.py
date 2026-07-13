"""成绩预测模块 - 基于 LinearRegression 预测期末成绩."""
import pickle
from typing import Optional

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import StudentCourseDAO
from utils.helpers import clamp


class GradePredictor:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._dao = StudentCourseDAO(db)
        self._model: Optional[LinearRegression] = None
        self._scaler: Optional[StandardScaler] = None
        self._is_trained = False

    def load_training_data(self) -> tuple[np.ndarray, np.ndarray]:
        df = self._dao.get_training_data()
        if df.empty:
            return np.array([]), np.array([])
        X = df[["usual_score", "midterm_score"]].values
        y = df["final_score"].values
        return X, y

    def train(self) -> dict:
        X, y = self.load_training_data()
        if len(X) < 5:
            return {"error": "训练数据不足（需要至少5条记录）"}

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        self._model = LinearRegression()
        self._model.fit(X_train, y_train)
        self._is_trained = True

        y_pred = self._model.predict(X_test)
        return {
            "r2_score": round(r2_score(y_test, y_pred), 4),
            "mae": round(mean_absolute_error(y_test, y_pred), 2),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "samples": len(X),
        }

    def predict(self, usual_score: float, midterm_score: float) -> float:
        if not self._is_trained:
            raise RuntimeError("模型尚未训练，请先调用 train()")
        X = np.array([[usual_score, midterm_score]])
        X_scaled = self._scaler.transform(X)
        pred = self._model.predict(X_scaled)[0]
        return round(clamp(pred, 0.0, 100.0), 1)

    def save_model(self, filepath: str) -> None:
        with open(filepath, "wb") as f:
            pickle.dump({"model": self._model, "scaler": self._scaler}, f)

    def load_model(self, filepath: str) -> None:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        self._model = data["model"]
        self._scaler = data["scaler"]
        self._is_trained = True
