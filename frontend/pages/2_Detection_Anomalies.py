import streamlit as st
from utils import get_data, detect_anomalie_batch, apply_filters
import pandas as pd
st.title("🔍 Détection des Anomalies Réseau")

df = get_data()
df_filtered = apply_filters(df)

# Simulation des données
st.subheader("🔄 Simulation des Données")
index_simulation = st.slider("⚙️ Contrôler la simulation", 0, len(df_filtered) - 1, 0)

st.write(f"📡 Connexion simulée :")
st.write(df_filtered.iloc[index_simulation])

connection = df_filtered.iloc[index_simulation].drop(columns=["label"]).apply(lambda x: x.item() if isinstance(x, (pd.Int64Dtype, pd.Float64Dtype, pd.Timestamp)) else x).values.tolist()

anomalie = detect_anomalie_batch([connection])

st.subheader("🔍 Analyse des Anomalies")
df_filtered["anomalie"] = detect_anomalie_batch(df_filtered.drop(columns=["label"]).values.tolist())
df_anomalies = df_filtered[df_filtered["anomalie"] == 1]

if len(df_anomalies) > 0:
    st.error(f"🚨 Alerte : {len(df_anomalies)} anomalies détectées !")
else:
    st.success("✅ Aucune anomalie détectée.")

st.dataframe(df_anomalies[["service", "src_bytes", "dst_bytes", "label", "anomalie"]])
