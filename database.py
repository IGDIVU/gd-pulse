import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")
PURAV_CARTING_FILE = os.path.join(DATA_DIR, "purav_carting.json")

DEFAULT_USERS = {
    "admin": {"password": "gdadmin123", "role": "admin", "name": "Admin"},
    "owner": {"password": "gdowner123", "role": "owner", "name": "Owner"},
    "manager": {"password": "gdmanager123", "role": "manager", "name": "Manager"},
    "staff": {"password": "gdstaff123", "role": "staff", "name": "Staff"},
    "user": {"password": "gduser123", "role": "user", "name": "User"}
}

DEFAULT_PURAV_CARTING = {
    "trucks": [],
    "customers": [],
    "suppliers": [],
    "staff": [],
    "materials": [],
    "entries": [],
    "challans": [],
    "purchases": [],
    "payments": [],
    "invoices": [],
    "trips": [],
    "salary_payments": [],
    "advance_payments": [],
    "settings": {
        "default_diesel_rate": 90,
        "default_labour_rate": 500,
        "default_driver_rate": 500,
        "company_name": "PURAV CARTING",
        "company_address": "",
        "company_gst": "",
        "company_phone": "",
        "company_email": "",
        "bank_name": "",
        "bank_account": "",
        "bank_ifsc": "",
        "bill_prefix_challan": "PC/CH",
        "bill_prefix_invoice": "PC/INV",
        "terms": "Goods once sold will not be taken back.",
        "challan_counter": 0,
        "invoice_counter": 0
    }
}

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# ---------- USERS ----------
def load_users():
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f).get("users", DEFAULT_USERS)
    except Exception:
        return DEFAULT_USERS

def save_users(users):
    ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump({"users": users}, f, indent=2)

def get_user(username):
    return load_users().get(username)

def add_user(username, password, role, name):
    users = load_users()
    users[username] = {"password": password, "role": role, "name": name}
    save_users(users)

def update_user(username, password=None, role=None, name=None):
    users = load_users()
    if username not in users: return False
    if password: users[username]["password"] = password
    if role: users[username]["role"] = role
    if name: users[username]["name"] = name
    save_users(users)
    return True

def delete_user(username):
    users = load_users()
    if username in users and username not in ("owner", "admin"):
        del users[username]
        save_users(users)
        return True
    return False

# ---------- PROMPTS ----------
def load_prompts():
    ensure_data_dir()
    if not os.path.exists(PROMPTS_FILE): return {}
    try:
        with open(PROMPTS_FILE, "r") as f:
            return json.load(f).get("prompts", {})
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

# ============================================
# PURAV CARTING
# ============================================

def load_purav_carting():
    ensure_data_dir()
    if not os.path.exists(PURAV_CARTING_FILE):
        save_purav_carting(DEFAULT_PURAV_CARTING)
        return DEFAULT_PURAV_CARTING
    try:
        with open(PURAV_CARTING_FILE, "r") as f:
            data = json.load(f)
            for k, v in DEFAULT_PURAV_CARTING.items():
                if k not in data:
                    data[k] = v
            for k, v in DEFAULT_PURAV_CARTING["settings"].items():
                if k not in data["settings"]:
                    data["settings"][k] = v
            return data
    except Exception:
        return DEFAULT_PURAV_CARTING

