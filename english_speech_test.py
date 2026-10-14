
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

print("Loading English speech model...")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

print("Model loaded successfully!")
print("Speak in English for 10 seconds.")

audio = sd.rec(
    int(10 * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=2
)

sd.wait()

audio_bytes = audio.tobytes()

if recognizer.AcceptWaveform(audio_bytes):
    result = json.loads(recognizer.Result())
else:
    result = json.loads(recognizer.FinalResult())

text = result.get("text", "")

print("\nRecognized English text:")
print(text if text else "No speech recognized. Please try again.")
