from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Chemin du fichier CSV
DATASET_PATH = "/app/data/csv/KDDCup99.csv"

# Charger et traiter le dataset une seule fois au démarrage de l'application
df = pd.read_csv(DATASET_PATH, header=None, dtype=str, low_memory=False)

# Définir les colonnes du dataset
df.columns = ["duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
              "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", "num_compromised",
              "root_shell", "su_attempted", "num_root", "num_file_creations", "num_shells",
              "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
              "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
              "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
              "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
              "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
              "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label"]

# Convertir les colonnes nécessaires en numériques
cols_to_convert = ["dst_bytes", "src_bytes", "num_failed_logins", "count", "srv_count", 
                   "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate", 
                   "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", 
                   "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", 
                   "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate", 
                   "dst_host_rerror_rate", "dst_host_srv_rerror_rate"]

df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

# Route d'accueil
@app.get("/")
def hello_world():
    return {"message": "Hello World - FastAPI"}

# Route pour récupérer un sous-ensemble de données aléatoires
@app.get("/get_data")
def get_data():
    sampled_data = df.sample(100)  # Prendre un échantillon aléatoire de 100 lignes
    return sampled_data.to_dict(orient="records")

# Route pour récupérer les colonnes disponibles
@app.get("/columns")
def get_columns():
    return {"columns": list(df.columns)}
