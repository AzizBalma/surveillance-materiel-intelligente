# anomaly_model.py
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import os

MODEL_DIR = '/app/models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Colonnes pour le ML
FEATURES = ['cpu_util','mem_util','temp_cpu','net_in_bytes','net_out_bytes','tcp_conn','user_active','usb_event']

# Charger les données collectées
df = pd.read_csv('../data/donnees_ml.csv')

# Préparer les features
X = df[FEATURES].fillna(0)

# Standardisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Isolation Forest pour anomalies
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_scaled)

# Sauvegarde
joblib.dump(model, os.path.join(MODEL_DIR,'if_model.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR,'scaler.pkl'))

print("✅ Modèle entraîné et sauvegardé")
