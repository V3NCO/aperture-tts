from fastapi import APIRouter, Depends
from aperture.services import ModelService
from aperture.app_services import get_model

api_router = APIRouter()

@api_router.get('/')
async def index(model: ModelService = Depends(get_model)):
    print(model.generate_audio("test"))
    return "success"
