import speech_recognition as sr
import pyttsx3
import time

class JarvisAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Adjusts to room noise
        self.recognizer.dynamic_energy_threshold = True
        
        # Set Voice Properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id) 
        self.engine.setProperty('rate', 175)

    def speak(self, text):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                query = self.recognizer.recognize_google(audio)
                return query.lower()
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return ""
            except Exception as e:
                print(f"Error: {e}")
                return ""

    def run(self):
        self.speak("System migration complete. All modules are online.")
        while True:
            command = self.listen()
            
            # Flexible Wake-Word Detection
            if any(word in command for word in ["jarvis", "jarv", "hello"]):
                self.speak("At your service, sir. How can I help?")
                
                # Nested logic for follow-up commands
                task = self.listen()
                if "status" in task:
                    self.speak("All systems are operational. CPU load is nominal.")
                elif "exit" in task or "sleep" in task:
                    self.speak("Understood. Entering standby mode.")
                    break
                elif task != "":
                    self.speak(f"I heard you say: {task}. Shall I search for that?")

if __name__ == "__main__":
    jarvis = JarvisAssistant()
    jarvis.run()
