import speech_recognition as sr
import pyttsx3
import time
import webbrowser
import datetime
import random
import threading
import subprocess
import os
import json
import math
import re
import sys

# ─────────────────────────────────────────────
#  Optional heavy imports (graceful fallback)
# ─────────────────────────────────────────────
try:
    import wikipedia
    WIKIPEDIA_OK = True
except ImportError:
    WIKIPEDIA_OK = False

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    import pvporcupine
    import pyaudio
    import struct
    PORCUPINE_OK = True
except ImportError:
    PORCUPINE_OK = False

try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

try:
    import vosk
    VOSK_OK = True
except ImportError:
    VOSK_OK = False

# Automation imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_OK = True
except ImportError:
    SELENIUM_OK = False

try:
    import pyautogui
    PYAutoGUI_OK = True
except ImportError:
    PYAutoGUI_OK = False

# ─────────────────────────────────────────────
#  Config – edit these to taste
# ─────────────────────────────────────────────
NEWS_API_KEY       = "YOUR_NEWSAPI_KEY"
OPENWEATHER_KEY    = "YOUR_OPENWEATHER_KEY"
PICOVOICE_KEY      = "YOUR_PICOVOICE_KEY"
ANTHROPIC_KEY      = "YOUR_ANTHROPIC_KEY"
VOSK_MODEL_PATH    = "vosk-model-small-en-us-0.15"
NOTES_FILE         = os.path.join(os.path.expanduser("~"), "jarvis_notes.json")
REMINDERS_FILE     = os.path.join(os.path.expanduser("~"), "jarvis_reminders.json")
DEFAULT_MUSIC_DIR  = os.path.join(os.path.expanduser("~"), "Music")
AUTOMATION_CONFIG_FILE = os.path.join(os.path.expanduser("~"), "jarvis_automation.json")

# User preferences for automation
USER_DATA = {
    "name": "",
    "email": "",
    "phone": "",
    "address": "",
    "credit_card": {
        "number": "",
        "expiry": "",
        "cvv": ""
    },
    "preferred_browser": "chrome"  # chrome, firefox, edge
}

# ══════════════════════════════════════════════
#  Helper utilities
# ══════════════════════════════════════════════

def load_json(path: str) -> dict | list:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_user_data():
    global USER_DATA
    data = load_json(AUTOMATION_CONFIG_FILE)
    if data:
        USER_DATA.update(data)

def save_user_data():
    save_json(AUTOMATION_CONFIG_FILE, USER_DATA)

# ══════════════════════════════════════════════
#  Automation Class for Browser Controls
# ══════════════════════════════════════════════

