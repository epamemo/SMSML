# Monitoring dan Logging — Epafraditus Memoriano (Kriteria 4)

Serving model + monitoring dengan **Prometheus** & **Grafana**. Target: **Advance**
(≥10 metriks di Grafana, 3 alerting).

## Urutan menjalankan
```bash
pip install -r requirements.txt

# 1) SERVING model (pilih salah satu) -> bukti untuk folder 1.bukti_serving
docker run -p 8080:8080 epamemo/telco-churn-ci:latest      # image dari Kriteria 3
# atau: mlflow models serve -m runs:/<run_id>/model -p 8080 --env-manager local

# 2) Exporter (proxy + /metrics di :8000)
python 3.prometheus_exporter.py

# 3) Prometheus (native) memakai 2.prometheus.yml
prometheus --config.file=2.prometheus.yml
#    ATAU via docker:  docker compose up -d   (pakai prometheus-compose.yml + Grafana)

# 4) Bangkitkan traffic supaya metriks terisi
python 7.inference.py --n 100

# 5) Grafana: http://localhost:3000  (add data source Prometheus http://localhost:9090)
```

## Metriks yang diekspos (>=10, untuk Advance)
| # | Metrik | Tipe | Contoh query Grafana |
|---|--------|------|----------------------|
| 1 | `app_requests_total` | Counter | `rate(app_requests_total[1m])` |
| 2 | `app_predictions_total` | Counter (per kelas) | `sum by (predicted_class)(app_predictions_total)` |
| 3 | `app_prediction_errors_total` | Counter | `rate(app_prediction_errors_total[5m])` |
| 4 | `app_request_latency_seconds` | Histogram | `histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[5m]))` |
| 5 | `app_inference_latency_seconds` | Histogram | `histogram_quantile(0.95, rate(app_inference_latency_seconds_bucket[5m]))` |
| 6 | `app_request_payload_bytes` | Summary | `rate(app_request_payload_bytes_sum[5m])` |
| 7 | `app_requests_in_progress` | Gauge | `app_requests_in_progress` |
| 8 | `app_last_prediction` | Gauge | `app_last_prediction` |
| 9 | `app_last_latency_seconds` | Gauge | `app_last_latency_seconds` |
| 10 | `app_model_up` | Gauge | `app_model_up` |
| 11 | `app_predictions_served_total` | Counter | `rate(app_predictions_served_total[1m])` |
| + | `process_*`, `python_*` | default prometheus_client | `process_resident_memory_bytes` |

## 3 Alerting Grafana (Advance) — buat di Grafana → Alerting → Alert rules
1. **Model down** — `app_model_up == 0` selama 1m.
2. **Error rate tinggi** — `rate(app_prediction_errors_total[5m]) > 0`.
3. **Latensi p95 tinggi** — `histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[5m])) > 1`.

Untuk tiap alert simpan 2 screenshot ke `6.bukti alerting Grafana/`:
konfigurasi **rules** + bukti **notifikasi** (state Firing / pesan kontak).

## Beri nama dashboard = username Dicoding Anda (wajib terlihat di screenshot).
```
- [x] Basic  — serving + Prometheus (>=3 metrik) + Grafana metrik sama
- [x] Skilled — Grafana >=5 metrik + 1 alerting
- [x] Advance — Grafana >=10 metrik + 3 alerting
```
