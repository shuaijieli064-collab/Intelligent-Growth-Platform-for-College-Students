"""数据处理工具类 - 数据聚合、特征工程、趋势分析."""
import pandas as pd
import numpy as np
from typing import Optional


class DataProcessor:
    @staticmethod
    def aggregate_study_hours(records: list[dict], freq: str = "W") -> pd.DataFrame:
        if not records:
            return pd.DataFrame(columns=["period", "total_hours", "avg_focus"])
        df = pd.DataFrame(records)
        df["study_date"] = pd.to_datetime(df["study_date"])
        df = df.set_index("study_date")
        result = df.resample(freq).agg(
            total_hours=("study_hours", "sum"),
            avg_focus=("focus_score", "mean"),
        ).reset_index()
        result.columns = ["period", "total_hours", "avg_focus"]
        return result

    @staticmethod
    def compute_score_trend(scores: list[dict]) -> dict[str, list]:
        if not scores:
            return {"dates": [], "values": []}
        df = pd.DataFrame(scores)
        if "assessment_date" in df.columns:
            df = df.sort_values("assessment_date")
            return {
                "dates": df["assessment_date"].astype(str).tolist(),
                "values": df["overall_health"].tolist(),
                "academic": df["academic_score"].tolist(),
                "physical": df["physical_score"].tolist(),
                "mental": df["mental_score"].tolist(),
                "social": df["social_score"].tolist(),
            }
        return {"dates": [], "values": []}

    @staticmethod
    def prepare_ml_features(df: pd.DataFrame,
                            feature_cols: list[str]) -> np.ndarray:
        return df[feature_cols].values

    @staticmethod
    def normalize_scores(values: list[float]) -> list[float]:
        if not values or max(values) == min(values):
            return [50.0 for _ in values] if values else []
        vmin, vmax = min(values), max(values)
        return [(v - vmin) / (vmax - vmin) * 100 for v in values]

    @staticmethod
    def rolling_average(data: list[float], window: int = 7) -> list[float]:
        if len(data) < window:
            return list(data)
        series = pd.Series(data)
        return series.rolling(window=window, min_periods=1).mean().tolist()

    @staticmethod
    def safe_mean(values: list, default: float = 0.0) -> float:
        return float(np.mean(values)) if values else default

    @staticmethod
    def safe_max(values: list, default: float = 0.0) -> float:
        return float(np.max(values)) if values else default

    @staticmethod
    def safe_min(values: list, default: float = 0.0) -> float:
        return float(np.min(values)) if values else default
