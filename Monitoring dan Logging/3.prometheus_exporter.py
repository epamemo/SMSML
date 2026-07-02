"""Prometheus exporter untuk model serving (Kriteria 4 - Advance).

Bertindak sebagai proxy di depan model MLflow yang di-serve (default
http://127.0.0.1:8080/invocations) DAN mengekspos >=10 metriks Prometheus di
/metrics (port 8000).

Alur:
    [inference.py] -> POST /predict (8000) -> proxy ke MLflow serve (8080) -> hasil
    Prometheus scrape http://127.0.0.1:8000/metrics

Jalankan:
    # 1) serve model (dari Docker image K3, atau mlflow models serve)
    docker run -p 8080:8080 epamemo/telco-churn-ci:latest
    # 2) exporter
    python 3.prometheus_exporter.py
"""
import os
import time

import requests
from flask import Flask, Response, request, jsonify
from prometheus_client import (Counter, Gauge, Histogram, Summary, Info,
                               generate_latest, CONTENT_TYPE_LATEST)

MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT", "http://127.0.0.1:8080/invocations")
app = Flask(__name__)

# ---- 10+ metriks berbeda ----
REQUESTS_TOTAL = Counter("app_requests_total", "Total request masuk", ["endpoint", "http_status"])
PREDICTIONS_TOTAL = Counter("app_predictions_total", "Total prediksi per kelas", ["predicted_class"])
PREDICTION_ERRORS = Counter("app_prediction_errors_total", "Total error saat inferensi")
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Latensi request end-to-end (detik)")
INFERENCE_LATENCY = Histogram("app_inference_latency_seconds", "Latensi panggilan model (detik)")
REQUEST_SIZE = Summary("app_request_payload_bytes", "Ukuran payload request (byte)")
IN_PROGRESS = Gauge("app_requests_in_progress", "Jumlah request yang sedang diproses")
LAST_PREDICTION = Gauge("app_last_prediction", "Nilai prediksi terakhir")
LAST_LATENCY = Gauge("app_last_latency_seconds", "Latensi request terakhir (detik)")
MODEL_UP = Gauge("app_model_up", "1 jika model endpoint sehat, 0 jika tidak")
THROUGHPUT = Counter("app_predictions_served_total", "Total prediksi berhasil dilayani")
APP_INFO = Info("app_build", "Info aplikasi exporter")
APP_INFO.info({"model_endpoint": MODEL_ENDPOINT, "owner": "epamemo", "version": "1.0"})


def _check_model():
    try:
        # MLflow scoring server merespons GET /ping (200 jika sehat)
        base = MODEL_ENDPOINT.rsplit("/", 1)[0]
        r = requests.get(f"{base}/ping", timeout=2)
        MODEL_UP.set(1 if r.status_code == 200 else 0)
    except Exception:
        MODEL_UP.set(0)


@app.route("/metrics")
def metrics():
    _check_model()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/predict", methods=["POST"])
def predict():
    IN_PROGRESS.inc()
    start = time.time()
    status = "200"
    try:
        payload = request.get_data()
        REQUEST_SIZE.observe(len(payload))

        t0 = time.time()
        resp = requests.post(
            MODEL_ENDPOINT, data=payload,
            headers={"Content-Type": "application/json"}, timeout=10,
        )
        INFERENCE_LATENCY.observe(time.time() - t0)
        resp.raise_for_status()

        result = resp.json()
        preds = result.get("predictions", result)
        if isinstance(preds, list) and preds:
            pred = preds[0]
            LAST_PREDICTION.set(float(pred))
            PREDICTIONS_TOTAL.labels(predicted_class=str(int(pred))).inc()
            THROUGHPUT.inc()
        return jsonify(result)
    except Exception as e:
        status = "500"
        PREDICTION_ERRORS.inc()
        return jsonify(error=str(e)), 500
    finally:
        elapsed = time.time() - start
        REQUEST_LATENCY.observe(elapsed)
        LAST_LATENCY.set(elapsed)
        REQUESTS_TOTAL.labels(endpoint="/predict", http_status=status).inc()
        IN_PROGRESS.dec()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
