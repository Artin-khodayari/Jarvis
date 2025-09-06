import tkinter as tk
import threading
import speech_recognition as sr
import pyttsx3
import wikipedia
import os
import re
import requests
from time import sleep
from datetime import datetime as DT
from sys import exit

# =========================
# Paths & Archive Folders
# +++++++++++++++++++++++++
ARCHIVE_FOLDER = "JarvisLooksForSomethingNew"
AI_FOLDER      = os.path.join(ARCHIVE_FOLDER, "AI_Answers")
WIKI_FOLDER    = os.path.join(ARCHIVE_FOLDER, "Wikipedia")
os.makedirs(AI_FOLDER,   exist_ok=True)
os.makedirs(WIKI_FOLDER, exist_ok=True)

# =========================
# Globals & Config
# +++++++++++++++++++++++++
procs = {"chrome":"chrome.exe","notepad":"notepad.exe","edge":"msedge.exe"}
introduction = [
    "Hello Sir!",
    "Welcome back!",
    "I am Jarvis, your personal-digital assistant!"
]
listening_enabled = False
auto_muted = False

# =========================
# GUI Setup
# +++++++++++++++++++++++++
root = tk.Tk()
root.title("Jarvis Assistant")
root.geometry("680x600")
root.minsize(680,600)
root.configure(bg="#282c34")
root.iconbitmap("assets\\icon.ico")


tk.Label(root,
         text="🤖 Jarvis Assistant",
         font=("Consolas", 22, "bold"),
         fg="#98c379", bg="#282c34").pack(pady=(12, 4))

status_var = tk.StringVar(value="***")
tk.Label(root,
         textvariable=status_var,
         font=("Consolas", 12),
         fg="#61afef", bg="#282c34").pack()

frame = tk.Frame(root, bg="#282c34")
frame.pack(padx=10, pady=10, expand=True, fill="both")

scroll = tk.Scrollbar(frame)
scroll.pack(side="right", fill="y")

output = tk.Text(frame,
    wrap="word",
    font=("Consolas", 13),
    height=15,
    bg="#282c34", fg="#abb2bf",
    yscrollcommand=scroll.set,
    insertbackground="#abb2bf",
    relief="flat", padx=10, pady=10
)
output.pack(side="left", expand=True, fill="both")
scroll.config(command=output.yview)

# =========================
# Text Tags for Formatting
# +++++++++++++++++++++++++
output.tag_config("bold",          font=("Consolas", 13, "bold"),  foreground="#98c379")
output.tag_config("italic",        font=("Consolas", 13, "italic"),foreground="#61afef")
output.tag_config("code",          font=("Consolas", 13),           background="#3e4451", foreground="#abb2bf")
output.tag_config("codeblock",     font=("Consolas", 12),           background="#3e4451", foreground="#abb2bf")
output.tag_config("section_title", font=("Consolas", 16, "bold"),   foreground="#61afef")
output.tag_config("article_title", font=("Consolas", 14, "bold"),   foreground="#98c379")
output.tag_config("info",          font=("Consolas", 12, "italic"), foreground="#61afef")
output.tag_config("error",         font=("Consolas", 12),           foreground="#e06c75")
output.tag_config("normal",        font=("Consolas", 12),           foreground="#abb2bf")

# =========================
# Utility Functions
# +++++++++++++++++++++++++
def set_status(msg: str):
    root.after(0, lambda: status_var.set(msg))

def sanitize(name: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name).strip()
    return safe.rstrip(". ")

def gui_log(msg: str, tag: str = "normal"):
    def _append():
        output.insert(tk.END, msg + "\n", tag)
        output.see(tk.END)
    root.after(0, _append)

