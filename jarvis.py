import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from config import API_KEY

# Setup Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Setup Voice Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Index 0 is usually a male voice, 1 is usually female
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 180) # Speed of speech

def speak(text):
    """Converts text to speech and prints it."""
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for audio and converts it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-US')
        print(f"You: {query}")
        return query.lower()
    except Exception:
        return ""

def get_ai_response(prompt):
    """Sends text to Gemini and gets a concise response."""
    try:
        # We tell the AI to act like Jarvis and keep it short for speech
        context = "Respond as JARVIS from Iron Man. Keep it brief and professional."
        response = model.generate_content(f"{context} User says: {prompt}")
        return response.text
    except Exception as e:
        return "I'm having trouble connecting to my servers, sir."

if __name__ == "__main__":
    speak("Systems initialized. JARVIS is online.")
    
    while True:
        # Continuous listening for the wake word
        input_text = listen()
        
        if "jarvis" in input_text:
            speak("At your service. What do you need?")
            
            # Now listen for the actual command
            command = listen()
            
            if command:
                if "exit" in command or "stop" in command:
                    speak("Shutting down systems. Goodbye, sir.")
                    break
                
                # Get response from AI and speak it
                reply = get_ai_response(command)
                speak(reply)