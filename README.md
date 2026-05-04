# AI-Voice
 
# 🎙️ AI Voice Assistant (Jarvis)

A simple AI-powered voice assistant that listens to your voice, processes it using AI, and responds with speech.

---

##  How to Run This

###  Install Dependencies

Make sure you have the necessary libraries installed:

```bash
pip install speechrecognition pyttsx3 google-generativeai pyaudio

```
Windows Users (PyAudio Fix)

If pyaudio fails on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

Execution

Run the script using:
```bash
python jarvis.py
``` 
File Structure of jarvis 
 
## 🛠️ Project Structure
```text
ai-voice-jarvis/
├── jarvis.py           # Main entry point for the assistant
├── jarvis_v2.py        # Optimized version with improved error handling
├── jarvis_engine/      # Core logic and module functions
│   └── core.py
├── config.py           # Configuration and API Key management
└── requirements.txt    # List of necessary Python libraries
