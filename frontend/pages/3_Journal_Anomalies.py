import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_data, detect_anomalie_batch, apply_filters

st.title("📋 Journal des Anomalies Réseau")

df = get_data()
df_filtered = apply_filters(df)

df_filtered["anomalie"] = detect_anomalie_batch(df_filtered.drop(columns=["label"]).values.tolist())
df_anomalies = df_filtered[df_filtered["anomalie"] == 1]

if "log_anomalies" not in st.session_state:
    st.session_state.log_anomalies = pd.DataFrame(columns=df_anomalies.columns)

st.session_state.log_anomalies = pd.concat([st.session_state.log_anomalies, df_anomalies]).drop_duplicates()
st.dataframe(st.session_state.log_anomalies)

# Sauvegarde CSV
csv = st.session_state.log_anomalies.to_csv(index=False)

st.download_button(
    label="📥 Télécharger le journal des anomalies",
    data=csv,
    file_name="journal_anomalies.csv",
    mime="text/csv"
)

fig = px.histogram(df_anomalies, x="service", color="label", title="Répartition des Anomalies par Service")
st.plotly_chart(fig)
