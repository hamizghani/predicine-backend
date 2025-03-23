import string
from typing import Literal
import pandas as pd
import numpy as np
import json
from pydantic import BaseModel
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

from models import PredictionInternalInput

model = xgb.XGBRegressor()
model.load_model("xgb_model.json")

medicine_list = pd.read_csv("medicine_list.csv")
medicine_data = pd.read_csv("medicine.csv")



def infer_stockout(input_data: PredictionInternalInput):
    """
    Parameters:
    - json_input: JSON object dengan atribut user, user_category, zone, medicine_name, stock, 
                  record_timestamp, avg_visitor_weekly, price
    - changed to input_data: PredictionInternalInput
    """
    data = pd.DataFrame([input_data.model_dump()])

    data["category"] = data["medicine_name"].map(
        dict(zip(medicine_list["medicine_name"], medicine_list["category"]))
    )

    data["restock_frequency"] = data["medicine_name"].map(
        dict(zip(medicine_list["medicine_name"], medicine_list["avg_restock_frequency"]))
    )

    supplier_avg = medicine_data.groupby("medicine_name")["supplier_reliability"].mean().to_dict()
    data["supplier_reliability"] = data["medicine_name"].map(supplier_avg)

    relevant_data = medicine_data[(medicine_data["medicine_name"] == data["medicine_name"].values[0]) &
                                  (medicine_data["zone"] == data["zone"].values[0])]

    if not relevant_data.empty:
        data["disease_score_1"] = relevant_data["disease_score_1"].values[0]
        data["disease_score_2"] = relevant_data["disease_score_2"].values[0]
        data["disease_score_3"] = relevant_data["disease_score_3"].values[0]
        data["corr_disease_1"] = relevant_data["corr_disease_1"].values[0]
        data["corr_disease_2"] = relevant_data["corr_disease_2"].values[0]
        data["corr_disease_3"] = relevant_data["corr_disease_3"].values[0]
    else:
        raise ValueError("Data penyakit tidak ditemukan untuk kombinasi medicine_name dan zone.")

    data["avg_price"] = data["medicine_name"].map(
        dict(zip(medicine_list["medicine_name"], medicine_list["avg_price"]))
    )

    data["record_timestamp"] = pd.to_datetime(data["record_timestamp"])

    data["stock_per_visitor"] = data["stock"] / (data["avg_visitor_weekly"] + 1)  # Hindari divisi nol

    categorical_features = ["user_category", "zone", "medicine_name", "category", "corr_disease_1", "corr_disease_2", "corr_disease_3"]
    for col in categorical_features:
        data[col] = LabelEncoder().fit_transform(data[col])

    features = [
        "user_category", "zone", "medicine_name", "category", "stock",
        "restock_frequency", "supplier_reliability", "disease_score_1",
        "disease_score_2", "disease_score_3", "corr_disease_1", "corr_disease_2",
        "corr_disease_3", "avg_price", "avg_visitor_weekly", "price", "stock_per_visitor"
    ]

    predictions = model.predict(data[features])

    data["predicted_stockout_days"] = predictions
    return data[["user", "medicine_name", "predicted_stockout_days"]].to_dict("records")[0]
