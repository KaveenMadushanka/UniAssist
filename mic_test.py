
import sounddevice as sd
import numpy as np

print("Recording for 5 seconds. Please speak now...")

audio = sd.rec(
    int(5 * 16000),
    samplerate=16000,
    channels=1,
    dtype="float32",
    device=2
)

sd.wait()

if np.max(np.abs(audio)) > 0.01:
    print("Microphone test passed! Voice detected.")
else:
    print("No clear voice detected. Check your microphone.")

print("Recording test completed.")
