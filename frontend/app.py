import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ✅ Configuration de la page
st.set_page_config(page_title="Network Traffic Dashboard", layout="wide")
st.title("🌐 Network Traffic Dashboard (KDDCUP99)")

# ✅ URL du backend dans Docker
backend_url = "http://backend:8000"

# ✅ Vérifier la connexion avec FastAPI
try:
    response = requests.get(backend_url)
    if response.status_code == 200:
        st.success(f"Réponse de l'API : {response.json().get('message', 'Pas de message')}")
    else:
        st.error(f"Erreur {response.status_code} lors de l'appel à l'API")
except requests.exceptions.ConnectionError:
    st.error("❌ Impossible de contacter l'API. Vérifiez si le backend est démarré.")

# ✅ Fonction pour récupérer les données avec cache
@st.cache_data(ttl=30)
def get_data():
    try:
        response = requests.get(f"{backend_url}/get_data")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Erreur {response.status_code} en récupérant les données")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de récupérer les données du backend.")
        return pd.DataFrame()

# ✅ Mode de visualisation : Temps réel ou Replay
mode = st.radio("🔄 Mode de visualisation", ["Temps Réel", "Replay"])

# ✅ Stocker l'historique des données
if "historique_data" not in st.session_state:
    st.session_state.historique_data = []

# ✅ Récupération des données
if mode == "Temps Réel":
    df = get_data()
    if not df.empty:
        st.session_state.historique_data.append(df.copy())
else:
    if st.session_state.historique_data:
        max_steps = len(st.session_state.historique_data) - 1
        step = st.slider("⏪ Revenir en arrière", 0, max_steps, max_steps)
        df = st.session_state.historique_data[step]
    else:
        df = pd.DataFrame()

if df.empty:
    st.warning("📭 Aucune donnée disponible.")
else:
    # ✅ Filtres interactifs
    protocol_filter = st.sidebar.multiselect("📡 Filtrer par Protocole", df["protocol_type"].unique(), default=df["protocol_type"].unique())
    service_filter = st.sidebar.multiselect("🛠️ Filtrer par Service", df["service"].unique(), default=df["service"].unique())

    df_filtered = df[df["protocol_type"].isin(protocol_filter) & df["service"].isin(service_filter)]

    # 📊 **Graphique des connexions réseau**
    st.subheader("📡 Visualisation des Connexions Réseau")
    fig_scatter = px.scatter(df_filtered, x="src_bytes", y="dst_bytes", color="protocol_type", 
                             hover_data=["service", "flag"], title="Trafic Réseau")
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 📈 **Histogramme des protocoles**
    st.subheader("📊 Répartition des Protocoles")
    fig_hist = px.histogram(df_filtered, x="protocol_type", title="Distribution des Protocoles", color="protocol_type")
    st.plotly_chart(fig_hist, use_container_width=True)

    # 🥧 **Camembert des anomalies**
    st.subheader("🔍 Répartition des Anomalies par Protocole")
    df_filtered["anomalie"] = df_filtered["label"].apply(lambda x: "Normal" if x == "normal." else "Anomalie")
    df_pie = df_filtered.groupby("protocol_type")["anomalie"].value_counts().unstack().fillna(0)
    fig_pie = px.pie(df_pie, values="Anomalie", names=df_pie.index, title="Anomalies par Protocole")
    st.plotly_chart(fig_pie, use_container_width=True)

    # 📋 **Tableau des connexions réseau**
    st.subheader("📋 Détails des Connexions Réseau")
    st.dataframe(df_filtered[["protocol_type", "service", "src_bytes", "dst_bytes", "label"]])