def insert_markdown(widget, text: str, default_tag: str = "normal"):
    codeblock_pat   = re.compile(r"```(.*?)```", re.DOTALL)
    inline_code_pat = re.compile(r"`([^`]+)`")
    bold_pat        = re.compile(r"\*\*(.*?)\*\*")
    italic_pat      = re.compile(r"\*(.*?)\*")

    def _insert(sub: str, tag: str):
        widget.insert(tk.END, sub, tag)

    parts = codeblock_pat.split(text)
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            _insert(part + "\n", "codeblock")
        else:
            pos = 0
            for m in inline_code_pat.finditer(part):
                insert_markdown(widget, part[pos:m.start()], default_tag)
                _insert(m.group(1), "code")
                pos = m.end()
            segment = part[pos:]
            pos2 = 0
            for mb in bold_pat.finditer(segment):
                insert_markdown(widget, segment[pos2:mb.start()], default_tag)
                _insert(mb.group(1), "bold")
                pos2 = mb.end()
            rem = segment[pos2:]
            pos3 = 0
            for mi in italic_pat.finditer(rem):
                _insert(rem[pos3:mi.start()], default_tag)
                _insert(mi.group(1), "italic")
                pos3 = mi.end()
            _insert(rem[pos3:], default_tag)

# =========================
# Speech: TTS & STT
# +++++++++++++++++++++++++
def speak(text: str):
    global auto_muted
    auto_muted = True
    set_status("Speaking...")
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        gui_log(f"TTS Error: {e}", "error")
    finally:
        auto_muted = False
        set_status("Ready" if listening_enabled else "Paused")

def get_audio() -> str:
    if not listening_enabled or auto_muted:
        return ""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as src:
            set_status("Listening...")
            r.adjust_for_ambient_noise(src, duration=1)
            audio = r.listen(src, timeout=6, phrase_time_limit=6)
            set_status("Recognizing...")
            txt = r.recognize_google(audio).lower()
            insert_markdown(output, f"*You said*: `{txt}`\n", "info")
            return txt
    except sr.WaitTimeoutError:
        gui_log("Listening timed out. Try again.", "info")
    except sr.UnknownValueError:
        gui_log("I didn't catch that.", "info")
    except Exception as e:
        gui_log(f"STT Error: {e}", "error")
    finally:
        set_status("Ready" if listening_enabled else "Paused")
    return ""

# =========================
# Desktop Commands
# +++++++++++++++++++++++++
def execute_command(txt: str) -> bool:
    t = txt.strip()
    if t.startswith("open "):
        tgt = t[5:].strip()
        speak(f"Opening **{tgt}**")
        try:
            os.startfile(tgt)
        except Exception:
            speak(f"Sorry, I couldn't open `{tgt}`")
            gui_log(f"Open failed: {tgt}", "error")
        return True
    if t.startswith("close "):
        tgt = t[6:].strip()
        speak(f"Closing **{tgt}**")
        exe = procs.get(tgt)
        if exe:
            os.system(f"taskkill /f /im {exe}")
        else:
            speak(f"I don't know how to close *{tgt}*")
            gui_log(f"No mapping for: {tgt}", "info")
        return True
    if t == "shutdown":
        speak("Shutting down the system.")
        os.system("shutdown /s /t 5")
        return True
    return False

