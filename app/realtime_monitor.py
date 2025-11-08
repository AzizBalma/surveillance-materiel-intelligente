# realtime_monitor.py
import psutil
import pandas as pd
import time
import joblib
import os
from datetime import datetime

MODEL_DIR = '/app/models'
FEATURES = ['cpu_util','mem_util','temp_cpu','net_in_bytes','net_out_bytes','tcp_conn','user_active','usb_event']

model = joblib.load(os.path.join(MODEL_DIR,'if_model.pkl'))
scaler = joblib.load(os.path.join(MODEL_DIR,'scaler.pkl'))

LIVE_FILE = '/app/data/system_data_live.csv'
os.makedirs('/app/data', exist_ok=True)

def collect_system_data():
    data = {
        'timestamp': datetime.now().isoformat(),
        'host': os.uname()[1],
        'cpu_util': psutil.cpu_percent(),
        'mem_util': psutil.virtual_memory().percent,
        'temp_cpu': psutil.sensors_temperatures().get('coretemp', [])[0].current if psutil.sensors_temperatures() else 50,
        'net_in_bytes': psutil.net_io_counters().bytes_recv,
        'net_out_bytes': psutil.net_io_counters().bytes_sent,
        'tcp_conn': len(psutil.net_connections(kind='tcp')),
        'user_active': len(psutil.users()),
        'usb_event': 0,  # à remplir si tu as des events USB
        'usb_device': 0
    }
    return data

while True:
    row = collect_system_data()
    X_live = pd.DataFrame([row])[FEATURES].fillna(0)
    X_scaled = scaler.transform(X_live)
    row['anomaly'] = int(model.predict(X_scaled)[0] == -1)
    
    # Sauvegarde
    if os.path.exists(LIVE_FILE):
        df_live = pd.read_csv(LIVE_FILE)
        df_live = pd.concat([df_live, pd.DataFrame([row])], ignore_index=True)
    else:
        df_live = pd.DataFrame([row])
    df_live.to_csv(LIVE_FILE, index=False)
    
    # Alertes
    if row['anomaly']:
        print(f"🚨 Anomalie détectée ! {row}")
    
    time.sleep(2)
