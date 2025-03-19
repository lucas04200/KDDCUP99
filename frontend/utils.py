import streamlit as st
import pandas as pd
import requests

API_URL = "http://backend:8000"  # URL du backend FastAPI

# Récupération des données du backend
@st.cache_data
def get_data():
    response = requests.get(f"{API_URL}/data")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Erreur lors de la récupération des données.")
        return pd.DataFrame()

# detection des anomalies
def detect_anomalie_batch(connections):
    """Détecte les anomalies en envoyant les connexions au backend"""
    
    def convert_to_native_types(data):
        if isinstance(data, pd.Series):  # Si c'est une Series pandas
            return data.to_dict()  # Convertir en dictionnaire (clé/valeur)
        elif isinstance(data, pd.DataFrame):  # Si c'est un DataFrame pandas
            return data.applymap(lambda x: x.item() if isinstance(x, (pd.Timestamp, pd.Int64Dtype, pd.Float64Dtype)) else x).to_dict(orient="records")
        else:
            return data  # Si ce n'est pas un type pandas, retourner tel quel

    try:
        connections_converted = [convert_to_native_types(c) for c in connections]
        response = requests.post(f"{API_URL}/predict", json={"features": connections_converted})
        
        if response.status_code == 200:
            return response.json().get("predictions", None)
        else:
            print(f"Erreur API : {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erreur lors de l'envoi de la requête : {e}")
        return None

# pouvoir appliquer le filtre sur la page
def apply_filters(df):
    st.sidebar.header("🔎 Filtres")
    services = st.sidebar.multiselect("🛠️ Filtrer par Service", df["service"].unique(), default=df["service"].unique())
    labels = st.sidebar.multiselect("🏷️ Filtrer par Label", df["label"].unique(), default=df["label"].unique())
    time_range = st.sidebar.slider("🕒 Plage de connexions", 0, len(df) - 1, (0, len(df) - 1))

    df_filtered = df[df["service"].isin(services) & df["label"].isin(labels)]
    df_filtered = df_filtered[(df_filtered.index >= time_range[0]) & (df_filtered.index <= time_range[1])]
    
    return df_filtered
