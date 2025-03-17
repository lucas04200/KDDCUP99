import streamlit as st
import requests
import pickle

st.title("Hackathon")

st.write("Hello !")

# Appel à l'API FastAPI
backend_url = "http://backend:8000/"  # URL du service backend dans Docker

try:
    response = requests.get(backend_url)
    if response.status_code == 200:
        st.success(f"Réponse de l'API : {response.json()['message']}")
    else:
        st.error(f"Erreur {response.status_code} lors de l'appel à l'API")
except requests.exceptions.ConnectionError:
    st.error("Impossible de contacter l'API. Vérifiez si le backend est démarré.")




