import streamlit as st
from utils import get_data, detect_anomalie_batch, apply_filters
import pandas as pd

st.title("🔍 Détection des Anomalies Réseau")

# Récupération des données
df = get_data()

# Filtrage des données
df_filtered = apply_filters(df)

# Simulation des données
st.subheader("🔄 Simulation des Données")
index_simulation = st.slider("⚙️ Contrôler la simulation", 0, len(df_filtered) - 1, 0)

st.write(f"📡 Connexion simulée :")
st.write(df_filtered.iloc[index_simulation])

# Connexion pour l'anomalie
connection = df_filtered.iloc[index_simulation].drop(columns=["label"]).values.tolist()  # Utiliser les données directement sans conversion explicite

# Détection des anomalies
anomalie = detect_anomalie_batch([connection])

# Analyse des anomalies
st.subheader("🔍 Analyse des Anomalies")
# Applique la conversion en str uniquement pour les colonnes object
df_filtered["anomalie"] = detect_anomalie_batch(df_filtered.drop(columns=["label"]).apply(
    lambda x: x.astype(str) if x.dtype == 'object' else x  # Conversion les object
).values.tolist())

# Récupérer les anomalies
df_anomalies = df_filtered[df_filtered["anomalie"] == 1]

if len(df_anomalies) > 0:
    st.error(f"🚨 Alerte : {len(df_anomalies)} anomalies détectées !")
else:
    st.success("✅ Aucune anomalie détectée.")

st.dataframe(df_anomalies[["service", "src_bytes", "dst_bytes", "label", "anomalie"]])
