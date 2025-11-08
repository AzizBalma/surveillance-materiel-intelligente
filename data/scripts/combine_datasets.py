import pandas as pd

# Charger les vraies données
df_real = pd.read_csv("data/donnees_ml.csv")

# Charger les données simulées
df_sim = pd.read_csv("data/simulated_ml_data.csv")

# Ajouter les colonnes manquantes avec des valeurs par défaut
for col in df_real.columns:
    if col not in df_sim.columns:
        if col in ["timestamp", "host", "usb_device"]:
            df_sim[col] = "simulated"
        else:
            df_sim[col] = 0

# Réordonner les colonnes
df_sim = df_sim[df_real.columns]

# Concaténer
df_combined = pd.concat([df_real, df_sim], ignore_index=True)

# Sauvegarder
df_combined.to_csv("data/donnees_ml_combined.csv", index=False)
print("✅ Dataset combiné créé avec succès :", df_combined.shape)

