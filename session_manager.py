import json, os, datetime

SESSION_FILE = "jarvis_session.json"

def start_session():
    if not os.path.exists(SESSION_FILE):
        return []
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def log_interaction(user_input, jarvis_response):
    session = start_session()
    session.append({
        "timestamp": str(datetime.datetime.now()),
        "user": user_input,
        "jarvis": jarvis_response
    })
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)
