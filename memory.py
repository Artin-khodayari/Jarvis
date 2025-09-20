import json, os

MEMORY_FILE = "jarvis_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def remember(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def recall(key):
    return load_memory().get(key, "I don't remember that yet.")

def forget(key):
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)
        return f"Forgot '{key}'."
    return f"'{key}' wasn't in memory."
