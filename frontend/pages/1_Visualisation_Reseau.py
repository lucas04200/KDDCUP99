import streamlit as st
import plotly.express as px
from utils import get_data, apply_filters

st.title("📡 Visualisation des Flux Réseau")

# Récupérer les données
df = get_data()
df_filtered = apply_filters(df)

# Affichage des protocoles
if 'protocol_type' in df.columns:
    protocols = df['protocol_type'].unique()
    for protocol in protocols:
        st.subheader(f"Protocole: {protocol}")
        
        df_protocol = df_filtered[df_filtered['protocol_type'] == protocol]

        fig = px.scatter(
            df_protocol, 
            x='src_bytes', y='dst_bytes',  
            color='service', 
            size='src_bytes', 
            hover_data=['protocol_type', 'src_bytes', 'dst_bytes'], 
            title=f"Flux Réseau - Protocole {protocol}",
            labels={"src_bytes": "Bytes Source", "dst_bytes": "Bytes Destination"}
        )
        st.plotly_chart(fig)
else:
    st.error("❌ La colonne 'protocol_type' est manquante dans les données.")
