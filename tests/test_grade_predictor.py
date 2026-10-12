"""测试成绩预测模块."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.grade_predictor_v2 import GradePredictorV2


def test_train_and_predict() -> None:
    db = DatabaseManager.get_instance()
    predictor = GradePredictorV2(db)

    metrics = predictor.train()
    if "error" in metrics:
        print(f"  ⚠ 训练数据不足: {metrics['error']}")
        return

    print(f"  ✓ 模型训练: 样本={metrics['samples']}, CV-MAE={metrics['cv_mae']}, "
          f"算法={metrics['algorithm']}")

    pred = predictor.predict(80, 75)
    point = pred["predicted"]
    assert 0 <= point <= 100, f"预测值异常: {point}"
    assert 0 <= pred["pass_probability"] <= 100, f"及格概率异常: {pred['pass_probability']}"
    assert pred["ci_lower"] <= point <= pred["ci_upper"], f"置信区间异常: {pred}"
    print(f"  ✓ 预测测试 (usual=80, midterm=75): {point} "
          f"CI=[{pred['ci_lower']}, {pred['ci_upper']}] 及格概率={pred['pass_probability']}%")


def main() -> None:
    print("成绩预测模块测试:")
    test_train_and_predict()
    print("\n✅ 成绩预测模块测试通过")


if __name__ == "__main__":
    DatabaseManager(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"], charset=DB_CONFIG.get("charset", "utf8mb4"),
    )
    main()
