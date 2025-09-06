# 🤖 Jarvis Assistant

![Jarvis GUI](assets/Jarvis.png)

**Jarvis Assistant** is a personal, voice-controlled digital assistant built in Python. Inspired by the AI from movies, this project allows you to interact with your computer using natural voice commands, search Wikipedia and GitHub, and get AI-powered responses directly in a beautiful GUI interface.

---

## 🌟 Features

- Voice-controlled commands (Start, Pause, Stop listening)
- Speak-to-text & text-to-speech integration using `speech_recognition` and `pyttsx3`
- Wikipedia search directly from GUI
- GitHub repository search and display of top results
- Ask AI questions via OpenRouter.ai integration
- Execute desktop commands (`open`, `close`, `shutdown`)
- Manual text input for commands if you prefer typing
- Colorful, responsive Tkinter GUI with markdown-style text formatting
- Archive system for saving AI responses and Wikipedia results

---

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/Artin-khodayari/Jarvis.git
cd Jarvis
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Make sure you have a microphone connected for voice commands.

---

## ⚙️ Requirements

- Python 3.10+
- `tkinter` (usually comes with Python)
- `pyttsx3`
- `speechrecognition`
- `wikipedia`
- `requests`

---

## 🖥️ Usage

1. Run the application:

```bash
python jarvis.py
```

2. Press **Start Listening** to activate voice commands.
3. Say commands like:
   - `Look for <topic>` → Search Wikipedia
   - `Search GitHub for <repository>` → Search GitHub
   - `Ask <question>` → Get AI-powered responses
   - `Open <application>` → Open apps like Notepad or Chrome
   - `Close <application>` → Close apps
4. Use **Pause Listening** to temporarily stop voice recognition.
5. Type commands manually in the text input box if needed.

---

## 📝 Examples of Commands

| Command                       | Action                                    |
| ----------------------------- | ----------------------------------------- |
| `Look for Python programming` | Searches Wikipedia and displays summary   |
| `Search GitHub for flask`     | Lists top 5 GitHub repositories for Flask |
| `Ask What is AI?`             | Queries OpenRouter.ai for an AI response  |
| `Open notepad`                | Opens Notepad                             |
| `Close chrome`                | Closes Chrome                             |
| `Shutdown`                    | Shuts down your system                    |
| `Say my name`                 | Jarvis will speak your name back          |

---

## 🎨 GUI

The interface is designed to be:

- Modern and minimal
- Color-coded messages (bold, italic, code, error, info)
- Scrollable output panel for AI and search results
- Resizable window with minsize constraints
- Manual text input with a Send button

---

## 🤝 Contributing

Contributions are welcome!\
To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-name`)
6. Open a Pull Request

---

# 🧑‍💻 About the Developer

This project is made by [Artin khodayari](https://github.com/Artin-khodayari).

You can contact me and report the problems and bugs to my [Gmail-Account](mailto:ArtinKhodayari2010@gmail.com)

Feel free to reach out for questions, feedback, or collaborations!

---

# 📄 License
Also read [License]([https://github.com/Artin-khodayari/Jarvis/blob/main/License](https://github.com/Artin-khodayari/Jarvis/tree/main?tab=MIT-1-ov-file)
