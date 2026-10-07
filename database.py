import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")

DEFAULT_USERS = {
    "owner": {"password": "gdowner123", "role": "owner", "name": "Owner"},
    "admin": {"password": "gdadmin123", "role": "admin", "name": "Admin"},
    "staff": {"password": "gdstaff123", "role": "staff", "name": "Staff"},
    "user": {"password": "gduser123", "role": "user", "name": "User"}
}

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_users():
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            return data.get("users", DEFAULT_USERS)
    except Exception:
        return DEFAULT_USERS

def save_users(users):
    ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump({"users": users}, f, indent=2)

def get_user(username):
    users = load_users()
    return users.get(username)

def add_user(username, password, role, name):
    users = load_users()
    users[username] = {"password": password, "role": role, "name": name}
    save_users(users)

def update_user(username, password=None, role=None, name=None):
    users = load_users()
    if username not in users:
        return False
    if password:
        users[username]["password"] = password
    if role:
        users[username]["role"] = role
    if name:
        users[username]["name"] = name
    save_users(users)
    return True

def delete_user(username):
    users = load_users()
    if username in users and username != "owner":
        del users[username]
        save_users(users)
        return True
    return False

# ---------- Prompts ----------

def load_prompts():
    ensure_data_dir()
    if not os.path.exists(PROMPTS_FILE):
        return {}
    try:
        with open(PROMPTS_FILE, "r") as f:
            data = json.load(f)
            return data.get("prompts", {})
    except Exception:
        return {}

def save_prompts(prompts):
    ensure_data_dir()
    with open(PROMPTS_FILE, "w") as f:
        json.dump({"prompts": prompts}, f, indent=2)

def add_prompt(key, data):
    prompts = load_prompts()
    prompts[key] = data
    save_prompts(prompts)

def update_prompt(key, data):
    prompts = load_prompts()
    if key in prompts:
        prompts[key].update(data)
        save_prompts(prompts)
        return True
    return False

def delete_prompt(key):
    prompts = load_prompts()
    if key in prompts:
        del prompts[key]
        save_prompts(prompts)
        return True
    return False
