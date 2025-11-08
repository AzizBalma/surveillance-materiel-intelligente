# scripts/ml/predictor.py
import os
import joblib
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FEATURES = ["cpu_util","mem_util","temp_cpu","net_in_bytes","net_out_bytes","tcp_conn","user_active","usb_event"]

class Predictor:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or os.path.join(ROOT, "models", "ml")
        self.scaler = self._load("scaler.joblib")
        self.kmeans = self._load("kmeans.joblib")
        self.iforest = self._load("iforest.joblib")
        self.classifier = self._load("classifier.joblib")

    def _load(self, fname):
        p = os.path.join(self.model_dir, fname)
        return joblib.load(p) if os.path.exists(p) else None

    def _to_df(self, x):
        """Convertit dict ou DataFrame en DataFrame aligné avec FEATURES (ordre et noms garantis)."""
        if isinstance(x, dict):
            clean = {}
            for f in FEATURES:
                v = x.get(f, 0.0)
                if isinstance(v, str):
                    v_l = v.lower()
                    if v_l in ("oui","yes","true","1"):
                        v = 1.0
                    elif v_l in ("non","no","false","0"):
                        v = 0.0
                try:
                    v = float(v)
                except Exception:
                    v = 0.0
                clean[f] = v
            df = pd.DataFrame([clean], columns=FEATURES)
            return df
        elif isinstance(x, pd.DataFrame):
            df = x.copy()
            # add missing
            for f in FEATURES:
                if f not in df.columns:
                    df[f] = 0.0
            # keep only features in the correct order
            df = df[FEATURES]
            # coerce to numeric
            df = df.apply(pd.to_numeric, errors='coerce').fillna(0.0)
            return df
        else:
            raise ValueError("Input must be dict or pandas.DataFrame")

    def score(self, x):
        """
        x: dict or pd.DataFrame
        returns dict with keys:
            kmeans_cluster, iforest_score, iforest_anomaly, classifier_pred, classifier_proba
        """
        df = self._to_df(x)  # **keep as DataFrame** -> avoids scaler warning
        # Use DataFrame for scaler.transform to preserve feature names association
        if self.scaler:
            try:
                Xs = self.scaler.transform(df)  # pass DataFrame (sklearn accepts it)
            except Exception:
                # fallback to numpy if scaler older version; but keep columns order
                Xs = self.scaler.transform(df.values)
        else:
            Xs = df.values

        res = {}
        if self.kmeans:
            try:
                res['kmeans_cluster'] = int(self.kmeans.predict(Xs)[0])
            except Exception:
                pass
        if self.iforest:
            try:
                score = float(self.iforest.decision_function(Xs)[0])
                is_anom = bool(self.iforest.predict(Xs)[0] == -1)
                res['iforest_score'] = score
                res['iforest_anomaly'] = is_anom
            except Exception:
                pass
        if self.classifier:
            try:
                pred = self.classifier.predict(Xs)[0]
                res['classifier_pred'] = int(pred)
                try:
                    res['classifier_proba'] = self.classifier.predict_proba(Xs)[0].tolist()
                except Exception:
                    res['classifier_proba'] = []
            except Exception:
                pass
        return res

