SCREENSHOT YANG WAJIB DILAMPIRKAN (tidak bisa di-generate otomatis):

1. screenshoot_dashboard.jpg
   - Buka http://127.0.0.1:5000, tangkap halaman daftar run/experiment MLflow
     yang menampilkan metriks (accuracy, f1, dll) dari run Anda.

2. screenshoot_artifak.jpg
   - Buka salah satu run -> tab "Artifacts", tangkap layar yang menampilkan
     model + artefak tambahan (confusion_matrix.png, classification_report.json,
     feature_importance.csv).

Langkah:
  pip install -r requirements.txt
  mlflow ui --host 127.0.0.1 --port 5000     (terminal 1)
  python modelling.py                         (terminal 2, autolog)
  python modelling_tuning.py                  (tuning + manual logging + artefak)

Simpan kedua screenshot di folder ini dengan nama persis di atas (.jpg).
