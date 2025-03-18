from fastapi import FastAPI
import pandas as pd
import pickle
from pydantic import BaseModel

app = FastAPI()

# Charger le dataset prétraité
DATA_PATH = "/app/data/csv/KDDCup99.csv"
df = pd.read_csv(DATA_PATH, sep=',')
df['label'] = (df['label'] != 'normal').astype(int)  # Convertir en 0 (normal) / 1 (anomalie)

# Charger le modèle
MODEL_PATH = "/app/artifacts/model.pkl"
with open(MODEL_PATH, "rb") as model_file:
    model = pickle.load(model_file)

# Sélectionner les colonnes pertinentes (exclure label si utilisé)
FEATURES = df.drop(columns=["label"]).columns.tolist()

class ConnectionData(BaseModel):
    features: list

@app.get("/data")
async def get_data(num_connections: int = 1000):  # Valeur par défaut = 10000
    """Retourne un échantillon des connexions réseau."""
    return df.sample(num_connections).to_dict(orient="records")

@app.post("/predict")
async def predict(data: ConnectionData):
    """Détection d'anomalie sur un échantillon de connexions (max 1000 lignes)."""
    print("Nombre de connexions reçues :", len(data.features))
    try:
        # Création du DataFrame avec toutes les connexions envoyées
        df_input = pd.DataFrame(data.features, columns=FEATURES)

        # Vérifier les types de colonnes avant d'envoyer les données
        print("Types de colonnes avant le traitement :\n", df_input.dtypes)

        # Convertir les colonnes catégorielles en type string
        df_input = df_input.applymap(str)

        print("Dtypes avant transformation :")
        print(df_input.dtypes)
        print(df_input.head())  # Pour inspecter les premières lignes de données

        # Vérifiez s'il y a des valeurs NaN ou des types inattendus dans les colonnes
        print(df_input.isnull().sum())


        # Convertir les colonnes catégorielles en chaînes
        df_input['protocol_type'] = df_input['protocol_type'].astype(str)
        df_input['service'] = df_input['service'].astype(str)
        df_input['flag'] = df_input['flag'].astype(str)

        # Appliquer pd.get_dummies() pour encoder les variables catégorielles
        df_input_encoded = pd.get_dummies(df_input, columns=['protocol_type', 'service', 'flag'])

        
        # Assurer que les colonnes correspondent à celles du modèle
        train_columns = model.feature_names_in_
        df_input_encoded = df_input_encoded.reindex(columns=train_columns, fill_value=0)

        # Prédiction
        predictions = model.predict(df_input_encoded)

        # Retourne les prédictions sous forme de liste
        return {"predictions": predictions.tolist()}
    
    except Exception as e:
        return {"error": str(e)}
