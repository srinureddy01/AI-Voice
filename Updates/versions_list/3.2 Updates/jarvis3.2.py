import speech_recognition as sr
import pyttsx3
import time
import webbrowser
import datetime
import random
import threading

# Optional: For real weather, install requests (pip install requests) and get an API key
# import requests

class JarvisAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Voice settings
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id) 
        self.engine.setProperty('rate', 175)

        self.active = True  # Controls main loop
        self.timer_thread = None

    def speak(self, text):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout=5):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                query = self.recognizer.recognize_google(audio)
                return query.lower()
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return ""
            except Exception as e:
                print(f"Error: {e}")
                return ""

    def tell_time(self):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")

    def tell_date(self):
        return datetime.datetime.now().strftime("%B %d, %Y")

    def tell_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field.",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you call a fish with no eyes? A fsh."
        ]
        return random.choice(jokes)

    def open_website(self, site_name):
        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com"
        }
        for key, url in sites.items():
            if key in site_name:
                webbrowser.open(url)
                return f"Opening {key}."
        webbrowser.open(f"https://www.{site_name.replace(' ', '')}.com")
        return f"Searching for {site_name}."

    def search_wikipedia(self, query):
        try:
            import wikipedia
            summary = wikipedia.summary(query, sentences=1)
            return summary
        except:
            return "Sorry, I could not find that on Wikipedia."

    def set_timer(self, seconds):
        def timer_function():
            time.sleep(seconds)
            self.speak("Time is up!")
        self.timer_thread = threading.Thread(target=timer_function)
        self.timer_thread.start()
        return f"Timer set for {seconds} seconds."

    def get_weather(self):
        # For real weather, use an API like OpenWeatherMap
        # This is a simulated version
        return "It's 22 degrees Celsius and sunny."

    def process_command(self, command):
        if not command:
            return

        print(f"Command: {command}")

        if "time" in command:
            self.speak(f"The time is {self.tell_time()}")
        
        elif "date" in command:
            self.speak(f"Today's date is {self.tell_date()}")
        
        elif "joke" in command:
            self.speak(self.tell_joke())
        
        elif "open" in command:
            if "google" in command:
                self.speak(self.open_website("google"))
            elif "youtube" in command:
                self.speak(self.open_website("youtube"))
            else:
                self.speak(self.open_website(command.replace("open", "").strip()))
        
        elif "wikipedia" in command or "wiki" in command:
            search_term = command.replace("wikipedia", "").replace("wiki", "").strip()
            if search_term:
                self.speak(f"Searching Wikipedia for {search_term}")
                result = self.search_wikipedia(search_term)
                self.speak(result)
            else:
                self.speak("What should I search on Wikipedia?")
        
        elif "timer" in command:
            words = command.split()
            for w in words:
                if w.isdigit():
                    secs = int(w)
                    self.speak(self.set_timer(secs))
                    return
            self.speak("Please specify seconds, for example: set timer for 10 seconds.")
        
        elif "weather" in command:
            self.speak(self.get_weather())
        
        elif "help" in command:
            self.speak("I can tell time and date, tell jokes, open websites, search Wikipedia, set timers, and give weather.")
        
        elif "exit" in command or "goodbye" in command or "sleep" in command:
            self.speak("Goodbye sir. Shutting down.")
            self.active = False
        
        else:
            self.speak(f"I heard you say: {command}. Say 'help' to see what I can do.")

    def run(self):
        self.speak("System migration complete. All modules are online.")
        self.speak("Say 'Jarvis' to wake me up.")

        while self.active:
            wake_command = self.listen(timeout=3)
            
            # Wake word detection
            if any(word in wake_command for word in ["jarvis", "jarv", "hey jarvis"]):
                self.speak("Yes sir, how can I help?")
                
                # Listen for a real command
                task = self.listen(timeout=5)
                if task:
                    self.process_command(task)
                else:
                    self.speak("I didn't hear a command. Say help for options.")
            elif "exit" in wake_command or "goodbye" in wake_command:
                self.speak("Shutting down.")
                self.active = False
            time.sleep(0.5)

if __name__ == "__main__":
    jarvis = JarvisAssistant()
    jarvis.run()
