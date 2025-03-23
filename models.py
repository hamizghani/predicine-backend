
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class AddMedicineBody(BaseModel):
    name: str
    amount: int


class RestockAlert(BaseModel):
    name: str
    quantity: int


class Product(BaseModel):
    name: str
    price: int
    currency: str = "IDR"
    image: str = ""
    description: str = ""
    category: Literal["Painkiller", "Antibiotic", "Antiviral", "Diabetes", "Cardiovascular"]
    stock: int
    sold: int


class ProductAvailability(BaseModel):
    percentage: int
    status: Literal['Out of stock', 'Low stock', 'In stock']


class ProductPrediction(BaseModel):
    restockDate: datetime
    availability: ProductAvailability


class SalesModel(BaseModel):
    amount: int
    currency: str = "IDR"
    trend: Literal['Up', 'Down']


class Overview(BaseModel):
    sales: SalesModel
    quantity: int
    topSelling: str
    overallStockStatus: ProductAvailability


class DashboardData(BaseModel):
    overview: Overview
    restockAlerts: list[RestockAlert]
    medicineRecommendations: str
    products: list[Product]


class ProductPredictionInput(BaseModel):
    name: str
    price: int
    record_timestamp: datetime



class PredictionInput(BaseModel):
    user: str
    user_category: str
    avg_visitor_weekly: int
    medicines: list[ProductPredictionInput]
