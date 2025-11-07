from style_bert_vits2.tts_model import TTSModel, Languages
from pathlib import Path
from IPython.display import Audio, display
from style_bert_vits2.nlp import bert_models

def main():
    assets_root = Path("Model")

    bert_models.load_model(Languages.EN, "deberta-v3-large")
    bert_models.load_tokenizer(Languages.EN, "deberta-v3-large")
    model = TTSModel(
        model_path=assets_root / "Portal_GLaDOS_v1_e782_s50000.safetensors",
        config_path=assets_root / "config.json",
        style_vec_path=assets_root / "style_vectors.npy",
        device="cpu",
    )




    sr, audio = model.infer(text="hello there", language=Languages.EN)
    with open('/tmp/test.wav', 'wb') as f:
        f.write(Audio(audio, rate=sr).data)


if __name__ == "__main__":
    main()
