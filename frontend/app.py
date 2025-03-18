import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json

# ✅ Configuration de la page
st.set_page_config(page_title="🔍 Détection d'Anomalies Réseau", layout="wide")
st.title("🚀 Détection d'Anomalies Réseau")

# ✅ URL du backend FastAPI
API_URL = "http://backend:8000"  # URL du backend

# ✅ Fonction de récupération des données
@st.cache_data
def get_data():
    response = requests.get(f"{API_URL}/data")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Erreur lors de la récupération des données.")
        return pd.DataFrame()

# ✅ Fonction de détection d'anomalies
import pandas as pd
import requests
import json

# ✅ Fonction de détection d'anomalies avec sérialisation JSON
def detect_anomalie_batch(connections):
    # Convertir toutes les données de type pandas en types natifs Python compatibles avec JSON
    def convert_to_native_types(data):
        if isinstance(data, pd.Series):  # Si c'est une Series pandas
            return data.to_dict()  # Convertir en dictionnaire (clé/valeur)
        elif isinstance(data, pd.DataFrame):  # Si c'est un DataFrame pandas
            return data.applymap(lambda x: x.item() if isinstance(x, pd.Timestamp) else x).to_dict(orient="records")
        else:
            return data  # Si ce n'est pas un type pandas, retourner tel quel
    
    # Convertir les données de type pandas
    connections_converted = [convert_to_native_types(c) for c in connections]
    
    # Sérialisation avec json.dumps pour gérer les types spécifiques
    try:
        response = requests.post(f"{API_URL}/predict", json={"features": connections_converted})
        if response.status_code == 200:
            return response.json().get("predictions", None)
        else:
            return None
    except Exception as e:
        print(f"Erreur lors de l'envoi de la requête : {e}")
        return None

# ✅ Chargement des données
df = get_data()

# --- Filtres ---
st.sidebar.header("🔎 Filtres")
services = st.sidebar.multiselect("🛠️ Filtrer par Service", df["service"].unique(), default=df["service"].unique())
labels = st.sidebar.multiselect("🏷️ Filtrer par Label", df["label"].unique(), default=df["label"].unique())
time_range = st.sidebar.slider("🕒 Plage de connexions", 0, len(df) - 1, (0, len(df) - 1))

df_filtered = df[df["service"].isin(services) & df["label"].isin(labels)]
df_filtered = df_filtered[(df_filtered.index >= time_range[0]) & (df_filtered.index <= time_range[1])]

# --- Visualisation des Connexions Réseau par Protocole ---
st.subheader("📡 Visualisation des Flux Réseau par Protocole")

# Vérification que la colonne 'protocol_type' existe
if 'protocol_type' in df.columns:
    # Affichage des protocoles disponibles
    protocols = df['protocol_type'].unique()
    st.write("Protocole(s) présent(s) dans les données :", protocols)
    
    for protocol in protocols:
        st.write(f"### Protocole: {protocol}")
        
        # Filtrer les données par protocole
        df_protocol = df[df['protocol_type'] == protocol]
        
        # Visualisation avec Plotly
        fig = px.scatter(
            df_protocol, 
            x='src_bytes', y='dst_bytes',  # Utilisation de src_bytes et dst_bytes
            color='service', 
            size='src_bytes', 
            hover_data=['protocol_type', 'src_bytes', 'dst_bytes'], 
            title=f"Flux Réseau - Protocole {protocol}",
            labels={"src_bytes": "Bytes Source", "dst_bytes": "Bytes Destination"}
        )
        st.plotly_chart(fig)
else:
    st.error("❌ La colonne 'protocol_type' est manquante dans les données.")

# --- Partie 2 : Simulation et Lecture des Données ---
st.subheader("🔄 Simulation des Données")

# Slider pour replay des données
index_simulation = st.slider("⚙️ Contrôler la simulation", 0, len(df_filtered) - 1, 0)

# Afficher la ligne correspondante à l'index sélectionné
st.write(f"📡 Connexion simulée :")
st.write(df_filtered.iloc[index_simulation])

# Affichage des anomalies détectées pour cette connexion simulée
st.write("⚠️ Anomalies détectées pour cette simulation :")
connection = df_filtered.iloc[index_simulation].drop(columns=["label"]).values.tolist()  # Exclure la colonne "label" pour la prédiction
anomalie = detect_anomalie_batch([connection])

if anomalie and anomalie[0] == 1:
    st.error("🚨 Anomalie détectée !")
else:
    st.success("✅ Aucune anomalie détectée.")


# --- Détection des Anomalies ---
st.subheader("🔍 Analyse des Anomalies")
seuil_anomalie = st.slider("⚠️ Seuil d'alerte (min anomalies)", 1, 50, 10)
df_filtered["anomalie"] = detect_anomalie_batch(df_filtered.drop(columns=["label"]).values.tolist())
df_anomalies = df_filtered[df_filtered["anomalie"] == 1]

if len(df_anomalies) > seuil_anomalie:
    st.error(f"🚨 Alerte : {len(df_anomalies)} anomalies détectées !")

st.dataframe(df_anomalies[["service", "src_bytes", "dst_bytes", "label", "anomalie"]])

# --- Visualisation des Anomalies ---
st.subheader("📊 Distribution des Anomalies")
fig = px.histogram(df_anomalies, x="service", color="label", title="Répartition des Anomalies par Service")
st.plotly_chart(fig)

# --- Journalisation des Anomalies ---
if "log_anomalies" not in st.session_state:
    st.session_state.log_anomalies = pd.DataFrame(columns=df_anomalies.columns)

st.session_state.log_anomalies = pd.concat([st.session_state.log_anomalies, df_anomalies]).drop_duplicates()
st.dataframe(st.session_state.log_anomalies)
csv = st.session_state.log_anomalies.to_csv(index=False)

st.download_button(
    label="📥 Télécharger le journal des anomalies",
    data=csv,
    file_name="journal_anomalies.csv",
    mime="text/csv"
)

st.success("✅ Vous pouvez télécharger le journal des anomalies.")
