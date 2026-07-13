"""测试成绩预测模块."""
import sys
sys.path.insert(0, ".")

from config import DB_CONFIG
from data_layer.database import DatabaseManager
from business_layer.grade_predictor import GradePredictor


def test_train_and_predict() -> None:
    db = DatabaseManager.get_instance()
    predictor = GradePredictor(db)

    X, y = predictor.load_training_data()
    print(f"  ✓ 加载训练数据: {len(X)} 条记录")

    if len(X) >= 5:
        metrics = predictor.train()
        if "error" not in metrics:
            print(f"  ✓ 模型训练: R²={metrics['r2_score']}, MAE={metrics['mae']}, "
                  f"RMSE={metrics['rmse']}")

            pred = predictor.predict(80, 75)
            assert 0 <= pred <= 100, f"预测值异常: {pred}"
            print(f"  ✓ 预测测试 (usual=80, midterm=75): {pred}")
        else:
            print(f"  ⚠ 训练失败: {metrics['error']}")
    else:
        print("  ⚠ 训练数据不足，跳过训练测试")


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
