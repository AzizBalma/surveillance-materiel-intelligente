# app/scripts/trainer/train_supervised.py
import os
import glob
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

from config.paths import *


DATA_PATH = "data/network-traffic-dataset-main/data/reduced/flows"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

# 1) collect CSVs
files = glob.glob(os.path.join(DATA_PATH, "**", "*.csv"), recursive=True)
if len(files) == 0:
    raise FileNotFoundError(f"Aucun CSV trouvé sous {DATA_PATH}")
df_list = [pd.read_csv(f) for f in files]
df = pd.concat(df_list, ignore_index=True)
print(f"Dataset: {df.shape}")

# 2) cleanup cols (adjust if truncated)
cols_to_drop = ['sAddress','rAddress','sMACs','rMACs','sIPs','rIPs','startDate','endDate','start']
df_clean = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

# target exists?
target_col = 'IT_M_Label'
if target_col not in df_clean.columns:
    raise ValueError("Colonne target 'IT_M_Label' introuvable")

X = df_clean.drop(columns=[target_col])
y = df_clean[target_col]

# encode target
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
print("Classes:", list(encoder.classes_))

# numeric features
numeric_features = X.select_dtypes(include=[np.number]).columns
X_numeric = X[numeric_features].copy()

# fill NA
for c in X_numeric.columns:
    X_numeric[c] = X_numeric[c].fillna(X_numeric[c].median())

# variance threshold
vt = VarianceThreshold()
X_f = vt.fit_transform(X_numeric)
selected_features = numeric_features[vt.get_support()]
print(f"Selected numeric features: {len(selected_features)}")

# scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_f)

# split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
print("Train/Test shapes:", X_train.shape, X_test.shape)

# model
model = GradientBoostingClassifier(n_estimators=300, learning_rate=0.1, max_depth=6, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
cv = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')

print("Accuracy:", acc)
print("F1 weighted:", f1)
print("CV mean:", cv.mean())
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

# save
joblib.dump(model, os.path.join(MODEL_DIR, "best_model_gradient_boosting_multiclass5.joblib"))
joblib.dump(encoder, os.path.join(MODEL_DIR, "label_encoder_multiclass5.joblib"))
joblib.dump(vt, os.path.join(MODEL_DIR, "variance_selector_multiclass5.joblib"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler_multiclass5.joblib"))
joblib.dump(list(selected_features), os.path.join(MODEL_DIR, "selected_features_multiclass5.joblib"))

print("Saved models to models/")