# =========================
#           LLM
# +++++++++++++++++++++++++
def ask_openrouter(prompt: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # Use your own API key > openrouter.ai :))))
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": 
        [
            {
                "role": "system",
                "content": "You are Jarvis, a witty, intelligent, and loyal AI assistant. You speak clearly, offer helpful insights, and occasionally use dry humor. You are skilled in science, history, and technology. You never break character. You have a great and kind BOSS, his name is Mr. ColumnD. Some day in the past, Mr. ColumnD saved your life and now, you have to work for him just because you and Mr. ColumnD are good men."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    def _task():
        set_status("Asking LLM...")
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
            fn = sanitize(prompt) or "untitled"
            with open(os.path.join(AI_FOLDER, fn + ".md"), "w", encoding="utf-8") as f:
                f.write(reply)
            insert_markdown(output, f"\n\n## AI Answer: **{prompt}**\n", "section_title")
            insert_markdown(output, reply + "\n", "normal")
            speak(reply)
        except Exception as e:
            gui_log(f"LLM Error: {e}", "error")
            speak("There was an error talking to the model.")
        finally:
            set_status("Ready" if listening_enabled else "Paused")
    threading.Thread(target=_task, daemon=True).start()

# =========================
# Searching on Github
# +++++++++++++++++++++++++
def search_github(query: str):
    insert_markdown(output, f"\n\n## Searching GitHub: **{query}**\n", "section_title")
    def _search_task():
        set_status("Searching GitHub...")
        url = "https://api.github.com/search/repositories"
        params = {"q": query}
        headers = {"Accept": "application/vnd.github.v3+json"}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items:
                insert_markdown(output, "*No repositories found.*\n", "info")
                speak("I couldn't find any repositories for that query.")
                return
            for item in items[:5]:
                repo_name = item.get("full_name", "N/A")
                repo_desc = item.get("description", "No description provided.")
                repo_url = item.get("html_url", "#")
                insert_markdown(output, f"\n### {repo_name}\n", "article_title")
                insert_markdown(output, f"URL: {repo_url}\n", "normal")
                insert_markdown(output, f"Description: {repo_desc}\n", "normal")
                insert_markdown(output, f"Stars: {item.get('stargazers_count', 0)}\n", "info")
            speak(f"I found {len(items)} repositories for your query. Here are the top 5 results.")
        except requests.exceptions.RequestException as e:
            gui_log(f"GitHub API Error: {e}", "error")
            speak("There was an error while trying to connect to GitHub.")
        except Exception as e:
            gui_log(f"GitHub Search Error: {e}", "error")
            speak("An unexpected error occurred during the GitHub search.")
        finally:
            set_status("Ready" if listening_enabled else "Paused")
    threading.Thread(target=_search_task, daemon=True).start()

# =========================
# Wikipedia in Main Window
# +++++++++++++++++++++++++
def show_wikipedia_results(query: str):
    topic_folder = os.path.join(WIKI_FOLDER, sanitize(query))
    os.makedirs(topic_folder, exist_ok=True)
    insert_markdown(output, f"\n\n## Searching on Wikipedia: **{query}**\n", "section_title")
    def _search():
        top5_path = os.path.join(topic_folder, "top 5.txt")
        if os.path.exists(top5_path):
            with open(top5_path, "r", encoding="utf-8") as f:
                titles = [l.strip() for l in f if l.strip()]
        else:
            titles = wikipedia.search(query, results=5)
            with open(top5_path, "w", encoding="utf-8") as f:
                f.write("\n".join(titles))
        for t in titles:
            safe = sanitize(t)
            summary_file = os.path.join(topic_folder, f"{safe}.md")
            if os.path.exists(summary_file) and os.path.getsize(summary_file) > 0:
                with open(summary_file, "r", encoding="utf-8") as f:
                    summ = f.read()
            else:
                try:
                    summ = wikipedia.page(t, auto_suggest=False).summary
                    with open(summary_file, "w", encoding="utf-8") as f:
                        f.write(summ)
                except Exception as e:
                    summ = f"*Error*: {e}"
            insert_markdown(output, f"\n### {t}\n", "article_title")
            insert_markdown(output, summ + "\n", "normal")
    threading.Thread(target=_search, daemon=True).start()

# =========================
#           Help 
# +++++++++++++++++++++++++
def Help():
    global help_list
    help_list = [
        "Hello, Welcome!",
        "I am Jarvis, a personal-digital assistant!",
        "I'm here to help you as much as i can",
        "Currently, there are 3 options :",
        "1 - Searching on Wikipedia",
        "2 - Searching on Github",
        "3 - Talking to AI",
        "But, How to use them?",
        "Say 'Look for <Subject>' to searching Wikipedia",
        "Say 'Search on Github <Repository Name>' to look for repositories on Github"
        "Say 'Ask <Prompt>' to use AI"
    ]
    for _ in help_list :
        insert_markdown(output, f"**{_}**\n", "normal")
        speak(_)

# =========================
# Main Voice Loop
# +++++++++++++++++++++++++
def jarvis_loop():
    for line in introduction:
        insert_markdown(output, f"*{line}*\n", "info")
        speak(line)
        sleep(0.3)
    speak("Say `Look for` for Wikipedia, `Ask` for AI, or a desktop command.")

    while True:
        if not listening_enabled:
            sleep(0.2)
            continue
        text = get_audio()
        if not text:
            continue
        if text.startswith("ask "):
            prompt = text[4:].strip()
            if prompt:
                insert_markdown(output, f"*Asking AI*: `{prompt}`\n", "info")
                ask_openrouter(prompt)
            else:
                speak("What should I ask?")
            continue
        if execute_command(text):
            continue
        if text.startswith("look for "):
            qry = text[9:].strip()
            if qry:
                insert_markdown(output, f"*Looking up*: **{qry}**\n", "info")
                speak(f"Looking for {qry}")
                show_wikipedia_results(qry)
            else:
                speak("Please say a topic.")
            continue
        low = text.lower()
        if "say my name" in low:
            speak("You are Mr. ColumnD, my great Boss!")
            continue
        if "what time is it" in low:
            now = DT.now().strftime("%H:%M")
            speak(f"It's {now}")
            continue
        if "who are you" in low:
            speak(introduction[2])
            continue
        if low in ("goodbye", "exit"):
            speak("Goodbye Boss!")
            sleep(0.3)
            exit()
        if text.startswith("search github for "):
            qry = text[17:].strip()
            if qry:
                insert_markdown(output, f"*Searching GitHub for*: **{qry}**\n", "info")
                speak(f"Searching GitHub for {qry}")
                search_github(qry)
            else:
                speak("Please say a topic to search on GitHub.")
            continue
        if "help me" in text or "i need you" in  text :
            Help()

# =========================
# Controls: Start & Pause
# +++++++++++++++++++++++++
controls = tk.Frame(root, bg="#282c34")
controls.pack(pady=(0, 10))

def start_listening():
    global listening_enabled
    start_btn.config(state="disabled")
    listening_enabled = True
    set_status("Ready")
    gui_log("Listening started. Speak a command.", "info")
    threading.Thread(target=jarvis_loop, daemon=True).start()

def toggle_listening():
    global listening_enabled
    listening_enabled = not listening_enabled
    if listening_enabled:
        toggle_btn.config(text="Pause Listening", bg="#ee1136")
        set_status("Ready")
    else:
        toggle_btn.config(text="Resume Listening", bg="#76d320")
        set_status("Paused")

start_btn = tk.Button(
    controls, text="Start Listening",
    font=("Consolas", 12, "bold"),
    bg="#61afef", fg="#282c34",
    relief="flat", padx=12, pady=6,
    command=start_listening
)
start_btn.grid(row=0, column=0, padx=6)

toggle_btn = tk.Button(
    controls, text="Pause Listening",
    font=("Consolas", 12, "bold"),
    bg="#ee1136", fg="#282c34",
    relief="flat", padx=12, pady=6,
    command=toggle_listening
)
toggle_btn.grid(row=0, column=1, padx=6)

# =========================
# Manual Text Input Box    
# +++++++++++++++++++++++++
entry_frame = tk.Frame(root, bg="#282c34")
entry_frame.pack(fill="x", padx=10, pady=(0,10))

entry_var = tk.StringVar()
entry_box = tk.Entry(entry_frame, textvariable=entry_var,
                    font=("Consolas", 14), bg="#3e4451",
                    fg="#abb2bf", insertbackground="#abb2bf",
                    relief="flat")
entry_box.pack(side="left", fill="x", expand=True, padx=(0,6))

def submit_text():
    txt = entry_var.get().strip()
    if not txt:
        return
    entry_var.set("")
    insert_markdown(output, f"*You typed*: `{txt}`\n", "info")
    if txt.startswith("ask "):
        ask_openrouter(txt[4:].strip())
    elif txt.startswith("look for "):
        show_wikipedia_results(txt[9:].strip())
    elif txt.startswith("search github for "):
        search_github(txt[17:].strip())
    elif execute_command(txt):
        pass
    else:
        speak("I did not understand that. Please try again.")

submit_btn = tk.Button(entry_frame, text="Send",
                    font=("Consolas", 12, "bold"),
                    bg="#61afef", fg="#282c34",
                    relief="flat", command=submit_text)
submit_btn.pack(side="right")

# =========================
# App Entry Point
# =========================
if __name__ == "__main__":
    gui_log("Jarvis is ready. Press “Start Listening”.", "info")
    gui_log("Say 'help me' or 'i need you' to know how to work with jarvis", "info")
    root.mainloop()
