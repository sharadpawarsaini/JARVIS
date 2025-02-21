import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import wikipediaapi
from bs4 import BeautifulSoup
import geocoder
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from PIL import Image, ImageTk
import threading
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(script_dir, "jarvis_bg.jpg")

# Initialize Speech Recognition & TTS Engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set Female Voice
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Set up Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(user_agent='JARVIS/1.0 (Sharad)', language='en')

# API Configuration for News & Weather (Use your API key)
API_KEY = "39aee1595bba488ea12b5182aab40f0a"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
WEATHER_API_KEY = "640d827371b623073e2a983309d0a2f7"

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="c312a261e3544e2cb942f910b911f82e",
    client_secret="3d5d3be79acc4bde9afedd2365bf8e88",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing,streaming"
))

def speak(text):
    wave_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
    animate_wave()
    root.update()
    engine.say(text)
    engine.runAndWait()
    wave_label.place_forget()
    root.update()

def animate_wave():
    for i in range(10):
        wave_label.config(font=("Arial", 50 + (i % 5) * 5))
        root.update()
        time.sleep(0.1)

def play_on_spotify(song_name):
    song_name = song_name.strip()
    if not song_name:
        speak("Please specify a song name.")
        return
    
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['external_urls']['spotify']
        webbrowser.open(track_uri)
        speak(f"Opening {song_name} on Spotify.")
    else:
        speak("Sorry, I couldn't find the song on Spotify.")
        
def search_wikipedia(query):
    """Fetches information from Wikipedia."""
    page = wiki_wiki.page(query)
    if page.exists():
        summary = page.summary[:500]
        speak(summary)
        return summary
    return "No Wikipedia information found."

def fetch_news():
    """Fetches and reads out the latest news headlines."""
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        if articles:
            speak("Here are the top news headlines.")
            for index, article in enumerate(articles[:5], start=1):
                title = article.get('title', "No title available")
                print(f"{index}. {title}")
                speak(title)
        else:
            speak("No news articles found.")
    except requests.RequestException:
        speak("Error fetching news. Please check your internet connection.")

def google_search(query):
    """Performs a Google search."""
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)
    speak(f"Here are the search results for {query}.")

def process_command():
    global active
    active = True
    speak("Yes?")
    while active:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for command...")
            try:
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
                command = recognizer.recognize_google(audio).lower()
                print("You said:", command)
                if command == "thank you jarvis":
                    speak("You're welcome, Sharad! Have a great day.")
                    active = False
                    root.destroy()
                    return
                elif "play" in command:
                    song = command.replace("play", "").strip()
                    play_on_spotify(song)
                elif "open" in command:
                    sites = {"google": "https://google.com", "facebook": "https://facebook.com", 
                             "youtube": "https://youtube.com", "linkedin": "https://linkedin.com", 
                             "erp": "https://student.gehu.ac.in/", "chat gpt": "https://chatgpt.com/"}
                    for key in sites:
                        if key in command:
                            webbrowser.open(sites[key])
                            speak(f"Opening {key}.")
                            break
                elif "weather" in command:
                    get_weather()
                elif "news" in command:
                    fetch_news()
                elif "how are you" in command:
                    speak("I am fine, what about you?")
                elif command in ["i am also fine", "fine"]:
                    speak("That's great, so how can I help you?")
                elif command == "what is your name":
                    speak("My name is Jarvis.")
                elif command == "who developed you":
                    speak("I was developed by Sharad Pawar Saini.")
                else:
                    response = search_wikipedia(command)
                    if "No Wikipedia information found" in response:
                        google_search(command)
                    else:
                        speak(response)
            except sr.UnknownValueError:
                speak("Sorry, I could not understand the command.")
            except sr.RequestError:
                speak("Network error. Please check your internet connection.")

def activate_jarvis():
    threading.Thread(target=process_command, daemon=True).start()

def create_gui():
    global root, wave_label
    root = tk.Tk()
    root.title("JARVIS Assistant")
    root.geometry("800x600")
    root.state('zoomed')
    
    try:
        bg_image = Image.open(bg_path)
        bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        print("Background image not found! Using default background.")
        root.configure(bg='black')
    
    wave_label = tk.Label(root, text="🔊", font=("Arial", 50), fg="blue")
    
    button = tk.Button(root, text="Speak", font=("Arial", 20), command=activate_jarvis, bg="blue", fg="white", padx=20, pady=10)
    button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
