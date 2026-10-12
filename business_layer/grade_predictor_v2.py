"""成绩预测 2.0 - 置信区间 + XGBoost 选项."""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import StudentCourseDAO
from utils.helpers import clamp


class GradePredictorV2:
    def __init__(self, db: DatabaseManager) -> None:
        self._dao = StudentCourseDAO(db)
        self._model = None
        self._scaler = StandardScaler()
        self._is_trained = False
        self._cv_scores: list[float] = []
        self._use_xgboost = False
        self._course_id: int | None = None

    def train(self, course_id: int | None = None, use_xgboost: bool = False) -> dict:
        self._use_xgboost = use_xgboost
        self._course_id = course_id
        df = self._dao.get_training_data(course_id)
        if df.empty or len(df) < 3:
            self._is_trained = False
            return {"error": f"该课程训练数据不足（需要至少3条完整成绩），当前只有{len(df)}条"}

        X = df[["usual_score", "midterm_score"]].values
        y = df["final_score"].values
        X_scaled = self._scaler.fit_transform(X)

        if use_xgboost:
            self._model = GradientBoostingRegressor(
                n_estimators=100, max_depth=3, random_state=42
            )
        else:
            self._model = LinearRegression()

        self._model.fit(X_scaled, y)
        self._is_trained = True

        self._cv_scores = list(cross_val_score(
            self._model, X_scaled, y, cv=min(5, len(X)), scoring="neg_mean_absolute_error"
        ))
        cv_mae = round(abs(np.mean(self._cv_scores)), 2)

        y_pred = self._model.predict(X_scaled)
        residuals = y - y_pred
        self._residual_std = np.std(residuals)

        return {
            "samples": len(X), "cv_mae": cv_mae,
            "residual_std": round(self._residual_std, 2),
            "algorithm": "XGBoost" if use_xgboost else "LinearRegression",
        }

    def predict(self, usual: float, midterm: float) -> dict:
        if not self._is_trained:
            raise RuntimeError("模型未训练")
        X = np.array([[usual, midterm]])
        X_scaled = self._scaler.transform(X)
        point = self._model.predict(X_scaled)[0]

        # 残差标准差为 0（完全拟合）时用最小尺度，避免置信区间退化为 NaN
        std = float(getattr(self, "_residual_std", 5.0) or 0.0)
        scale = std if std > 1e-6 else 1.0

        # 95% 置信区间
        ci_lower = point - 1.96 * scale
        ci_upper = point + 1.96 * scale

        # 达标概率 (以60分为及格线)
        from scipy.stats import norm
        pass_prob = 1 - norm.cdf(60, loc=point, scale=scale)

        return {
            "predicted": round(clamp(point, 0, 100), 1),
            "ci_lower": round(max(0, ci_lower), 1),
            "ci_upper": round(min(100, ci_upper), 1),
            "pass_probability": round(pass_prob * 100, 1),
            "risk": "低风险" if pass_prob > 0.8 else "中风险" if pass_prob > 0.5 else "高风险",
        }
