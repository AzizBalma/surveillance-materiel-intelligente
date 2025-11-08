import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Nombre de données à générer
n_normal = 400
n_anomaly = 600

# Génération des timestamps
start_time = datetime(2025, 1, 1, 0, 0, 0)
timestamps_normal = [start_time + timedelta(seconds=i*10) for i in range(n_normal)]
timestamps_anomaly = [start_time + timedelta(seconds=i*10) for i in range(n_anomaly)]

# Fonction pour générer des valeurs normales
def generate_normal():
    return {
        "cpu_util": np.random.uniform(0, 20),
        "mem_util": np.random.uniform(20, 50),
        "temp_cpu": np.random.uniform(40, 60),
        "net_in_bytes": np.random.uniform(1e6, 1e9),
        "net_out_bytes": np.random.uniform(1e6, 1e9),
        "tcp_conn": np.random.randint(1, 50),
        "user_active": np.random.randint(0, 2),
        "usb_event": np.random.randint(0, 2),
        "anomaly": 0
    }

# Fonction pour générer des valeurs anormales
def generate_anomaly():
    return {
        "cpu_util": np.random.uniform(70, 100),
        "mem_util": np.random.uniform(70, 100),
        "temp_cpu": np.random.uniform(80, 100),
        "net_in_bytes": np.random.uniform(1e9, 1e10),
        "net_out_bytes": np.random.uniform(1e9, 1e10),
        "tcp_conn": np.random.randint(100, 500),
        "user_active": np.random.randint(1, 5),
        "usb_event": np.random.randint(0, 5),
        "anomaly": 1
    }

# Générer les données
data_normal = [generate_normal() for _ in range(n_normal)]
data_anomaly = [generate_anomaly() for _ in range(n_anomaly)]

df_normal = pd.DataFrame(data_normal)
df_normal["timestamp"] = timestamps_normal
df_normal["host"] = "simulated"

df_anomaly = pd.DataFrame(data_anomaly)
df_anomaly["timestamp"] = timestamps_anomaly
df_anomaly["host"] = "simulated"

# Combiner les données simulées avec ton dataset existant
df_simulated = pd.concat([df_normal, df_anomaly], ignore_index=True)

# Optionnel : mélanger les lignes
df_simulated = df_simulated.sample(frac=1, random_state=42).reset_index(drop=True)

# Sauvegarder dans un CSV
df_simulated.to_csv("data/simulated_ml_data.csv", index=False)

print("✅ Dataset simulé créé avec", len(df_simulated), "lignes")
print(df_simulated["anomaly"].value_counts())

