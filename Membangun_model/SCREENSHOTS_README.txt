SCREENSHOT YANG WAJIB DILAMPIRKAN (tidak bisa di-generate otomatis):

PENTING: Jalankan SEMUA perintah dengan venv .venv-k2 (mlflow==2.19.0).
Dengan MLflow 3.x folder "model" TIDAK muncul di tab Artifacts run
(penyebab penolakan review sebelumnya).

Aktifkan venv di setiap terminal baru:
  E:\Code\d\mach\.venv-k2\Scripts\activate
  cd E:\Code\d\mach\SMSML_Epafraditus-Memoriano\Membangun_model

Run yang sudah tercatat (mlflow 2.19.0, siap di-screenshot):
  - telco_churn_basic  / rf_autolog            run_id: f863de3cf2ca492289380d1987f8364c
  - telco_churn_tuning / rf_gridsearch_manual  run_id: f3d09d046e174e288b94129d87d969f2

--- KRITERIA 2 ---

0. Pastikan MLflow UI jalan (terminal 1):
     mlflow ui --host 127.0.0.1 --port 5000

1. screenshoot_dashboard.jpg
   - Buka http://127.0.0.1:5000, tangkap halaman daftar run/experiment
     yang menampilkan metriks (accuracy, f1, dll).

2. screenshoot_artifak.jpg
   - Buka run rf_autolog -> tab "Artifacts".
   - WAJIB terlihat folder "model" ter-expand berisi: MLmodel, conda.yaml,
     model.pkl, python_env.yaml, requirements.txt (klik segitiga di samping
     "model" agar isinya kelihatan).

--- KRITERIA 4 (bukti serving, folder "1.bukti_serving") ---

3. Screenshot TERMINAL yang menjalankan mlflow models serve (terminal 2):
     set MLFLOW_TRACKING_URI=http://127.0.0.1:5000
     mlflow models serve -m "runs:/f863de3cf2ca492289380d1987f8364c/model" --port 5002 --env-manager local
   - Tunggu sampai muncul "Serving on http://127.0.0.1:5002".
   - Tangkap seluruh jendela terminal (perintah + log serving harus terbaca).
   - Opsional tapi bagus: di terminal lain kirim request lalu screenshot juga:
     python -c "import pandas as pd, requests; df = pd.read_csv('telco_churn_preprocessing/test.csv').drop(columns=['Churn']).head(3); print(requests.post('http://127.0.0.1:5002/invocations', json={'dataframe_split': df.to_dict(orient='split')}).text)"
     (hasil terverifikasi: {"predictions": [0, 0, 0]})

Simpan screenshot Kriteria 2 di folder ini dengan nama persis di atas (.jpg).
