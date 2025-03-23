from datetime import datetime
import json
from typing import Annotated
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
from functools import lru_cache

import prediction
from models import PredictionInput

app = FastAPI()

def transform_to_rechartsable(data: dict):
    res = {}
    for disease,diseaseinfo in data.items():
        avgs = {}
        locationCount = 0
        
        for location, stats in diseaseinfo['data'].items():
            locationCount+=1
            for entry in stats:
                avgs[entry['timestamp']]=avgs.get(entry['timestamp'], 0)+entry['rate_per_1000']
        
        for k in avgs:
            res[k] = res.get(k, {})
            res[k].update({disease: avgs[k]//locationCount})
    recordified = [{'timestamp': datetime.strptime(timestamp, "%Y-%m-%d").isoformat(),**dataentry} for timestamp, dataentry in res.items()]
    return recordified

@lru_cache
def get_disease_rechartable(filename: str):
    with open(filename, 'r') as f:
        data = json.load(f)
        return transform_to_rechartsable(data)

@app.get('/v1/disease')
def get_disease():
    return JSONResponse(get_disease_rechartable('disease.json'))

@app.get('/v1/inventory')
def get_inventory(username: str):
    return JSONResponse(prediction.get_inventory(username))

@app.post('/v1/inventory/predict')
def predict_by_inventory(predictionInput: Annotated[PredictionInput, Body(embed=True)]):
    return JSONResponse({'status':"SUCCESS", 'data':"TODO"})
