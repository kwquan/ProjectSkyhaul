from fastapi import FastAPI
from .droneCtrl import drone_router

app = FastAPI()
app.include_router(drone_router)
