import json
import joblib
import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "winequality-red.csv")

def main():
    df = pd.read_csv(DATA_PATH, sep=";")

    X = df.drop("quality", axis=1)
    y = df["quality"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    joblib.dump(model, "model.pkl")

    metrics = {
        "r2": float(r2),
        "mse": float(mse),
        "accuracy": float(r2)  # for Jenkins
    }

    # 1️⃣ Save for GitHub Actions (Lab 4)
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    with open("results.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # 2️⃣ Save for Jenkins (Lab 6)
    os.makedirs("app/artifacts", exist_ok=True)

    with open("app/artifacts/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Saved model and metrics")
    print(metrics)

if __name__ == "__main__":
    main()