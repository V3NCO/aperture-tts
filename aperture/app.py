from fastapi import FastAPI
from aperture.model import ModelLoader
from aperture.views import api_router

model = ModelLoader()

app = FastAPI()
app.include_router(api_router)
