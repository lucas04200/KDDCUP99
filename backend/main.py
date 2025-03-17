from fastapi import FastAPI, Request
import pickle
import numpy as np
import pandas as pd

app = FastAPI()



@app.get("/")
def hello_world():
    return {"message": "Hello World - FastAPI"}

model = None
try:
    with open('../artifacts/model.pkl', 'rb') as handle:
        model = pickle.load(handle)
except Exception as e:
    model = None

@app.get("/test_model")
def test_model_loading():
    if model:
        return {"message": "Le modèle a été chargé avec succès"}
    else:
        return {"message": "Erreur lors du chargement du modèle"}