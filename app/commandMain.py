from fastapi import FastAPI
from .commandCtrl import command_router

app = FastAPI()
app.include_router(command_router)


