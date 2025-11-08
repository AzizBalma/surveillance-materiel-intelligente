# scripts/ml/train_models.py
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer
from yellowbrick.classifier import ClassificationReport

print("🚀 Début de l'entraînement des modèles ML...")

# --- Définition correcte des chemins relatifs ---
# train_models.py → /app/scripts/ml/
# On remonte 3 fois : ml → scripts → app → surveillance-materiel_final
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DATA_PATH = os.path.join(ROOT_DIR, "data", "donnees_ml_combined.csv")
OUT_MODELS = os.path.join(ROOT_DIR, "models", "ml")
OUT_VIS = os.path.join(ROOT_DIR, "visualizations", "ml")

os.makedirs(OUT_MODELS, exist_ok=True)
os.makedirs(OUT_VIS, exist_ok=True)

# --- Chargement des données ---
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset introuvable : {DATA_PATH}\nAssure-toi que 'donnees_ml.csv' se trouve bien dans 'data/'.")
    print(f"📂 Chargement des données depuis : {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

# --- Préparation des features ---
def prepare_features(df):
    numeric_cols = ["cpu_util", "mem_util", "temp_cpu", "net_in_bytes", "net_out_bytes", "tcp_conn", "user_active", "usb_event"]
    available = [c for c in numeric_cols if c in df.columns]
    if not available:
        raise ValueError("❌ Aucune colonne numérique trouvée dans les données.")
    X = df[available].fillna(0)
    return X, available

def detect_label_column(df):
    for candidate in ["anomaly", "label", "target", "y"]:
        for c in df.columns:
            if c.lower() == candidate:
                return c
    return None

# --- Entraînement principal ---
def train():
    df = load_data()
    label_col = detect_label_column(df)
    print(f"🔍 Colonne de label détectée : {label_col if label_col else 'Aucune (mode non supervisé)'}")

    X, feature_names = prepare_features(df)
    print("📊 Utilisation des features :", feature_names)

    # Mise à l’échelle
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(OUT_MODELS, "scaler.joblib"))
    print("✅ Scaler sauvegardé.")

    # --- KMeans ---
    print("\n🌀 Entraînement du modèle KMeans...")
    try:
        kv = KElbowVisualizer(KMeans(random_state=42), k=(2,10))
        kv.fit(X_scaled)
        kv.show(outpath=os.path.join(OUT_VIS, "kmeans_elbow.png"))
        best_k = int(kv.elbow_value_ or 3)
    except Exception as e:
        print("⚠️ Elbow Visualizer échoué :", e)
        best_k = 3

    kmeans = KMeans(n_clusters=best_k, random_state=42).fit(X_scaled)
    joblib.dump(kmeans, os.path.join(OUT_MODELS, "kmeans.joblib"))
    print(f"✅ KMeans sauvegardé (k={best_k}).")

    try:
        sv = SilhouetteVisualizer(KMeans(n_clusters=best_k, random_state=42))
        sv.fit(X_scaled)
        sv.show(outpath=os.path.join(OUT_VIS, "kmeans_silhouette.png"))
    except Exception as e:
        print("⚠️ Silhouette Visualizer échoué :", e)

    # --- Isolation Forest ---
    print("\n🌲 Entraînement du modèle IsolationForest...")
    iforest = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
    iforest.fit(X_scaled)
    joblib.dump(iforest, os.path.join(OUT_MODELS, "iforest.joblib"))
    print("✅ IsolationForest sauvegardé.")

    scores = iforest.decision_function(X_scaled)
    plt.figure(figsize=(8,4))
    sns.histplot(scores, bins=50, kde=True)
    plt.title("Scores IsolationForest (haut = normal, bas = anormal)")
    plt.savefig(os.path.join(OUT_VIS, "iforest_scores.png"))
    plt.close()

    # --- Supervised (si label présent) ---
    if label_col:
        print("\n🎯 Entraînement supervisé avec RandomForest...")
        y = df[label_col].fillna(0).values
        stratify = y if len(np.unique(y)) > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=stratify)
        clf = RandomForestClassifier(n_estimators=200, random_state=42)
        clf.fit(X_train, y_train)
        joblib.dump(clf, os.path.join(OUT_MODELS, "classifier.joblib"))
        print("✅ RandomForest sauvegardé.")
        try:
            visualizer = ClassificationReport(clf, classes=np.unique(y).astype(str))
            visualizer.score(X_test, y_test)
            visualizer.show(outpath=os.path.join(OUT_VIS, "classification_report.png"))
        except Exception as e:
            print("⚠️ Visualisation Yellowbrick échouée :", e)
        y_pred = clf.predict(X_test)
        print("\n📈 Rapport de classification :\n", classification_report(y_test, y_pred))

    print("\n✅ Entraînement terminé !")
    print(f"📦 Modèles sauvegardés dans : {OUT_MODELS}")
    print(f"🖼️ Visualisations sauvegardées dans : {OUT_VIS}")

if __name__ == "__main__":
    train()

