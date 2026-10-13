
import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

print("Available voices:")

for index, voice in enumerate(voices):
    print(index, voice.name, voice.id)

text = "Hello! Welcome to UniAssist. How can I help you today?"

engine.say(text)
engine.runAndWait()

print("Voice test completed.")
