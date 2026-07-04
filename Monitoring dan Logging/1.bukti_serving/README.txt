Bukti serving = screenshot TERMINAL yang menjalankan `mlflow models serve`
(BUKAN halaman browser /metrics — itu penyebab penolakan review sebelumnya).

Cara mengambil (terminal baru, perintah sudah terverifikasi jalan):

  1) Pastikan MLflow UI aktif di terminal lain:
       E:\Code\d\mach\.venv-k2\Scripts\activate
       cd E:\Code\d\mach\SMSML_Epafraditus-Memoriano\Membangun_model
       mlflow ui --host 127.0.0.1 --port 5000

  2) Di terminal baru:
       E:\Code\d\mach\.venv-k2\Scripts\activate
       cd E:\Code\d\mach\SMSML_Epafraditus-Memoriano\Membangun_model
       set MLFLOW_TRACKING_URI=http://127.0.0.1:5000
       mlflow models serve -m "runs:/f863de3cf2ca492289380d1987f8364c/model" --port 5002 --env-manager local

  3) Tunggu baris "Serving on http://127.0.0.1:5002" muncul, lalu screenshot
     SELURUH jendela terminal (perintah + log harus terbaca).
     Simpan di folder ini, misal: serving_mlflow.jpg

  4) (Opsional, memperkuat bukti) Terminal ketiga — kirim request lalu
     screenshot respons prediksinya:
       E:\Code\d\mach\.venv-k2\Scripts\activate
       cd E:\Code\d\mach\SMSML_Epafraditus-Memoriano\Membangun_model
       python -c "import pandas as pd, requests; df = pd.read_csv('telco_churn_preprocessing/test.csv').drop(columns=['Churn']).head(3); print(requests.post('http://127.0.0.1:5002/invocations', json={'dataframe_split': df.to_dict(orient='split')}).text)"
     Hasil terverifikasi: {"predictions": [0, 0, 0]}
