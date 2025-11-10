class ModelService:
    def __init__(self, model):
        self.model = model

    def generate_audio(self, text):
        return self.model.generate_audio(text)
