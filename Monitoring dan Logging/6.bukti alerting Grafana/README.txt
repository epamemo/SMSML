Untuk Advance: 3 alerting. Setiap alert = 2 file (rules + notifikasi).

  1.rules_model_down.jpg          (konfigurasi alert rule: app_model_up == 0)
  2.notifikasi_model_down.jpg     (bukti alert Firing / notifikasi terkirim)
  3.rules_error_rate.jpg          (rate(app_prediction_errors_total[5m]) > 0)
  4.notifikasi_error_rate.jpg
  5.rules_latency_p95.jpg         (histogram_quantile p95 latency > 1s)
  6.notifikasi_latency_p95.jpg

Buat di Grafana -> Alerting -> Alert rules. Set contact point (mis. email/webhook)
agar notifikasi terlihat. Screenshot state "Firing" sebagai bukti notifikasi.
