# Jarvis AI Assistant

A cross-platform, multi-functional voice assistant with a focus on privacy, offline capabilities, and graceful degradation.

---

## 🚀 Key Features

### 📝 Productivity & Organization
* **Persistent Notes:** "Take a note, remember to buy milk" / "Read my notes" / "Clear notes." Notes are saved to a JSON file to persist between sessions.
* **Smart Reminders:** "Remind me in 5 minutes to check the oven." Features spoken alerts and automatic restoration of pending reminders on startup.
* **Math Calculator:** Understands natural speech for operations like "What is 25 squared divided by 5" or "square root of 144."
* **News Headlines:** Pulls top stories via NewsAPI with "What's the news?" (Requires a free API key).

### 📂 System & Media Control
* **File Management:** "List files," "Find file resume," or "Open file budget."
* **Media Playback:** Priority search in your local `~/Music` folder with an automatic fallback to YouTube search.
* **Hardware Control:** "Set volume to 60," "Mute," or "Set brightness to 80." Works across macOS, Linux, and Windows.

### 🧠 Intelligent Core
* **Better Wake-Word Detection:** Uses **Picovoice Porcupine** (offline/accurate) if an API key is provided; falls back to standard keyword detection otherwise.
* **Offline Speech Recognition:** Automatically utilizes **Vosk** for fast, private processing if the model is downloaded; falls back to Google STT.
* **AI Fallback:** Unknown commands are intelligently handled by **Claude** for a natural spoken reply instead of an error.

---

## 🛠 Installation

### 1. Install Dependencies
Ensure you have Python installed, then run the following command to install the required libraries:

```bash
pip install SpeechRecognition pyttsx3 wikipedia requests pvporcupine pyaudio vosk anthropic
