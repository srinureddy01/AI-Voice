# JARVIS AI Voice Assistant 🎙️

An intelligent, voice-activated assistant built with Python. This version marks a significant migration from functional scripting to a robust Class-based architecture.

##   Latest Updates

### 1. Object-Oriented Migration
The core logic has been refactored into the `JarvisAssistant` class. 
* **Scalability:** Makes it easier to add new features (like API integrations) without cluttering the main loop.
* **State Management:** Better handling of the assistant's "status" and voice properties.

### 2. Intelligent Ambient Noise Calibration
* Added `recognizer.dynamic_energy_threshold = True`.
* **Benefit:** JARVIS now dynamically adjusts to background noise in real-time, reducing false triggers in noisy environments.

### 3. Optimized Listening Logic
* **Timeout Controls:** Implemented `phrase_time_limit=5`.
* **Effect:** Prevents the assistant from "hanging" or listening indefinitely. If no speech is detected within the window, it resets to standby mode.

### 4. Natural Speech Synthesis
* **Adjusted Rate:** Set speech velocity to `175` wpm.
* **Tone:** This provides a more professional, crisp response profile compared to the default system speed.

### 5. Multi-Stage Command Handling
* The system now supports **Nested Listening**. 
* **Flow:** Wake Word Detection ➔ Acknowledgment ➔ Task Command. This mimics a more natural human-to-AI interaction.

---

##   Requirements
- `SpeechRecognition`
- `pyttsx3`
- `PyAudio` (Required for Microphone access)

##   Quick Start
```python
from jarvis import JarvisAssistant

bot = JarvisAssistant()
bot.run()