def save_purav_carting(data):
    ensure_data_dir()
    with open(PURAV_CARTING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_collection(name):
    return load_purav_carting().get(name, [])

def get_item(name, item_id):
    for it in get_collection(name):
        if it["id"] == item_id:
            return it
    return None

def add_item(name, item_data):
    data = load_purav_carting()
    if name not in data: data[name] = []
    data[name].append(item_data)
    save_purav_carting(data)

def update_item(name, item_id, item_data):
    data = load_purav_carting()
    for i, it in enumerate(data.get(name, [])):
        if it["id"] == item_id:
            data[name][i].update(item_data)
            save_purav_carting(data)
            return True
    return False

def delete_item(name, item_id):
    data = load_purav_carting()
    data[name] = [it for it in data.get(name, []) if it["id"] != item_id]
    save_purav_carting(data)

# ---------- SHORTCUTS ----------
def get_trucks(): return get_collection("trucks")
def get_truck(tid): return get_item("trucks", tid)
def add_truck(d): add_item("trucks", d)
def update_truck(tid, d): return update_item("trucks", tid, d)
def delete_truck(tid): delete_item("trucks", tid)

def get_customers(): return get_collection("customers")
def get_customer(cid): return get_item("customers", cid)
def add_customer(d): add_item("customers", d)
def update_customer(cid, d): return update_item("customers", cid, d)
def delete_customer(cid): delete_item("customers", cid)

def get_suppliers(): return get_collection("suppliers")
def get_supplier(sid): return get_item("suppliers", sid)
def add_supplier(d): add_item("suppliers", d)
def update_supplier(sid, d): return update_item("suppliers", sid, d)
def delete_supplier(sid): delete_item("suppliers", sid)

def get_staff(): return get_collection("staff")
def get_staff_member(sid): return get_item("staff", sid)
def add_staff(d): add_item("staff", d)
def update_staff(sid, d): return update_item("staff", sid, d)
def delete_staff(sid): delete_item("staff", sid)

def get_materials(): return get_collection("materials")
def get_material(mid): return get_item("materials", mid)
def add_material(d): add_item("materials", d)
def update_material(mid, d): return update_item("materials", mid, d)
def delete_material(mid): delete_item("materials", mid)

def get_entries(): return get_collection("entries")
def get_entry(eid): return get_item("entries", eid)
def add_entry(d): add_item("entries", d)
def update_entry(eid, d): return update_item("entries", eid, d)
def delete_entry(eid): delete_item("entries", eid)

def get_challans(): return get_collection("challans")
def get_challan(cid): return get_item("challans", cid)
def add_challan(d): add_item("challans", d)
def update_challan(cid, d): return update_item("challans", cid, d)
def delete_challan(cid): delete_item("challans", cid)

def get_purchases(): return get_collection("purchases")
def get_purchase(pid): return get_item("purchases", pid)
def add_purchase(d): add_item("purchases", d)
def update_purchase(pid, d): return update_item("purchases", pid, d)
def delete_purchase(pid): delete_item("purchases", pid)

def get_payments(): return get_collection("payments")
def get_payment(pid): return get_item("payments", pid)
def add_payment(d): add_item("payments", d)
def update_payment(pid, d): return update_item("payments", pid, d)
def delete_payment(pid): delete_item("payments", pid)

def get_invoices(): return get_collection("invoices")
def get_invoice(iid): return get_item("invoices", iid)
def add_invoice(d): add_item("invoices", d)
def update_invoice(iid, d): return update_item("invoices", iid, d)
def delete_invoice(iid): delete_item("invoices", iid)

def get_trips(): return get_collection("trips")
def get_trip(tid): return get_item("trips", tid)
def add_trip(d): add_item("trips", d)
def update_trip(tid, d): return update_item("trips", tid, d)
def delete_trip(tid): delete_item("trips", tid)

def get_salary_payments(): return get_collection("salary_payments")
def add_salary_payment(d): add_item("salary_payments", d)
def delete_salary_payment(pid): delete_item("salary_payments", pid)

def get_advance_payments(): return get_collection("advance_payments")
def add_advance_payment(d): add_item("advance_payments", d)
def delete_advance_payment(pid): delete_item("advance_payments", pid)

# ---------- SETTINGS ----------
def get_settings():
    return load_purav_carting().get("settings", DEFAULT_PURAV_CARTING["settings"])

def save_settings(settings):
    data = load_purav_carting()
    data["settings"] = settings
    save_purav_carting(data)

# ---------- COUNTERS ----------
def next_challan_no():
    data = load_purav_carting()
    settings = data.get("settings", DEFAULT_PURAV_CARTING["settings"])
    counter = settings.get("challan_counter", 0) + 1
    settings["challan_counter"] = counter
    data["settings"] = settings
    save_purav_carting(data)
    return f"{settings.get('bill_prefix_challan', 'PC/CH')}/2025-26/{counter:04d}"

def next_invoice_no():
    data = load_purav_carting()
    settings = data.get("settings", DEFAULT_PURAV_CARTING["settings"])
    counter = settings.get("invoice_counter", 0) + 1
    settings["invoice_counter"] = counter
    data["settings"] = settings
    save_purav_carting(data)
    return f"{settings.get('bill_prefix_invoice', 'PC/INV')}/2025-26/{counter:04d}"

# ============================================
# ACCOUNTS (Customer Ledger / Outstanding)
# ============================================

def get_customer_ledger(customer_id):
    """Return all transactions for a customer."""
    challans = [c for c in get_challans() if c.get("customer_id") == customer_id and c.get("invoiced")]
    invoices = [i for i in get_invoices() if i.get("customer_id") == customer_id]
    payments = [p for p in get_payments() if p.get("customer_id") == customer_id]

    # Use invoices as debit (what customer owes), payments as credit
    ledger = []
    for inv in invoices:
        ledger.append({
            "date": inv.get("date", ""),
            "type": "Invoice",
            "ref": inv.get("invoice_no", ""),
            "debit": inv.get("total", 0),
            "credit": 0,
            "notes": inv.get("notes", "")
        })
    for pay in payments:
        ledger.append({
            "date": pay.get("date", ""),
            "type": "Payment",
            "ref": pay.get("mode", "") + " " + pay.get("ref_no", ""),
            "debit": 0,
            "credit": pay.get("amount", 0),
            "notes": pay.get("notes", "")
        })
    # Opening balance
    customer = get_customer(customer_id) or {}
    if customer.get("opening_balance", 0) != 0:
        ledger.append({
            "date": customer.get("created_at", "")[:10],
            "type": "Opening",
            "ref": "Opening Balance",
            "debit": customer.get("opening_balance", 0),
            "credit": 0,
            "notes": ""
        })
    ledger.sort(key=lambda x: x.get("date", ""))
    running = 0
    for l in ledger:
        running += l["debit"] - l["credit"]
        l["balance"] = running
    return ledger, running

def get_customer_outstanding(customer_id):
    ledger, balance = get_customer_ledger(customer_id)
    return balance

def get_all_outstanding():
    """Return list of customers with outstanding balance > 0"""
    customers = get_customers()
    out = []
    for c in customers:
        bal = get_customer_outstanding(c["id"])
        if bal > 0:
            out.append({"customer": c, "balance": bal})
    return out
