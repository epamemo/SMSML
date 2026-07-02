"""Kriteria 2 - Skilled + Advance.

- Hyperparameter tuning (GridSearchCV).
- Manual logging (BUKAN autolog): params, metrics, dan model.
- Advance: tracking ONLINE via DagsHub + minimal 2 artefak tambahan
  (confusion matrix PNG, classification report JSON, feature importance CSV).

Set env var USE_DAGSHUB=1 untuk logging ke DagsHub (butuh MLFLOW_TRACKING_USERNAME
& MLFLOW_TRACKING_PASSWORD / token). Tanpa itu, logging jatuh ke MLflow lokal.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report, ConfusionMatrixDisplay)
from sklearn.model_selection import GridSearchCV

DATA = "telco_churn_preprocessing"
TARGET = "Churn"
DAGSHUB_OWNER = "epamemo"
DAGSHUB_REPO = "Sistem-Machine-Learning"


def setup_tracking():
    if os.getenv("USE_DAGSHUB") == "1":
        import dagshub
        dagshub.init(repo_owner=DAGSHUB_OWNER, repo_name=DAGSHUB_REPO, mlflow=True)
        print("Tracking -> DagsHub")
    else:
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        print("Tracking -> local MLflow (127.0.0.1:5000)")
    mlflow.set_experiment("telco_churn_tuning")


def load():
    train = pd.read_csv(f"{DATA}/train.csv")
    test = pd.read_csv(f"{DATA}/test.csv")
    return (train.drop(columns=[TARGET]), test.drop(columns=[TARGET]),
            train[TARGET], test[TARGET])


def main():
    setup_tracking()
    X_train, X_test, y_train, y_test = load()

    param_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth": [None, 8, 16],
        "min_samples_split": [2, 5],
    }
    grid = GridSearchCV(
        RandomForestClassifier(random_state=42, class_weight="balanced"),
        param_grid, cv=3, scoring="f1", n_jobs=-1,
    )

    with mlflow.start_run(run_name="rf_gridsearch_manual"):
        grid.fit(X_train, y_train)
        model = grid.best_estimator_
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        # --- manual logging: params ---
        for k, v in grid.best_params_.items():
            mlflow.log_param(k, v)
        mlflow.log_param("cv_folds", 3)

        # --- manual logging: metrics (setara autolog) ---
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "best_cv_f1": grid.best_score_,
        }
        mlflow.log_metrics(metrics)
        print(json.dumps(metrics, indent=2))

        # --- manual logging: model ---
        mlflow.sklearn.log_model(model, artifact_path="model")

        # --- Advance: artefak tambahan (>=2) ---
        os.makedirs("artifacts", exist_ok=True)

        # 1) confusion matrix PNG
        ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred)).plot()
        plt.title("Confusion Matrix")
        cm_path = "artifacts/confusion_matrix.png"
        plt.savefig(cm_path, bbox_inches="tight"); plt.close()
        mlflow.log_artifact(cm_path)

        # 2) classification report JSON
        report_path = "artifacts/classification_report.json"
        with open(report_path, "w") as f:
            json.dump(classification_report(y_test, y_pred, output_dict=True), f, indent=2)
        mlflow.log_artifact(report_path)

        # 3) feature importance CSV
        fi = pd.DataFrame({
            "feature": X_train.columns,
            "importance": model.feature_importances_,
        }).sort_values("importance", ascending=False)
        fi_path = "artifacts/feature_importance.csv"
        fi.to_csv(fi_path, index=False)
        mlflow.log_artifact(fi_path)

        print("Logged model + 3 extra artifacts.")


if __name__ == "__main__":
    main()
