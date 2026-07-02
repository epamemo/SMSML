"""Kriteria 2 - Basic: latih model dengan MLflow autolog (tracking lokal).

Jalankan MLflow UI lebih dulu di terminal terpisah:
    mlflow ui --host 127.0.0.1 --port 5000

lalu:
    python modelling.py
Buka http://127.0.0.1:5000 untuk melihat run + artefak.
"""
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

DATA = "telco_churn_preprocessing"
TARGET = "Churn"


def load():
    train = pd.read_csv(f"{DATA}/train.csv")
    test = pd.read_csv(f"{DATA}/test.csv")
    X_train, y_train = train.drop(columns=[TARGET]), train[TARGET]
    X_test, y_test = test.drop(columns=[TARGET]), test[TARGET]
    return X_train, X_test, y_train, y_test


def main():
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("telco_churn_basic")
    mlflow.sklearn.autolog()

    X_train, X_test, y_train, y_test = load()

    with mlflow.start_run(run_name="rf_autolog"):
        model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
        model.fit(X_train, y_train)
        acc = model.score(X_test, y_test)
        print(f"Test accuracy: {acc:.4f}")


if __name__ == "__main__":
    main()
