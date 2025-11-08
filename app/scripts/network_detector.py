# app/scripts/network_detector.py
import os
import joblib
import logging
import pandas as pd
from datetime import datetime

MODEL_BASE = "models"
MODEL_FILE = os.path.join(MODEL_BASE, "best_model_gradient_boosting_multiclass5.joblib")
ENC_FILE = os.path.join(MODEL_BASE, "label_encoder_multiclass5.joblib")
VAR_FILE = os.path.join(MODEL_BASE, "variance_selector_multiclass5.joblib")
SCL_FILE = os.path.join(MODEL_BASE, "scaler_multiclass5.joblib")
FEAT_FILE = os.path.join(MODEL_BASE, "selected_features_multiclass5.joblib")

class NetworkDetector:
    def __init__(self, alert_system=None):
        self.alert_system = alert_system
        self.model = None
        self.encoder = None
        self.variance_selector = None
        self.scaler = None
        self.selected_features = None
        self._load()

    def _load(self):
        if all(os.path.exists(p) for p in [MODEL_FILE, ENC_FILE, VAR_FILE, SCL_FILE, FEAT_FILE]):
            try:
                self.model = joblib.load(MODEL_FILE)
                self.encoder = joblib.load(ENC_FILE)
                self.variance_selector = joblib.load(VAR_FILE)
                self.scaler = joblib.load(SCL_FILE)
                self.selected_features = joblib.load(FEAT_FILE)
                logging.info("Modèle réseau chargé.")
            except Exception as e:
                logging.error(f"Erreur chargement modèle réseau: {e}")
        else:
            logging.warning("Modèle réseau manquant; réseau désactivé.")

    def preprocess(self, df: pd.DataFrame):
        try:
            df2 = df.copy()
            cols_to_drop = ['sAddress','rAddress','sMACs','rMACs','sIPs','rIPs','startDate','endDate','start']
            df2 = df2.drop(columns=[c for c in cols_to_drop if c in df2.columns], errors='ignore')
            numeric_cols = df2.select_dtypes(include=['number']).columns
            for c in numeric_cols:
                df2[c] = df2[c].fillna(df2[c].median())
            expected = self.variance_selector.feature_names_in_
            for c in expected:
                if c not in df2.columns:
                    df2[c] = 0
            X = df2[expected]
            Xf = self.variance_selector.transform(X)
            Xs = self.scaler.transform(Xf)
            return Xs
        except Exception as e:
            logging.error(f"Erreur préprocess network: {e}")
            return None

    def detect(self, df: pd.DataFrame):
        if self.model is None:
            return []
        X = self.preprocess(df)
        if X is None:
            return []
        preds = self.model.predict(X)
        labels = self.encoder.inverse_transform(preds)
        anomalies = []
        for i, lbl in enumerate(labels):
            if lbl != "Normal":
                anomaly = {"index": i, "label": lbl, "timestamp": datetime.utcnow().isoformat()}
                anomalies.append(anomaly)
                if self.alert_system:
                    self.alert_system.send_alert(f"Intrusion réseau: {lbl}", "network_intrusion", anomaly)
        return anomalies
