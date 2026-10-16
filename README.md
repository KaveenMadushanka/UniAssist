# UniAssist — University Student Support Chatbot

UniAssist is an offline university student support chatbot developed using Python. It helps students explore general university information through a simple graphical user interface.

## Features

- Student categories: A/L Student, University Student, and General
- University selection
- FAQ-based responses using local JSON data
- English and Sinhala text interaction
- Offline English speech recognition using Vosk
- English voice output using pyttsx3
- Microphone input using sounddevice
- Typewriter effect for chatbot responses
- Modern graphical user interface built with Tkinter

## Technologies Used

- Python
- Tkinter
- JSON
- Vosk
- sounddevice
- NumPy
- pyttsx3

## Project Structure

```text
UniAssist/
├── main.py
├── chatbot.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── general_faq.json
│   └── university_info.json
└── models/
    └── vosk-model-small-en-us-0.15/
```

## Installation

1. Install Python 3.12.
2. Clone or download this repository.
3. Open the project folder in VS Code.
4. Create and activate a Python virtual environment.
5. Install the required packages:

```bash
python -m pip install -r requirements.txt
```

6. Ensure the Vosk English speech model is available in the `models` directory.

### Download the Vosk Speech Recognition Model

UniAssist uses the Vosk English speech recognition model for offline microphone input.

1. Download the English model from the official Vosk website: https://alphacephei.com/vosk/models
2. Download `vosk-model-small-en-us-0.15`.
3. Extract the downloaded ZIP file.
4. Place the extracted model folder inside the project's `models` directory.

The expected folder structure is:

```text
UniAssist/
└── models/
    └── vosk-model-small-en-us-0.15/
```

Make sure the model folder contains the required Vosk model files before running the application.
## Run the Application

```bash
python main.py
```

## Notes

- Speech recognition works offline using the locally stored Vosk model.
- English voice output uses the available Windows speech voices.
- University-specific information should be verified using official university sources.
- Microphone availability and Windows audio settings may affect voice features.

## Project Purpose

This project was developed as a Python learning and university coursework project to explore chatbot logic, GUI development, local data handling, and offline speech technologies.
