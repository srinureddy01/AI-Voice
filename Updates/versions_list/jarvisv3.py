import asyncio
import edge_tts
import pygame
import speech_recognition as sr
from google import genai
import os
import time
from config import API_KEY

# Setup
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 
VOICE = "en-GB-ThomasNeural"
OUTPUT_FILE = "response.mp3"

def play_audio():
    pygame.mixer.init()
    if os.path.exists(OUTPUT_FILE): 
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()

async def speak(text):
    """Generates and plays the voice response."""
    print(f"JARVIS: {text}")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)
    play_audio()
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

def listen(timeout_val=None, recognizer=None, microphone=None):
    """Listens for the user's voice."""
    if recognizer is None:
        recognizer = sr.Recognizer()
    
    with microphone as source:
        # Reduced duration for faster response
        try:
            audio = recognizer.listen(source, timeout=timeout_val, phrase_time_limit=5)
            query = recognizer.recognize_google(audio, language='en-US')
            print(f"User: {query}")
            return query.lower()
        except:
            return ""

async def main():
    await speak("Systems initialized. JARVIS is online.")
    is_active = False 
    
    # Initialize these once to save time in the loop
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    # Pre-adjust for noise once at startup
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)

    while True:
        if not is_active:
            print("\n[ STANDBY: Waiting for 'Jarvis'... ]")
            wake_word = listen(recognizer=r, microphone=mic)
            
            # --- FLEXIBLE WAKE WORD LOGIC ---
            # Checks for common variations or if the phrase starts with 'j'
            wake_variants = ["jarvis", "jar", "jars", "java", "jarv"]
            
            # Logic: If any variant is in the text OR the text starts with 'j'
            should_wake = any(variant in wake_word for variant in wake_variants) or wake_word.startswith("j ")
            
            if should_wake:
                is_active = True
                await speak("At your service, sir.")
        
        else:
            print("\n[ ACTIVE: Listening for your command... ]")
            command = listen(timeout_val=10, recognizer=r, microphone=mic)
            
            if not command:
                print("No activity detected. Returning to standby.")
                is_active = False
                continue

            if any(word in command for word in ["stop", "sleep", "exit", "go to sleep"]):
                await speak("Understood. I'll be standing by.")
                is_active = False
                continue
            
            try:
                prompt = f"System: You are JARVIS. Give a concise, professional response. User: {command}"
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                
                ai_text = response.text.replace("*", "")
                await speak(ai_text)
                
            except Exception as e:
                print(f"AI Error: {e}")
                await speak("I've encountered a connection error, sir.")
                is_active = False

if __name__ == "__main__":
    asyncio.run(main())
