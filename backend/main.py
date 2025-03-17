from fastapi import FastAPI
import pandas as pd
import pickle
from pydantic import BaseModel
import uvicorn

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
async def get_data():
    """Retourne un échantillon des connexions réseau."""
    return df.sample(50).to_dict(orient="records")  # Renvoie 50 connexions aléatoires


@app.post("/predict")
async def predict(data: ConnectionData):
    """Détection d'anomalie sur un échantillon de connexions (max 100 lignes)."""
    print("Nombre de connexions reçues :", len(data.features))
    
    try:
        # Création du DataFrame avec toutes les connexions envoyées
        df_input = pd.DataFrame(data.features, columns=FEATURES)

        # Sélectionner un échantillon de 500 lignes max
        if len(df_input) > 500:
            df_input = df_input.sample(n=500, random_state=42)

        print(f"Données envoyées pour prédiction ({len(df_input)} lignes) :\n", df_input.head())

        # Appliquer le même encodage qu'à l'entraînement
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