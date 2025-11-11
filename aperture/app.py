from fastapi import FastAPI
from aperture.config import model
from aperture.views import api_router


app = FastAPI()
app.include_router(api_router)
