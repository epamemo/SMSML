"""Client inferensi (Kriteria 4): kirim data uji ke exporter untuk membangkitkan
traffic sehingga metriks Prometheus/Grafana terisi.

Kirim ke exporter (yang mem-proxy ke model + mencatat metriks):
    python 7.inference.py --n 50

Atau langsung ke MLflow serve:
    python 7.inference.py --url http://127.0.0.1:8080/invocations
"""
import argparse
import time

import pandas as pd
import requests

DATA = "telco_churn_preprocessing/test.csv"
TARGET = "Churn"


def main(url, n, delay):
    df = pd.read_csv(DATA).drop(columns=[TARGET])
    cols = list(df.columns)
    ok = err = 0
    for i in range(n):
        row = df.iloc[[i % len(df)]]
        payload = {"dataframe_split": {"columns": cols, "data": row.values.tolist()}}
        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            ok += 1
            if i < 5:
                print(f"[{i}] -> {r.json()}")
        except Exception as e:
            err += 1
            print(f"[{i}] ERROR: {e}")
        time.sleep(delay)
    print(f"Done. success={ok} error={err}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/predict",
                    help="endpoint exporter (/predict) atau MLflow (/invocations)")
    ap.add_argument("--n", type=int, default=50, help="jumlah request")
    ap.add_argument("--delay", type=float, default=0.2, help="jeda antar request (detik)")
    a = ap.parse_args()
    main(a.url, a.n, a.delay)
