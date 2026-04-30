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
MODEL_ID = "gemini-2.5-flash" 
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

def listen(timeout_val=None):
    """Listens for the user's voice."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # We wait for the user to start talking
            audio = r.listen(source, timeout=timeout_val, phrase_time_limit=10)
            query = r.recognize_google(audio, language='en-US')
            print(f"User: {query}")
            return query.lower()
        except:
            return ""

async def main():
    await speak("Systems initialized. JARVIS is online.")
    is_active = False # Start in standby mode
    
    while True:
        if not is_active:
            print("\n[ STANDBY: Waiting for 'Jarvis'... ]")
            wake_word = listen()
            
            if "jarvis" in wake_word:
                is_active = True
                await speak("At your service, sir. How can I help?")
        
        else:
            # While active, he listens for ANY command without needing his name
            print("\n[ ACTIVE: Listening for your command... ]")
            command = listen(timeout_val=10) # Wait 10 seconds for a question
            
            if not command:
                print("No activity detected. Returning to standby.")
                is_active = False
                continue

            if "stop" in command or "sleep" in command or "exit" in command:
                await speak("Understood. I'll be standing by if you need me.")
                is_active = False
                continue
            
            # Process the command
            try:
                # Add personality
                prompt = f"System: You are JARVIS. Give a concise, professional response. User: {command}"
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt
                )
                
                ai_text = response.text.replace("*", "")
                await speak(ai_text)
                # AFTER SPEAKING, the loop continues and he listens again automatically!
                
            except Exception as e:
                print(f"AI Error: {e}")
                await speak("I've encountered a connection error, sir.")
                #adding the commading to end the jarvis
                #this update in the version 3

if __name__ == "__main__":
    asyncio.run(main())
