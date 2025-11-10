from aperture.app import model
from aperture.services import ModelService

async def get_model():
    return ModelService(model=model)
