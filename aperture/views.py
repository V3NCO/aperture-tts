from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel
from aperture.services import ModelService
from aperture.app_services import get_model
from IPython.display import Audio
from typing import Literal

api_router = APIRouter()

class ModelParams(BaseModel):
    text: str
    style: Literal["Neutral", "Deep", "Standard", "Standard_02", "Light"] = Query(default="Neutral")

@api_router.get('/tts', response_class=Response)
async def index(
    params: ModelParams,
    model: ModelService = Depends(get_model)
):
    sr,audio = model.generate_audio(text=params.text, style=params.style)
    print(sr)
    print(audio)
    return Response(content=Audio(audio, rate=sr).data, media_type="audio/wav")
