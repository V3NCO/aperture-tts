class ModelLoader:
    def __init__(self):
        from style_bert_vits2.tts_model import TTSModel, Languages
        from pathlib import Path
        from style_bert_vits2.nlp import bert_models
        import nltk

        nltk.download('averaged_perceptron_tagger_eng')
        assets_root = Path("glados-model/Models/Style-Bert_VITS2/Portal_GLaDOS_v1")

        bert_models.load_model(Languages.EN, "deberta-v3-large")
        bert_models.load_tokenizer(Languages.EN, "deberta-v3-large")
        model = TTSModel(
            model_path=assets_root / "Portal_GLaDOS_v1_e782_s50000.safetensors",
            config_path=assets_root / "config.json",
            style_vec_path=assets_root / "style_vectors.npy",
            device="cpu",
        )

        self.model = model

    def generate_audio(self, text: str, style: str = "Neutral"):
        from style_bert_vits2.tts_model import Languages
        sr, audio = self.model.infer(text=text, language=Languages.EN, style=style)
        return sr,audio
