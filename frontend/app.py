import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
import datetime

# ✅ Configuration de la page
st.set_page_config(page_title="🔍 Détection d'Anomalies Réseau", layout="wide")
st.title("🚀 Détection d'Anomalies Réseau")

# ✅ URL du backend FastAPI
API_URL = "http://backend:8000"  # Assurez-vous que l'URL correspond à votre backend (ajustez si nécessaire)

# ✅ Fonction pour récupérer les données
def get_data():
    response = requests.get(f"{API_URL}/data")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ Erreur lors de la récupération des données.")
        return pd.DataFrame()

# ✅ Chargement des données
if "df" not in st.session_state:
    st.session_state.df = get_data()
df = st.session_state.df

# ✅ Fonction de prédiction (données en batch)
def detect_anomalie_batch(connections):
    response = requests.post(f"{API_URL}/predict_batch", json={"features": connections})
    if response.status_code == 200:
        return response.json().get("predictions", None)
    return None

# ✅ Mode de visualisation
mode = st.radio("🔄 Mode de visualisation", ["Temps Réel (Simulé)", "Replay"])

# ✅ Stockage de l’historique en session
if "historique" not in st.session_state:
    st.session_state.historique = []

# ✅ Simulation en temps réel
if mode == "Temps Réel (Simulé)":
    if len(st.session_state.historique) == 0:
        st.session_state.historique.append(df.iloc[0:1])
    
    last_step = len(st.session_state.historique[-1])
    new_step = min(last_step + 5, len(df))
    
    if new_step > last_step:
        new_data = df.iloc[last_step:new_step].copy()
        # Appliquer la détection d'anomalies sur un lot de données (batch)
        new_data["anomalie"] = detect_anomalie_batch(new_data.drop(columns=["label"]).values.tolist())
        st.session_state.historique.append(new_data)
        time.sleep(1)  # Pause pour éviter le spam

    df_affiche = st.session_state.historique[-1]
else:
    step = st.slider("⏪ Revenir dans le temps", 0, len(df) - 1, len(df) - 1)
    df_affiche = df.iloc[:step]

# ✅ Filtres
st.sidebar.header("🔎 Filtres")
protocols = st.sidebar.multiselect("📡 Filtrer par Protocole", df["protocol_type"].unique(), default=df["protocol_type"].unique())
services = st.sidebar.multiselect("🛠️ Filtrer par Service", df["service"].unique(), default=df["service"].unique())

df_filtered = df_affiche[df_affiche["protocol_type"].isin(protocols) & df_affiche["service"].isin(services)]




# ✅ Statistiques
st.sidebar.subheader("📊 Statistiques Globales")
st.sidebar.metric("Total Connexions", len(df_filtered))
st.sidebar.metric("Anomalies Détectées", len(df_filtered[df_filtered["anomalie"] == "Anomalie"]))

# ✅ Visualisation des connexions
st.subheader("📡 Visualisation des Flux Réseau")
st.plotly_chart(px.scatter(df_filtered, x="src_bytes", y="dst_bytes", color="protocol_type", hover_data=["service", "flag"], title="Trafic Réseau"), use_container_width=True)

# ✅ Distribution des protocoles
st.subheader("📊 Répartition des Protocoles")
st.plotly_chart(px.histogram(df_filtered, x="protocol_type", title="Distribution des Protocoles", color="protocol_type"), use_container_width=True)

# ✅ Détection des Anomalies
st.subheader("🔍 Détection des Anomalies")
seuil_anomalie = st.slider("⚠️ Seuil d'alerte (min anomalies)", 1, 50, 10)
df_anomalies = df_filtered[df_filtered["anomalie"] == "Anomalie"]
if len(df_anomalies) > seuil_anomalie:
    st.error(f"🚨 Alerte : {len(df_anomalies)} anomalies détectées !")

st.dataframe(df_anomalies[["protocol_type", "service", "src_bytes", "dst_bytes", "label"]])

# ✅ Journalisation et export
st.subheader("📜 Journalisation et Export")
if st.button("📥 Exporter les logs d'anomalies"):
    df_anomalies.to_csv("logs_anomalies.csv", index=False)
    st.success("✅ Logs exportés sous 'logs_anomalies.csv'.")

# ✅ Graphique des anomalies
st.plotly_chart(px.pie(df_anomalies, names="protocol_type", title="Anomalies par Protocole"), use_container_width=True)

# ✅ Stockage des anomalies pour audit
if "log_anomalies" not in st.session_state:
    st.session_state.log_anomalies = pd.DataFrame(columns=df_anomalies.columns)
st.session_state.log_anomalies = pd.concat([st.session_state.log_anomalies, df_anomalies]).drop_duplicates()
st.dataframe(st.session_state.log_anomalies)

if st.button("📥 Exporter le journal des anomalies"):
    st.session_state.log_anomalies.to_csv("journal_anomalies.csv", index=False)
    st.success("✅ Journal exporté sous 'journal_anomalies.csv'.")