class BrowserAutomation:
    def __init__(self, assistant):
        self.assistant = assistant
        self.driver = None
        self.wait = None
        
    def init_driver(self, browser=None):
        """Initialize the web driver"""
        if not SELENIUM_OK:
            self.assistant.speak("Selenium is not installed. Please run: pip install selenium")
            return False
            
        try:
            browser = browser or USER_DATA.get("preferred_browser", "chrome")
            
            if browser == "chrome":
                options = webdriver.ChromeOptions()
                options.add_argument("--disable-notifications")
                options.add_experimental_option("detach", True)
                self.driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                options.set_preference("dom.webnotifications.enabled", False)
                self.driver = webdriver.Firefox(options=options)
            elif browser == "edge":
                options = webdriver.EdgeOptions()
                options.add_argument("--disable-notifications")
                self.driver = webdriver.Edge(options=options)
            else:
                self.driver = webdriver.Chrome()
                
            self.wait = WebDriverWait(self.driver, 15)
            return True
        except Exception as e:
            self.assistant.speak(f"Failed to initialize browser: {str(e)}")
            return False
    
    def book_ticket(self, source, destination, date=None):
        """Automate ticket booking (example: MakeMyTrip, RedBus, etc.)"""
        if not self.init_driver():
            return "Browser automation not available"
        
        try:
            self.assistant.speak(f"Booking ticket from {source} to {destination}")
            
            # Open a travel website (example using MakeMyTrip)
            self.driver.get("https://www.makemytrip.com/")
            time.sleep(3)
            
            # Close any popups
            try:
                close_btn = self.driver.find_element(By.CLASS_NAME, "close")
                close_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Click on Flights
            flights_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-cy='menu_Flights']")))
            flights_tab.click()
            time.sleep(2)
            
            # Enter source
            from_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='From']")))
            from_input.click()
            time.sleep(1)
            from_input.clear()
            from_input.send_keys(source)
            time.sleep(2)
            from_input.send_keys(Keys.ENTER)
            
            # Enter destination
            to_input = self.driver.find_element(By.XPATH, "//input[@placeholder='To']")
            to_input.click()
            to_input.clear()
            to_input.send_keys(destination)
            time.sleep(2)
            to_input.send_keys(Keys.ENTER)
            
            # Select date if provided
            if date:
                date_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Departure']")
                date_input.click()
                # Simple date selection - assumes format: "19 March 2025"
                date_elem = self.driver.find_element(By.XPATH, f"//div[@aria-label='{date}']")
                date_elem.click()
            
            # Search for flights
            search_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cy='submit']")))
            search_btn.click()
            
            self.assistant.speak("Searching for flights. Please check the browser to continue with payment.")
            return "Ticket booking initiated. Complete payment in browser window."
            
        except Exception as e:
            self.assistant.speak(f"Error during booking: {str(e)}")
            return f"Booking failed: {str(e)}"
    
    def order_food(self, item, platform="swiggy"):
        """Order food from Swiggy or Zomato"""
        if not self.init_driver():
            return "Browser automation not available"
        
        try:
            if platform == "swiggy":
                self.driver.get("https://www.swiggy.com/")
            else:
                self.driver.get("https://www.zomato.com/")
                
            self.assistant.speak(f"Searching for {item} on {platform}")
            time.sleep(5)  # Let the page load
            
            # Search for item
            search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='search']")))
            search_box.clear()
            search_box.send_keys(item)
            search_box.send_keys(Keys.ENTER)
            
            self.assistant.speak(f"Found results for {item}. Please complete your order in the browser.")
            return f"Food ordering initiated for {item}"
            
        except Exception as e:
            return f"Food ordering failed: {str(e)}"
    
    def shop_online(self, product, platform="amazon"):
        """Shop for products on Amazon or Flipkart"""
        if not self.init_driver():
            return "Browser automation not available"
        
        try:
            if platform == "amazon":
                self.driver.get("https://www.amazon.com/")
            else:
                self.driver.get("https://www.flipkart.com/")
                
            self.assistant.speak(f"Searching for {product} on {platform}")
            time.sleep(3)
            
            # Handle popups/close buttons
            try:
                if platform == "amazon":
                    # Amazon might have location popup
                    pass
                elif platform == "flipkart":
                    close_btn = self.driver.find_element(By.XPATH, "//button[@class='_2KpZ6l _2doB4z']")
                    close_btn.click()
                    time.sleep(1)
            except:
                pass
            
            # Search for product
            search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
            search_box.clear()
            search_box.send_keys(product)
            search_box.send_keys(Keys.ENTER)
            
            self.assistant.speak(f"Found results for {product}. Please browse and complete purchase.")
            return f"Shopping initiated for {product}"
            
        except Exception as e:
            return f"Shopping failed: {str(e)}"
    
    def fill_form(self, form_url, form_data):
        """Automatically fill any form"""
        if not self.init_driver():
            return "Browser automation not available"
        
        try:
            self.driver.get(form_url)
            self.assistant.speak("Form opened. Filling in details...")
            time.sleep(3)
            
            # Find all input fields and fill
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            field_index = 0
            for field in inputs + textareas:
                if field.get_attribute("type") not in ["submit", "button", "reset", "hidden"]:
                    if field_index < len(form_data):
                        field.clear()
                        field.send_keys(form_data[field_index])
                        field_index += 1
                        
            self.assistant.speak("Form fields filled. Please review and submit.")
            return "Form filled successfully"
            
        except Exception as e:
            return f"Form filling failed: {str(e)}"
    
    def close_browser(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            return "Browser closed"
        return "No browser window open"
    
    def search_google(self, query):
        """Search Google for information"""
        if not self.init_driver():
            return "Browser automation not available"
        
        try:
            self.driver.get("https://www.google.com/")
            time.sleep(2)
            
            search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            
            self.assistant.speak(f"Searching Google for {query}")
            return f"Google search initiated for {query}"
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def download_youtube_video(self, url):
        """Download YouTube video using yt-dlp"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(DEFAULT_MUSIC_DIR, '%(title)s.%(ext)s'),
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.assistant.speak(f"Downloaded: {info.get('title', 'video')}")
                return f"Downloaded to {DEFAULT_MUSIC_DIR}"
        except ImportError:
            return "yt-dlp not installed. Run: pip install yt-dlp"
        except Exception as e:
            return f"Download failed: {str(e)}"
    
    def monitor_price(self, product_url, target_price):
        """Monitor product price and alert when drops"""
        if not REQUESTS_OK:
            return "Requests module required for price monitoring"
        
        def check_price():
            while True:
                try:
                    response = requests.get(product_url, timeout=10)
                    # This is simplified - would need proper scraping for real implementation
                    self.assistant.speak(f"Current price check would be performed here for {product_url}")
                    time.sleep(3600)  # Check every hour
                except:
                    time.sleep(3600)
        
        monitor_thread = threading.Thread(target=check_price, daemon=True)
        monitor_thread.start()
        return f"Price monitoring started for {product_url}"

# ══════════════════════════════════════════════
#  Main Assistant Class
# ══════════════════════════════════════════════

class JarvisAssistant:
    def __init__(self):
        # ── TTS engine ──────────────────────────────
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)
        self.engine.setProperty("rate", 175)

        # ── STT ─────────────────────────────────────
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        # ── Vosk offline recognizer (optional) ──────
        self.vosk_model = None
        if VOSK_OK and os.path.exists(VOSK_MODEL_PATH):
            self.vosk_model = vosk.Model(VOSK_MODEL_PATH)
            print("[INFO] Vosk offline STT loaded.")

        # ── Anthropic AI client (optional) ──────────
        self.ai_client = None
        if ANTHROPIC_OK and ANTHROPIC_KEY != "YOUR_ANTHROPIC_KEY":
            self.ai_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        # ── Browser Automation ──────────────────────
        self.automation = BrowserAutomation(self)
        load_user_data()

        # ── State ────────────────────────────────────
        self.active = True
        self.timer_thread = None
        self.reminder_threads = []
        self.notes = load_json(NOTES_FILE) if isinstance(load_json(NOTES_FILE), dict) else {}
        self.reminders = load_json(REMINDERS_FILE) if isinstance(load_json(REMINDERS_FILE), list) else []
        
        # Conversation context for follow-ups
        self.last_command = ""
        self.waiting_for_info = False
        self.pending_action = None
        self.collected_data = {}

        # Restore pending reminders on startup
        self._restore_reminders()

    # ──────────────────────────────────────────
    #  Speech
    # ──────────────────────────────────────────

    def speak(self, text: str):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout: int = 5) -> str:
        """Listen via Google Cloud STT, or fall back to Vosk if available."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("Listening…")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                return ""

        # Try Vosk offline first (faster, private)
        if self.vosk_model:
            try:
                rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
                rec.AcceptWaveform(audio.get_wav_data())
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    return text.lower()
            except Exception:
                pass

        # Fall back to Google
        try:
            return self.recognizer.recognize_google(audio).lower()
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return ""
        except Exception as e:
            print(f"[STT Error] {e}")
            return ""

    # ──────────────────────────────────────────
    #  Wake-word detection
    # ──────────────────────────────────────────

    def wait_for_wake_word_porcupine(self) -> bool:
        """Accurate offline wake-word via Picovoice (requires key)."""
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_KEY,
            keywords=["jarvis"]
        )
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )
        detected = False
        try:
            while self.active:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                if porcupine.process(pcm_unpacked) >= 0:
                    detected = True
                    break
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            porcupine.delete()
        return detected

    def wait_for_wake_word_simple(self) -> bool:
        """Keyword-matching fallback wake-word detection."""
        cmd = self.listen(timeout=3)
        return any(w in cmd for w in ["jarvis", "hey jarvis", "jarv", "travis"])

    def wait_for_wake_word(self) -> bool:
        if PORCUPINE_OK and PICOVOICE_KEY != "YOUR_PICOVOICE_KEY":
            return self.wait_for_wake_word_porcupine()
        return self.wait_for_wake_word_simple()

    # ──────────────────────────────────────────
    #  Time / Date
    # ──────────────────────────────────────────

    def tell_time(self) -> str:
        return datetime.datetime.now().strftime("%I:%M %p")

    def tell_date(self) -> str:
        return datetime.datetime.now().strftime("%B %d, %Y")

    # ──────────────────────────────────────────
    #  Jokes
    # ──────────────────────────────────────────

    def tell_joke(self) -> str:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field.",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What do you call a fish with no eyes? A fsh.",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why do programmers prefer dark mode? Because light attracts bugs.",
        ]
        return random.choice(jokes)

    # ──────────────────────────────────────────
    #  Web
    # ──────────────────────────────────────────

    def open_website(self, site_name: str) -> str:
        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://www.twitter.com",
            "spotify": "https://open.spotify.com",
            "amazon": "https://www.amazon.com",
            "flipkart": "https://www.flipkart.com",
            "swiggy": "https://www.swiggy.com",
            "zomato": "https://www.zomato.com",
            "makemytrip": "https://www.makemytrip.com",
        }
        for key, url in sites.items():
            if key in site_name:
                webbrowser.open(url)
                return f"Opening {key}."
        webbrowser.open(f"https://www.{site_name.replace(' ', '')}.com")
        return f"Opening {site_name}."

    def search_wikipedia(self, query: str) -> str:
        if not WIKIPEDIA_OK:
            return "Wikipedia module not installed. Run: pip install wikipedia"
        try:
            return wikipedia.summary(query, sentences=2)
        except Exception:
            return "Sorry, I could not find that on Wikipedia."

    # ──────────────────────────────────────────
    #  Weather (real API if key provided)
    # ──────────────────────────────────────────

    def get_weather(self, city: str = "New York") -> str:
        if REQUESTS_OK and OPENWEATHER_KEY != "YOUR_OPENWEATHER_KEY":
            try:
                url = (
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?q={city}&appid={OPENWEATHER_KEY}&units=metric"
                )
                data = requests.get(url, timeout=5).json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"It's {temp}°C with {desc} in {city}."
            except Exception:
                pass
        return "It's 22 degrees Celsius and sunny. (Simulated – add your OpenWeather key for real data.)"

    # ──────────────────────────────────────────
    #  News (NewsAPI)
    # ──────────────────────────────────────────

    def get_news(self, count: int = 5) -> str:
        if not REQUESTS_OK:
            return "requests module not installed. Run: pip install requests"
        if NEWS_API_KEY == "YOUR_NEWSAPI_KEY":
            return "Add your NewsAPI key in the config section to get real headlines."
        try:
            url = (
                f"https://newsapi.org/v2/top-headlines"
                f"?language=en&pageSize={count}&apiKey={NEWS_API_KEY}"
            )
            articles = requests.get(url, timeout=5).json().get("articles", [])
            headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles)]
            return "Here are today's top headlines: " + ". ".join(headlines)
        except Exception as e:
            return f"Could not fetch news: {e}"

    # ──────────────────────────────────────────
    #  Math calculator
    # ──────────────────────────────────────────

    def calculate(self, expression: str) -> str:
        expr = (expression
                .replace("plus", "+").replace("minus", "-")
                .replace("times", "*").replace("multiplied by", "*")
                .replace("divided by", "/").replace("over", "/")
                .replace("squared", "**2").replace("cubed", "**3")
                .replace("square root of", "math.sqrt(").replace("sqrt", "math.sqrt("))
        open_p = expr.count("math.sqrt(")
        close_p = expr.count(")")
        expr += ")" * (open_p - close_p)

        try:
            result = eval(expr, {"__builtins__": {}, "math": math})
            return f"The answer is {result}"
        except Exception:
            return "Sorry, I couldn't calculate that. Try rephrasing, e.g. '5 plus 3'."

    # ──────────────────────────────────────────
    #  Timer
    # ──────────────────────────────────────────

    def set_timer(self, seconds: int) -> str:
        def _run():
            time.sleep(seconds)
            self.speak("Timer complete! Time is up, sir.")
        self.timer_thread = threading.Thread(target=_run, daemon=True)
        self.timer_thread.start()
        mins, secs = divmod(seconds, 60)
        label = f"{mins} minute{'s' if mins != 1 else ''}" if mins else f"{secs} second{'s' if secs != 1 else ''}"
        return f"Timer set for {label}."

    def _parse_duration_seconds(self, command: str) -> int | None:
        total = 0
        matched = False
        for m in re.finditer(r"(\d+)\s*(hour|hr|minute|min|second|sec)s?", command):
            val, unit = int(m.group(1)), m.group(2)
            if unit in ("hour", "hr"):
                total += val * 3600
            elif unit in ("minute", "min"):
                total += val * 60
            else:
                total += val
            matched = True
        if not matched:
            nums = re.findall(r"\d+", command)
            if nums:
                return int(nums[-1])
        return total if matched else None

    # ──────────────────────────────────────────
    #  Notes
    # ──────────────────────────────────────────

    def add_note(self, content: str) -> str:
        key = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes[key] = content
        save_json(NOTES_FILE, self.notes)
        return f"Note saved: {content}"

    def read_notes(self) -> str:
        if not self.notes:
            return "You have no saved notes."
        recent = list(self.notes.items())[-5:]
        lines = [f"{ts}: {txt}" for ts, txt in recent]
        return "Your recent notes: " + ". ".join(lines)

    def clear_notes(self) -> str:
        self.notes = {}
        save_json(NOTES_FILE, self.notes)
        return "All notes cleared."

    # ──────────────────────────────────────────
    #  Reminders
    # ──────────────────────────────────────────

    def add_reminder(self, text: str, seconds: int) -> str:
        trigger_time = (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).isoformat()
        entry = {"text": text, "trigger": trigger_time, "done": False}
        self.reminders.append(entry)
        save_json(REMINDERS_FILE, self.reminders)
        self._schedule_reminder(entry)
        mins, secs = divmod(seconds, 60)
        label = f"{mins}m {secs}s" if mins else f"{secs}s"
        return f"Reminder set in {label}: {text}"

    def _schedule_reminder(self, entry: dict):
        delay = (datetime.datetime.fromisoformat(entry["trigger"]) - datetime.datetime.now()).total_seconds()
        if delay < 0:
            return
        def _fire():
            time.sleep(delay)
            if not entry.get("done"):
                self.speak(f"Reminder: {entry['text']}")
                entry["done"] = True
                save_json(REMINDERS_FILE, self.reminders)
        t = threading.Thread(target=_fire, daemon=True)
        t.start()
        self.reminder_threads.append(t)

    def _restore_reminders(self):
        for entry in self.reminders:
            if not entry.get("done"):
                self._schedule_reminder(entry)

    def list_reminders(self) -> str:
        pending = [r for r in self.reminders if not r.get("done")]
        if not pending:
            return "No pending reminders."
        lines = [f"{r['text']} at {r['trigger'][11:16]}" for r in pending]
        return "Pending reminders: " + "; ".join(lines)

    # ──────────────────────────────────────────
    #  System controls
    # ──────────────────────────────────────────

    def set_volume(self, level: int) -> str:
        level = max(0, min(100, level))
        if sys.platform == "darwin":
            os.system(f"osascript -e 'set volume output volume {level}'")
        elif sys.platform.startswith("linux"):
            os.system(f"amixer -q sset Master {level}%")
        elif sys.platform == "win32":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100, None)
            except Exception as e:
                return f"Could not set volume: {e}"
        return f"Volume set to {level} percent."

    def set_brightness(self, level: int) -> str:
        level = max(0, min(100, level))
        if sys.platform == "darwin":
            return f"Brightness adjustment on macOS requires additional tools. Value requested: {level}%"
        elif sys.platform.startswith("linux"):
            try:
                os.system(f"xrandr --output $(xrandr | grep ' connected' | awk '{{print $1}}' | head -1) --brightness {level/100:.2f}")
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                import wmi
                c = wmi.WMI(namespace="wmi")
                methods = c.WmiMonitorBrightnessMethods()[0]
                methods.WmiSetBrightness(level, 0)
            except Exception as e:
                return f"Could not set brightness: {e}"
        return f"Brightness set to {level} percent."

    def mute_volume(self) -> str:
        if sys.platform == "darwin":
            os.system("osascript -e 'set volume output muted true'")
        elif sys.platform.startswith("linux"):
            os.system("amixer -q sset Master mute")
        elif sys.platform == "win32":
            os.system("nircmd.exe mutesysvolume 1")
        return "Volume muted."

    def unmute_volume(self) -> str:
        if sys.platform == "darwin":
            os.system("osascript -e 'set volume output muted false'")
        elif sys.platform.startswith("linux"):
            os.system("amixer -q sset Master unmute")
        elif sys.platform == "win32":
            os.system("nircmd.exe mutesysvolume 0")
        return "Volume unmuted."

    # ──────────────────────────────────────────
    #  Music playback
    # ──────────────────────────────────────────

    def play_music(self, query: str = "") -> str:
        music_dir = os.path.expanduser(DEFAULT_MUSIC_DIR)
        if os.path.isdir(music_dir):
            files = [f for f in os.listdir(music_dir)
                     if f.endswith((".mp3", ".wav", ".flac", ".m4a", ".ogg"))]
            if files:
                if query:
                    match = next((f for f in files if query.lower() in f.lower()), None)
                    target = match or random.choice(files)
                else:
                    target = random.choice(files)
                path = os.path.join(music_dir, target)
                if sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                elif sys.platform.startswith("linux"):
                    subprocess.Popen(["xdg-open", path])
                elif sys.platform == "win32":
                    os.startfile(path)
                return f"Playing {target}."
        search = query or "music"
        webbrowser.open(f"https://www.youtube.com/results?search_query={search.replace(' ', '+')}")
        return f"Opening YouTube search for {search}."

    def pause_music(self) -> str:
        if sys.platform == "darwin":
            os.system("osascript -e 'tell application \"Music\" to pause'")
        elif sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
        return "Music paused."

    # ──────────────────────────────────────────
    #  File management
    # ──────────────────────────────────────────

    def list_files(self, directory: str = "~") -> str:
        path = os.path.expanduser(directory)
        try:
            items = os.listdir(path)
            files = [i for i in items if os.path.isfile(os.path.join(path, i))][:10]
            dirs = [i for i in items if os.path.isdir(os.path.join(path, i))][:5]
            result = ""
            if dirs: result += f"Folders: {', '.join(dirs)}. "
            if files: result += f"Files: {', '.join(files)}."
            return result or "Directory is empty."
        except Exception as e:
            return f"Could not read directory: {e}"

    def find_file(self, name: str, start: str = "~") -> str:
        root = os.path.expanduser(start)
        found = []
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                if name.lower() in fname.lower():
                    found.append(os.path.join(dirpath, fname))
                if len(found) >= 5:
                    break
        if found:
            return "Found: " + ", ".join(found)
        return f"No files matching '{name}' found."

    def open_file(self, name: str) -> str:
        result = self.find_file(name)
        if result.startswith("Found:"):
            path = result.replace("Found: ", "").split(",")[0].strip()
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", path])
            elif sys.platform == "win32":
                os.startfile(path)
            return f"Opening {os.path.basename(path)}."
        return result

    # ──────────────────────────────────────────
    #  Automation Functions (New)
    # ──────────────────────────────────────────

    def setup_user_profile(self) -> str:
        """Set up user profile for automated tasks"""
        self.speak("Let me set up your profile for automated tasks. Please tell me your name.")
        name = self.listen(timeout=5)
        if name:
            USER_DATA["name"] = name
        
        self.speak("What is your email address?")
        email = self.listen(timeout=5)
        if email:
            USER_DATA["email"] = email
        
        self.speak("What is your phone number?")
        phone = self.listen(timeout=5)
        if phone:
            USER_DATA["phone"] = phone
        
        save_user_data()
        return "Profile setup complete. You can now use automation features."

    def book_ticket_automation(self, command: str) -> str:
        """Handle ticket booking requests"""
        # Extract source and destination
        source_match = re.search(r"from (\w+)", command)
        dest_match = re.search(r"to (\w+)", command)
        
        source = source_match.group(1) if source_match else "New York"
        destination = dest_match.group(1) if dest_match else "London"
        
        return self.automation.book_ticket(source, destination)

    def order_food_automation(self, command: str) -> str:
        """Handle food ordering"""
        # Extract food item
        item_match = re.search(r"order (.+) from (swiggy|zomato)", command)
        platform_match = re.search(r"(swiggy|zomato)", command)
        
        if item_match:
            item = item_match.group(1)
            platform = platform_match.group(1) if platform_match else "swiggy"
        else:
            item = command.replace("order", "").replace("food", "").strip()
            platform = "swiggy"
        
        return self.automation.order_food(item, platform)

    def shop_automation(self, command: str) -> str:
        """Handle shopping"""
        product_match = re.search(r"buy (.+) on (amazon|flipkart)", command)
        platform_match = re.search(r"(amazon|flipkart)", command)
        
        if product_match:
            product = product_match.group(1)
            platform = platform_match.group(1) if platform_match else "amazon"
        else:
            product = command.replace("buy", "").replace("shop", "").strip()
            platform = "amazon"
        
        return self.automation.shop_online(product, platform)

    def google_search_automation(self, command: str) -> str:
        """Handle Google search"""
        query = command.replace("google", "").replace("search for", "").replace("search", "").strip()
        if not query:
            self.speak("What would you like me to search for?")
            query = self.listen(timeout=5)
        
        if query:
            return self.automation.search_google(query)
        return "No search query provided."

    def close_browser_automation(self) -> str:
        """Close browser window"""
        return self.automation.close_browser()

    # ──────────────────────────────────────────
    #  AI fallback (Anthropic Claude)
    # ──────────────────────────────────────────

    def ask_ai(self, command: str) -> str:
        if not self.ai_client:
            return f"I heard: '{command}'. I don't know that command yet. Say 'help' for options."
        try:
            msg = self.ai_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                system=(
                    "You are Jarvis, a concise voice assistant. "
                    "Reply in 1-2 short sentences suitable for text-to-speech. "
                    "No markdown, no lists."
                ),
                messages=[{"role": "user", "content": command}],
            )
            return msg.content[0].text
        except Exception as e:
            return f"AI unavailable: {e}"

    # ──────────────────────────────────────────
    #  Command router
    # ──────────────────────────────────────────

    def process_command(self, command: str):
        if not command:
            return

        print(f"[CMD] {command}")
        c = command.lower()

        # ── Automation Commands (New) ──────────────────
        
        # Ticket Booking
        if any(w in c for w in ["book a ticket", "book ticket", "buy ticket", "flight booking"]):
            self.speak(self.book_ticket_automation(c))
        
        # Food Ordering
        elif any(w in c for w in ["order food", "order from swiggy", "order from zomato"]):
            self.speak(self.order_food_automation(c))
        
        # Online Shopping
        elif any(w in c for w in ["buy", "shop for", "purchase", "shopping"]):
            if any(w in c for w in ["amazon", "flipkart"]):
                self.speak(self.shop_automation(c))
            else:
                self.speak("Which platform should I use? Amazon or Flipkart?")
                platform = self.listen(timeout=5)
                if platform:
                    self.speak(self.shop_automation(f"buy {c.replace('buy', '')} on {platform}"))
        
        # Google Search
        elif "google" in c and "search" in c:
            self.speak(self.google_search_automation(c))
        
        # Close Browser
        elif "close browser" in c or "close tab" in c:
            self.speak(self.close_browser_automation())
        
        # Setup Profile
        elif "setup profile" in c or "configure my profile" in c:
            self.speak(self.setup_user_profile())

        # ── Time / Date ──────────────────────────────
        elif "time" in c and "timer" not in c:
            self.speak(f"The time is {self.tell_time()}")

        elif "date" in c:
            self.speak(f"Today is {self.tell_date()}")

        # ── Joke ─────────────────────────────────────
        elif "joke" in c:
            self.speak(self.tell_joke())

        # ── Website ───────────────────────────────────
        elif "open" in c:
            site = c.replace("open", "").strip()
            self.speak(self.open_website(site))

        # ── Wikipedia ─────────────────────────────────
        elif "wikipedia" in c or "wiki" in c:
            term = re.sub(r"\b(wikipedia|wiki|search|look up)\b", "", c).strip()
            if term:
                self.speak(f"Searching Wikipedia for {term}.")
                self.speak(self.search_wikipedia(term))
            else:
                self.speak("What should I search on Wikipedia?")

        # ── Weather ───────────────────────────────────
        elif "weather" in c:
            city_match = re.search(r"weather (?:in|for|at) (.+)", c)
            city = city_match.group(1).strip() if city_match else "New York"
            self.speak(self.get_weather(city))

        # ── News ──────────────────────────────────────
        elif "news" in c or "headline" in c:
            self.speak(self.get_news())

        # ── Math ──────────────────────────────────────
        elif any(w in c for w in ["calculate", "what is", "compute", "equals", "plus", "minus",
                                   "times", "divided", "sqrt", "square root", "squared", "cubed"]):
            expr = re.sub(r"\b(calculate|what is|compute|whats)\b", "", c).strip()
            self.speak(self.calculate(expr))

        # ── Timer ─────────────────────────────────────
        elif "timer" in c:
            secs = self._parse_duration_seconds(c)
            if secs:
                self.speak(self.set_timer(secs))
            else:
                self.speak("Please say a duration, like 'set timer for 2 minutes'.")

        # ── Notes ─────────────────────────────────────
        elif "take a note" in c or "add a note" in c or "note that" in c or "write down" in c:
            content = re.sub(r"\b(take a note|add a note|note that|write down|note)\b", "", c).strip()
            if content:
                self.speak(self.add_note(content))
            else:
                self.speak("What should I note?")
                content = self.listen()
                if content:
                    self.speak(self.add_note(content))

        elif "read my notes" in c or "show notes" in c or "what are my notes" in c:
            self.speak(self.read_notes())

        elif "clear notes" in c or "delete notes" in c:
            self.speak(self.clear_notes())

        # ── Reminders ─────────────────────────────────
        elif "remind me" in c or "set a reminder" in c:
            secs = self._parse_duration_seconds(c)
            text = re.sub(
                r"\b(remind me|set a reminder|reminder|to|in|after|for)\b|\d+\s*(hour|hr|minute|min|second|sec)s?",
                "", c
            ).strip() or "unnamed reminder"
            if secs:
                self.speak(self.add_reminder(text, secs))
            else:
                self.speak("How long until the reminder? For example: remind me in 5 minutes to check the oven.")

        elif "list reminders" in c or "my reminders" in c:
            self.speak(self.list_reminders())

        # ── Volume ────────────────────────────────────
        elif "volume" in c:
            if "mute" in c:
                self.speak(self.mute_volume())
            elif "unmute" in c:
                self.speak(self.unmute_volume())
            else:
                nums = re.findall(r"\d+", c)
                if nums:
                    self.speak(self.set_volume(int(nums[0])))
                else:
                    self.speak("Please specify a volume level, like 'set volume to 50'.")

        # ── Brightness ────────────────────────────────
        elif "brightness" in c:
            nums = re.findall(r"\d+", c)
            if nums:
                self.speak(self.set_brightness(int(nums[0])))
            else:
                self.speak("Please specify a brightness level, like 'set brightness to 70'.")

        # ── Music ─────────────────────────────────────
        elif "play" in c and ("music" in c or "song" in c or "audio" in c):
            query = re.sub(r"\b(play|music|song|audio|some)\b", "", c).strip()
            self.speak(self.play_music(query))

        elif "pause" in c and "music" in c:
            self.speak(self.pause_music())

        # ── Files ─────────────────────────────────────
        elif "list files" in c or "what files" in c or "show files" in c:
            folder_match = re.search(r"(?:in|from|inside) (.+)", c)
            folder = folder_match.group(1).strip() if folder_match else "~"
            self.speak(self.list_files(folder))

        elif "find file" in c or "search for file" in c:
            name = re.sub(r"\b(find|search for|file|named|called)\b", "", c).strip()
            self.speak(self.find_file(name))

        elif "open file" in c:
            name = c.replace("open file", "").strip()
            self.speak(self.open_file(name))

        # ── Help ──────────────────────────────────────
        elif "help" in c:
            self.speak(
                "I can do many things: tell time and date, tell jokes, open websites, "
                "search Wikipedia, get weather and news, do math, set timers and reminders, "
                "take notes, control volume and brightness, play music, manage files, "
                "AND NOW I can also: book tickets, order food, shop online, search Google, "
                "and automate browser tasks. Just ask me like 'book a ticket from New York to London'"
                "or 'order pizza from Swiggy' or 'buy shoes on Amazon'."
            )

        # ── Exit ──────────────────────────────────────
        elif any(w in c for w in ["exit", "goodbye", "shut down", "sleep", "bye"]):
            self.automation.close_browser()  # Close browser on exit
            self.speak("Goodbye sir. All systems going offline.")
            self.active = False

        # ── AI fallback ───────────────────────────────
        else:
            self.speak(self.ask_ai(command))

    # ──────────────────────────────────────────
    #  Main loop
    # ──────────────────────────────────────────

    def run(self):
        self.speak("System migration complete. All modules are online.")
        self.speak("I now have automation capabilities. Say Jarvis to wake me up.")
        self.speak("You can ask me to book tickets, order food, shop online, and more.")

        while self.active:
            if self.wait_for_wake_word():
                self.speak("Yes sir, how can I help?")
                task = self.listen(timeout=6)
                if task:
                    self.process_command(task)
                else:
                    self.speak("I didn't catch that. Say help for a list of commands.")
            time.sleep(0.3)


# ══════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════

if __name__ == "__main__":
    jarvis = JarvisAssistant()
    jarvis.run()
