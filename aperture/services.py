class ModelService:
    def __init__(self, model):
        self.model = model

    def generate_audio(self, text, style):
        return self.model.generate_audio(text=text, style=style)
