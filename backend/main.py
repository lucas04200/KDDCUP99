from fastapi import FastAPI, Request
import pickle
import numpy as np
import pandas as pd

app = FastAPI()



@app.get("/")
def hello_world():
    return {"message": "Hello World - FastAPI"}