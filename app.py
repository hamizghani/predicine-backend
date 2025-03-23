from datetime import datetime
import json
from typing import Annotated
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache

import prediction
from models import PredictionInput

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    recordified = sorted([{'timestamp': timestamp,**dataentry} for timestamp, dataentry in res.items()], key=lambda e:datetime.strptime(e['timestamp'], '%Y-%m-%d'))
    return recordified

@lru_cache
def get_disease_rechartable(filename: str):
    with open(filename, 'r') as f:
        data = json.load(f)
        return transform_to_rechartsable(data)


@app.get('/v1/disease')
def get_disease():
    chartable_data = get_disease_rechartable('disease.json')
    trending_diseases = sorted([(v,k) for k,v in chartable_data[-1].items() if k!='timestamp'], reverse=True)
    trending_disease_names = [e[1] for e in trending_diseases[:3]]
    return JSONResponse({'trending_diseases': trending_disease_names, 'data':chartable_data})

@app.get('/v1/inventory')
def get_inventory(username: str):
    return JSONResponse(prediction.get_inventory(username))

@app.post('/v1/inventory/predict')
def predict_by_inventory(predictionInput: Annotated[PredictionInput, Body(embed=True)]):
    return JSONResponse({'status':"SUCCESS", 'data':"TODO"})
