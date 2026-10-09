from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import io
import uuid
from datetime import datetime
from PIL import Image
import database

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gd_pulse_secret_key_2025")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

def current_user(): return session.get("user")
def current_role(): return session.get("role")
def current_name(): return session.get("name", session.get("user"))

ROLE_LEVELS = {"admin": 6, "owner": 5, "manager": 4, "hr": 3, "staff": 2, "user": 1}

def require_login(): return current_role() in ROLE_LEVELS
def require_staff(): return current_role() in ("admin", "owner", "manager", "hr", "staff")
def require_prompts(): return current_role() in ("admin", "owner", "manager", "staff")
def require_prompts_crud(): return current_role() in ("admin", "owner")
def require_admin(): return current_role() in ("admin", "owner")
def require_owner(): return current_role() in ("admin", "owner")

PURAV_CARTING = {"username": "PC", "password": "123", "display_name": "Purav Carting"}

@app.after_request
def inject_animations(response):
    if (response.content_type and "text/html" in response.content_type
        and response.status_code == 200):
        try:
            html = response.get_data(as_text=True)
            if "animations.js" not in html and "</body>" in html:
                script_tag = '  <script src="/static/animations.js"></script>\n</body>'
                html = html.replace("</body>", script_tag, 1)
                response.set_data(html)
        except Exception:
            pass
    return response

@app.route("/")
def portfolio():
    return render_template("portfolio.html", user=current_user(), role=current_role(), name=current_name())

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = database.get_user(username)
        if user and user["password"] == password:
            session["user"] = username
            session["role"] = user["role"]
            session["name"] = user["name"]
            role = user["role"]
            if role == "admin": return redirect(url_for("admin"))
            elif role == "owner": return redirect(url_for("owner"))
            elif role in ("manager", "staff"): return redirect(url_for("tools"))
            elif role == "hr": return redirect(url_for("owner"))
            else: return redirect(url_for("portfolio"))
        else:
            error = "Galat username ya password"
    return render_template("login.html", error=error, name="", user="", role="")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("portfolio"))

@app.route("/prompts")
def prompts():
    if not require_prompts(): return redirect(url_for("login"))
    all_prompts = database.load_prompts()
    can_edit = require_prompts_crud()
    return render_template("prompts.html", user=current_user(), role=current_role(),
                          name=current_name(), db_prompts=all_prompts, can_edit=can_edit)

@app.route("/tools")
def tools():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("tools.html", user=current_user(), role=current_role(), name=current_name())

# ============================================
# PURAV WORK
# ============================================

@app.route("/purav")
def purav_dashboard():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("purav/dashboard.html", user=current_user(), role=current_role(), name=current_name())

@app.route("/purav/login", methods=["GET", "POST"])
def purav_login():
    if not require_staff(): return redirect(url_for("login"))
    biz = request.args.get("biz", "carting")
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == PURAV_CARTING["username"] and password == PURAV_CARTING["password"]:
            session["purav_biz"] = biz
            session["purav_user"] = username
            session["purav_name"] = PURAV_CARTING["display_name"]
            return redirect(url_for("purav_carting"))
        else:
            error = "Galat username ya password"
    return render_template("purav/login.html", user=current_user(), role=current_role(),
                          name=current_name(), biz=biz, error=error)

def purav_logged_in():
    return session.get("purav_biz") == "carting"

def purav_guard():
    if not require_staff(): return redirect(url_for("login"))
    if not purav_logged_in(): return redirect(url_for("purav_login", biz="carting"))
    return None

@app.route("/purav/carting")
def purav_carting():
    g = purav_guard()
    if g: return g
    trucks = database.get_trucks()
    entries = database.get_entries()
    challans = database.get_challans()
    purchases = database.get_purchases()
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    today_entries = [e for e in entries if e.get("date") == today]
    month_entries = [e for e in entries if e.get("date", "").startswith(month)]
    month_purchases = [p for p in purchases if p.get("date", "").startswith(month)]

    stats = {
        "today_trips": sum(e.get("trips", 0) for e in today_entries),
        "today_sale": sum(e.get("sale", 0) for e in today_entries),
        "today_diesel": sum(e.get("diesel", 0) for e in today_entries),
        "today_profit": sum(e.get("profit", 0) for e in today_entries),
        "month_trips": sum(e.get("trips", 0) for e in month_entries),
        "month_sale": sum(e.get("sale", 0) for e in month_entries),
        "month_cost": sum(e.get("total_cost", 0) for e in month_entries),
        "month_profit": sum(e.get("profit", 0) for e in month_entries),
        "month_purchase": sum(p.get("amount", 0) for p in month_purchases),
        "pending_challans": len([c for c in challans if not c.get("invoiced")]),
    }

    truck_map = {t["id"]: t for t in trucks}
    recent = sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    for e in recent:
        e["truck_number"] = truck_map.get(e.get("truck_id", ""), {}).get("number", "—")

    truck_today = {}
    for e in today_entries:
        tid = e.get("truck_id", "")
        if tid not in truck_today:
            truck_today[tid] = {"trips": 0, "sale": 0, "profit": 0, "number": truck_map.get(tid, {}).get("number", "—")}
        truck_today[tid]["trips"] += e.get("trips", 0)
        truck_today[tid]["sale"] += e.get("sale", 0)
        truck_today[tid]["profit"] += e.get("profit", 0)

    alerts = []
    for t in trucks:
        for field, label in [("insurance_expiry", "Insurance"), ("fitness_expiry", "Fitness"), ("permit_expiry", "Permit")]:
            exp = t.get(field, "")
            if exp:
                try:
                    exp_date = datetime.strptime(exp, "%Y-%m-%d")
                    days = (exp_date - datetime.now()).days
                    if 0 <= days <= 30:
                        alerts.append({"type": "warn", "msg": f"{label} expiring: {t['number']} ({days} days)"})
                    elif days < 0:
                        alerts.append({"type": "danger", "msg": f"{label} EXPIRED: {t['number']}"})
                except Exception:
                    pass

    return render_template("purav/carting.html", user=current_user(), role=current_role(),
                          name=current_name(), stats=stats, recent=recent,
                          truck_today=truck_today, alerts=alerts, truck_count=len(trucks))

# ============================================
# TRUCK MASTER
# ============================================

@app.route("/purav/carting/trucks")
def purav_trucks():
    g = purav_guard()
    if g: return g
    trucks = database.get_trucks()
    entries = database.get_entries()
    for t in trucks:
        t_entries = [e for e in entries if e.get("truck_id") == t["id"]]
        t["total_trips"] = sum(e.get("trips", 0) for e in t_entries)
        t["total_sale"] = sum(e.get("sale", 0) for e in t_entries)
        t["total_profit"] = sum(e.get("profit", 0) for e in t_entries)
    return render_template("purav/trucks.html", user=current_user(), role=current_role(),
                          name=current_name(), trucks=trucks)

@app.route("/purav/carting/trucks/add", methods=["POST"])
def purav_trucks_add():
    g = purav_guard()
    if g: return g
    number = request.form.get("number", "").strip().upper()
    if not number: return redirect(url_for("purav_trucks") + "?error=missing")
    database.add_truck({
        "id": str(uuid.uuid4())[:8], "number": number,
        "model": request.form.get("model", "").strip(),
        "owner": request.form.get("owner", "Self").strip(),
        "insurance_expiry": request.form.get("insurance_expiry", ""),
        "fitness_expiry": request.form.get("fitness_expiry", ""),
        "permit_expiry": request.form.get("permit_expiry", ""),
        "status": request.form.get("status", "Active").strip(),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_trucks") + "?success=added")

@app.route("/purav/carting/trucks/edit/<tid>", methods=["POST"])
def purav_trucks_edit(tid):
    g = purav_guard()
    if g: return g
    database.update_truck(tid, {
        "number": request.form.get("number", "").strip().upper(),
        "model": request.form.get("model", "").strip(),
        "owner": request.form.get("owner", "Self").strip(),
        "insurance_expiry": request.form.get("insurance_expiry", ""),
        "fitness_expiry": request.form.get("fitness_expiry", ""),
        "permit_expiry": request.form.get("permit_expiry", ""),
        "status": request.form.get("status", "Active").strip(),
        "notes": request.form.get("notes", "").strip(),
    })
    return redirect(url_for("purav_trucks") + "?success=updated")

@app.route("/purav/carting/trucks/delete/<tid>")
def purav_trucks_delete(tid):
    g = purav_guard()
    if g: return g
    database.delete_truck(tid)
    return redirect(url_for("purav_trucks") + "?success=deleted")

# ============================================
# CUSTOMER MASTER
# ============================================

@app.route("/purav/carting/customers")
def purav_customers():
    g = purav_guard()
    if g: return g
    customers = database.get_customers()
    challans = database.get_challans()
    for c in customers:
        c_challans = [ch for ch in challans if ch.get("customer_id") == c["id"] and not ch.get("invoiced")]
        c["pending_count"] = len(c_challans)
        c["pending_amount"] = sum(ch.get("amount", 0) for ch in c_challans)
    return render_template("purav/customers.html", user=current_user(), role=current_role(),
                          name=current_name(), customers=customers)

@app.route("/purav/carting/customers/add", methods=["POST"])
def purav_customers_add():
    g = purav_guard()
    if g: return g
    name = request.form.get("name", "").strip()
    if not name: return redirect(url_for("purav_customers") + "?error=missing")
    database.add_customer({
        "id": str(uuid.uuid4())[:8], "name": name,
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "gstin": request.form.get("gstin", "").strip(),
        "pan": request.form.get("pan", "").strip(),
        "address": request.form.get("address", "").strip(),
        "state": request.form.get("state", "").strip(),
        "type": request.form.get("type", "Regular").strip(),
        "opening_balance": float(request.form.get("opening_balance", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_customers") + "?success=added")

@app.route("/purav/carting/customers/edit/<cid>", methods=["POST"])
def purav_customers_edit(cid):
    g = purav_guard()
    if g: return g
    database.update_customer(cid, {
        "name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "gstin": request.form.get("gstin", "").strip(),
        "pan": request.form.get("pan", "").strip(),
        "address": request.form.get("address", "").strip(),
        "state": request.form.get("state", "").strip(),
        "type": request.form.get("type", "Regular").strip(),
        "opening_balance": float(request.form.get("opening_balance", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
    })
    return redirect(url_for("purav_customers") + "?success=updated")

@app.route("/purav/carting/customers/delete/<cid>")
def purav_customers_delete(cid):
    g = purav_guard()
    if g: return g
    database.delete_customer(cid)
    return redirect(url_for("purav_customers") + "?success=deleted")

# ============================================
# SUPPLIER / STAFF / MATERIAL
# ============================================

@app.route("/purav/carting/suppliers")
def purav_suppliers():
    g = purav_guard()
    if g: return g
    return render_template("purav/suppliers.html", user=current_user(), role=current_role(),
                          name=current_name(), suppliers=database.get_suppliers())

@app.route("/purav/carting/suppliers/add", methods=["POST"])
def purav_suppliers_add():
    g = purav_guard()
    if g: return g
    name = request.form.get("name", "").strip()
    if not name: return redirect(url_for("purav_suppliers") + "?error=missing")
    database.add_supplier({
        "id": str(uuid.uuid4())[:8], "name": name,
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "gstin": request.form.get("gstin", "").strip(),
        "address": request.form.get("address", "").strip(),
        "type": request.form.get("type", "Material").strip(),
        "opening_balance": float(request.form.get("opening_balance", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_suppliers") + "?success=added")

@app.route("/purav/carting/suppliers/edit/<sid>", methods=["POST"])
def purav_suppliers_edit(sid):
    g = purav_guard()
    if g: return g
    database.update_supplier(sid, {
        "name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "gstin": request.form.get("gstin", "").strip(),
        "address": request.form.get("address", "").strip(),
        "type": request.form.get("type", "Material").strip(),
        "opening_balance": float(request.form.get("opening_balance", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
    })
    return redirect(url_for("purav_suppliers") + "?success=updated")

@app.route("/purav/carting/suppliers/delete/<sid>")
def purav_suppliers_delete(sid):
    g = purav_guard()
    if g: return g
    database.delete_supplier(sid)
    return redirect(url_for("purav_suppliers") + "?success=deleted")

@app.route("/purav/carting/staff")
def purav_staff():
    g = purav_guard()
    if g: return g
    return render_template("purav/staff.html", user=current_user(), role=current_role(),
                          name=current_name(), staff=database.get_staff())

@app.route("/purav/carting/staff/add", methods=["POST"])
def purav_staff_add():
    g = purav_guard()
    if g: return g
    name = request.form.get("name", "").strip()
    if not name: return redirect(url_for("purav_staff") + "?error=missing")
    database.add_staff({
        "id": str(uuid.uuid4())[:8], "name": name,
        "phone": request.form.get("phone", "").strip(),
        "role": request.form.get("role", "Labour").strip(),
        "salary_type": request.form.get("salary_type", "Daily").strip(),
        "rate": float(request.form.get("rate", 0) or 0),
        "address": request.form.get("address", "").strip(),
        "joining_date": request.form.get("joining_date", ""),
        "notes": request.form.get("notes", "").strip(),
        "status": request.form.get("status", "Active").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_staff") + "?success=added")

@app.route("/purav/carting/staff/edit/<sid>", methods=["POST"])
def purav_staff_edit(sid):
    g = purav_guard()
    if g: return g
    database.update_staff(sid, {
        "name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "role": request.form.get("role", "Labour").strip(),
        "salary_type": request.form.get("salary_type", "Daily").strip(),
        "rate": float(request.form.get("rate", 0) or 0),
        "address": request.form.get("address", "").strip(),
        "joining_date": request.form.get("joining_date", ""),
        "notes": request.form.get("notes", "").strip(),
        "status": request.form.get("status", "Active").strip(),
    })
    return redirect(url_for("purav_staff") + "?success=updated")

@app.route("/purav/carting/staff/delete/<sid>")
def purav_staff_delete(sid):
    g = purav_guard()
    if g: return g
    database.delete_staff(sid)
    return redirect(url_for("purav_staff") + "?success=deleted")

@app.route("/purav/carting/materials")
def purav_materials():
    g = purav_guard()
    if g: return g
    return render_template("purav/materials.html", user=current_user(), role=current_role(),
                          name=current_name(), materials=database.get_materials())

@app.route("/purav/carting/materials/add", methods=["POST"])
def purav_materials_add():
    g = purav_guard()
    if g: return g
    name = request.form.get("name", "").strip()
    if not name: return redirect(url_for("purav_materials") + "?error=missing")
    database.add_material({
        "id": str(uuid.uuid4())[:8], "name": name,
        "category": request.form.get("category", "Sand").strip(),
        "unit": request.form.get("unit", "Ton").strip(),
        "default_rate": float(request.form.get("default_rate", 0) or 0),
        "hsn": request.form.get("hsn", "").strip(),
        "gst_rate": float(request.form.get("gst_rate", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_materials") + "?success=added")

@app.route("/purav/carting/materials/edit/<mid>", methods=["POST"])
def purav_materials_edit(mid):
    g = purav_guard()
    if g: return g
    database.update_material(mid, {
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "Sand").strip(),
        "unit": request.form.get("unit", "Ton").strip(),
        "default_rate": float(request.form.get("default_rate", 0) or 0),
        "hsn": request.form.get("hsn", "").strip(),
        "gst_rate": float(request.form.get("gst_rate", 0) or 0),
        "notes": request.form.get("notes", "").strip(),
    })
    return redirect(url_for("purav_materials") + "?success=updated")

@app.route("/purav/carting/materials/delete/<mid>")
def purav_materials_delete(mid):
    g = purav_guard()
    if g: return g
    database.delete_material(mid)
    return redirect(url_for("purav_materials") + "?success=deleted")

# ============================================
# DAILY ENTRY
# ============================================

@app.route("/purav/carting/entry")
def purav_entry():
    g = purav_guard()
    if g: return g
    trucks = database.get_trucks()
    entries = database.get_entries()
    truck_map = {t["id"]: t for t in trucks}
    entries_sorted = sorted(entries, key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)[:100]
    for e in entries_sorted:
        e["truck_number"] = truck_map.get(e.get("truck_id", ""), {}).get("number", "—")
    return render_template("purav/entry.html", user=current_user(), role=current_role(),
                          name=current_name(), trucks=trucks, entries=entries_sorted,
                          today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/purav/carting/entry/add", methods=["POST"])
def purav_entry_add():
    g = purav_guard()
    if g: return g
    try:
        trips = int(request.form.get("trips", 0) or 0)
        sale = float(request.form.get("sale", 0) or 0)
        diesel = float(request.form.get("diesel", 0) or 0)
        labour = float(request.form.get("labour", 0) or 0)
        driver = float(request.form.get("driver", 0) or 0)
        maintenance = float(request.form.get("maintenance", 0) or 0)
        other = float(request.form.get("other", 0) or 0)
    except ValueError:
        return redirect(url_for("purav_entry") + "?error=invalid")
    total_cost = diesel + labour + driver + maintenance + other
    database.add_entry({
        "id": str(uuid.uuid4())[:8],
        "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
        "truck_id": request.form.get("truck_id", ""),
        "trips": trips, "sale": sale, "diesel": diesel, "labour": labour,
        "driver": driver, "maintenance": maintenance, "other": other,
        "total_cost": total_cost, "profit": sale - total_cost,
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_entry") + "?success=added")

@app.route("/purav/carting/entry/edit/<eid>", methods=["POST"])
def purav_entry_edit(eid):
    g = purav_guard()
    if g: return g
    try:
        trips = int(request.form.get("trips", 0) or 0)
        sale = float(request.form.get("sale", 0) or 0)
        diesel = float(request.form.get("diesel", 0) or 0)
        labour = float(request.form.get("labour", 0) or 0)
        driver = float(request.form.get("driver", 0) or 0)
        maintenance = float(request.form.get("maintenance", 0) or 0)
        other = float(request.form.get("other", 0) or 0)
    except ValueError:
        return redirect(url_for("purav_entry") + "?error=invalid")
    total_cost = diesel + labour + driver + maintenance + other
    database.update_entry(eid, {
        "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
        "truck_id": request.form.get("truck_id", ""),
        "trips": trips, "sale": sale, "diesel": diesel, "labour": labour,
        "driver": driver, "maintenance": maintenance, "other": other,
        "total_cost": total_cost, "profit": sale - total_cost,
        "notes": request.form.get("notes", "").strip(),
    })
    return redirect(url_for("purav_entry") + "?success=updated")

@app.route("/purav/carting/entry/delete/<eid>")
def purav_entry_delete(eid):
    g = purav_guard()
    if g: return g
    database.delete_entry(eid)
    return redirect(url_for("purav_entry") + "?success=deleted")

# ============================================
# CHALLAN
# ============================================

@app.route("/purav/carting/challan")
def purav_challan():
    g = purav_guard()
    if g: return g
    return render_template("purav/challan.html", user=current_user(), role=current_role(),
                          name=current_name(), customers=database.get_customers(),
                          trucks=database.get_trucks(), materials=database.get_materials(),
                          today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/purav/carting/challan/add", methods=["POST"])
def purav_challan_add():
    g = purav_guard()
    if g: return g
    customer_id = request.form.get("customer_id", "").strip()
    truck_id = request.form.get("truck_id", "").strip()
    material_id = request.form.get("material_id", "").strip()
    if not customer_id or not truck_id or not material_id:
        return redirect(url_for("purav_challan") + "?error=missing")
    customer = database.get_customer(customer_id) or {}
    truck = database.get_truck(truck_id) or {}
    material = database.get_material(material_id) or {}
    try:
        qty = float(request.form.get("quantity", 0) or 0)
        rate = float(request.form.get("rate", 0) or 0)
    except ValueError:
        return redirect(url_for("purav_challan") + "?error=invalid")
    challan_no = database.next_challan_no()
    database.add_challan({
        "id": str(uuid.uuid4())[:8],
        "challan_no": challan_no,
        "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
        "customer_id": customer_id,
        "customer_name": customer.get("name", ""),
        "truck_id": truck_id,
        "truck_number": truck.get("number", ""),
        "material_id": material_id,
        "material_name": material.get("name", ""),
        "unit": material.get("unit", "Ton"),
        "quantity": qty, "rate": rate, "amount": qty * rate,
        "driver": request.form.get("driver", "").strip(),
        "vehicle": request.form.get("vehicle", "").strip() or truck.get("number", ""),
        "notes": request.form.get("notes", "").strip(),
        "invoiced": False, "invoice_id": None,
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_challan_list") + "?success=added")

@app.route("/purav/carting/challan/list")
def purav_challan_list():
    g = purav_guard()
    if g: return g
    challans = database.get_challans()
    customer_filter = request.args.get("customer", "all")
    status_filter = request.args.get("status", "all")
    month_filter = request.args.get("month", "")

    filtered = []
    for c in challans:
        if customer_filter != "all" and c.get("customer_id") != customer_filter: continue
        if status_filter == "pending" and c.get("invoiced"): continue
        if status_filter == "invoiced" and not c.get("invoiced"): continue
        if month_filter and not c.get("date", "").startswith(month_filter): continue
        filtered.append(c)
    filtered.sort(key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)

    totals = {
        "count": len(filtered),
        "amount": sum(c.get("amount", 0) for c in filtered),
        "pending_count": len([c for c in filtered if not c.get("invoiced")]),
        "pending_amount": sum(c.get("amount", 0) for c in filtered if not c.get("invoiced")),
    }
    return render_template("purav/challan-list.html", user=current_user(), role=current_role(),
                          name=current_name(), challans=filtered, totals=totals,
                          customers=database.get_customers(),
                          customer_filter=customer_filter, status_filter=status_filter,
                          month_filter=month_filter)

@app.route("/purav/carting/challan/delete/<cid>")
def purav_challan_delete(cid):
    g = purav_guard()
    if g: return g
    c = database.get_challan(cid)
    if c and c.get("invoiced"):
        return redirect(url_for("purav_challan_list") + "?error=invoiced")
    database.delete_challan(cid)
    return redirect(url_for("purav_challan_list") + "?success=deleted")

@app.route("/purav/carting/challan/print/<cid>")
def purav_challan_print(cid):
    g = purav_guard()
    if g: return g
    challan = database.get_challan(cid)
    if not challan: return redirect(url_for("purav_challan_list"))
    return render_template("purav/challan-print.html", user=current_user(), role=current_role(),
                          name=current_name(), challan=challan, settings=database.get_settings())

# ============================================
# PURCHASE
# ============================================

@app.route("/purav/carting/purchase")
def purav_purchase():
    g = purav_guard()
    if g: return g
    return render_template("purav/purchase.html", user=current_user(), role=current_role(),
                          name=current_name(), suppliers=database.get_suppliers(),
                          materials=database.get_materials(),
                          today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/purav/carting/purchase/add", methods=["POST"])
def purav_purchase_add():
    g = purav_guard()
    if g: return g
    supplier_id = request.form.get("supplier_id", "").strip()
    material_id = request.form.get("material_id", "").strip()
    if not supplier_id or not material_id:
        return redirect(url_for("purav_purchase") + "?error=missing")
    supplier = database.get_supplier(supplier_id) or {}
    material = database.get_material(material_id) or {}
    try:
        qty = float(request.form.get("quantity", 0) or 0)
        rate = float(request.form.get("rate", 0) or 0)
    except ValueError:
        return redirect(url_for("purav_purchase") + "?error=invalid")
    database.add_purchase({
        "id": str(uuid.uuid4())[:8],
        "bill_no": request.form.get("bill_no", "").strip(),
        "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
        "supplier_id": supplier_id,
        "supplier_name": supplier.get("name", ""),
        "material_id": material_id,
        "material_name": material.get("name", ""),
        "unit": material.get("unit", "Ton"),
        "quantity": qty, "rate": rate, "amount": qty * rate,
        "vehicle": request.form.get("vehicle", "").strip(),
        "driver": request.form.get("driver", "").strip(),
        "payment_status": request.form.get("payment_status", "Pending").strip(),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_purchase_list") + "?success=added")

@app.route("/purav/carting/purchase/list")
def purav_purchase_list():
    g = purav_guard()
    if g: return g
    purchases = database.get_purchases()
    supplier_filter = request.args.get("supplier", "all")
    month_filter = request.args.get("month", "")

    filtered = []
    for p in purchases:
        if supplier_filter != "all" and p.get("supplier_id") != supplier_filter: continue
        if month_filter and not p.get("date", "").startswith(month_filter): continue
        filtered.append(p)
    filtered.sort(key=lambda x: (x.get("date", ""), x.get("created_at", "")), reverse=True)

    totals = {
        "count": len(filtered),
        "amount": sum(p.get("amount", 0) for p in filtered),
        "paid": sum(p.get("amount", 0) for p in filtered if p.get("payment_status") == "Paid"),
        "pending": sum(p.get("amount", 0) for p in filtered if p.get("payment_status") != "Paid"),
    }
    return render_template("purav/purchase-list.html", user=current_user(), role=current_role(),
                          name=current_name(), purchases=filtered, totals=totals,
                          suppliers=database.get_suppliers(),
                          supplier_filter=supplier_filter, month_filter=month_filter)

@app.route("/purav/carting/purchase/delete/<pid>")
def purav_purchase_delete(pid):
    g = purav_guard()
    if g: return g
    database.delete_purchase(pid)
    return redirect(url_for("purav_purchase_list") + "?success=deleted")

@app.route("/purav/carting/purchase/mark-paid/<pid>")
def purav_purchase_mark_paid(pid):
    g = purav_guard()
    if g: return g
    database.update_purchase(pid, {"payment_status": "Paid"})
    return redirect(url_for("purav_purchase_list") + "?success=paid")

# ============================================
# LEDGER
# ============================================

@app.route("/purav/carting/ledger")
def purav_ledger():
    g = purav_guard()
    if g: return g
    trucks = database.get_trucks()
    entries = database.get_entries()
    truck_map = {t["id"]: t for t in trucks}
    truck_filter = request.args.get("truck", "all")
    month_filter = request.args.get("month", datetime.now().strftime("%Y-%m"))
    filtered = []
    for e in entries:
        if month_filter and not e.get("date", "").startswith(month_filter): continue
        if truck_filter != "all" and e.get("truck_id") != truck_filter: continue
        e["truck_number"] = truck_map.get(e.get("truck_id", ""), {}).get("number", "—")
        filtered.append(e)
    filtered.sort(key=lambda x: x.get("date", ""))
    totals = {
        "trips": sum(e.get("trips", 0) for e in filtered),
        "sale": sum(e.get("sale", 0) for e in filtered),
        "diesel": sum(e.get("diesel", 0) for e in filtered),
        "labour": sum(e.get("labour", 0) for e in filtered),
        "driver": sum(e.get("driver", 0) for e in filtered),
        "maintenance": sum(e.get("maintenance", 0) for e in filtered),
        "other": sum(e.get("other", 0) for e in filtered),
        "total_cost": sum(e.get("total_cost", 0) for e in filtered),
        "profit": sum(e.get("profit", 0) for e in filtered),
    }
    return render_template("purav/ledger.html", user=current_user(), role=current_role(),
                          name=current_name(), trucks=trucks, entries=filtered,
                          totals=totals, truck_filter=truck_filter, month_filter=month_filter)

# ============================================
# ADMIN / OWNER
# ============================================

@app.route("/admin")
def admin():
    if not require_admin(): return redirect(url_for("login"))
    return render_template("admin.html", user=current_user(), role=current_role(),
                          name=current_name(), all_users=database.load_users(),
                          all_prompts=database.load_prompts())

@app.route("/admin/add-user", methods=["POST"])
def admin_add_user():
    if not require_admin(): return redirect(url_for("login"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "user").strip()
    name = request.form.get("name", "").strip() or username
    if not username or not password: return redirect(url_for("admin") + "?tab=users&error=missing")
    if role not in ("admin", "owner", "manager", "hr", "staff", "user"): role = "user"
    if current_role() == "owner" and role == "admin": role = "owner"
    database.add_user(username, password, role, name)
    return redirect(url_for("admin") + "?tab=users&success=added")

@app.route("/admin/delete-user/<username>")
def admin_delete_user(username):
    if not require_admin(): return redirect(url_for("login"))
    if username == current_user(): return redirect(url_for("admin") + "?tab=users&error=self")
    if username == "admin": return redirect(url_for("admin") + "?tab=users&error=protected")
    database.delete_user(username)
    return redirect(url_for("admin") + "?tab=users&success=deleted")

@app.route("/admin/add-prompt", methods=["POST"])
def admin_add_prompt():
    if not require_admin(): return redirect(url_for("login"))
    key = request.form.get("key", "").strip().lower().replace(" ", "-")
    title = request.form.get("title", "").strip()
    sub = request.form.get("sub", "").strip()
    cat = request.form.get("cat", "single").strip()
    text = request.form.get("text", "").strip()
    if not key or not title or not text: return redirect(url_for("admin") + "?tab=prompts&error=missing")
    database.add_prompt(key, {"title": title, "sub": sub, "cat": cat,
        "steps": [{"label": "Prompt", "name": title, "text": text}]})
    return redirect(url_for("admin") + "?tab=prompts&success=added")

@app.route("/admin/edit-prompt/<key>", methods=["GET", "POST"])
def admin_edit_prompt(key):
    if not require_admin(): return redirect(url_for("login"))
    prompts = database.load_prompts()
    if key not in prompts: return redirect(url_for("admin") + "?tab=prompts&error=notfound")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        sub = request.form.get("sub", "").strip()
        cat = request.form.get("cat", "single").strip()
        text = request.form.get("text", "").strip()
        if not title or not text: return redirect(url_for("admin") + "?tab=prompts&error=missing")
        prompts[key]["title"] = title
        prompts[key]["sub"] = sub
        prompts[key]["cat"] = cat
        prompts[key]["steps"] = [{"label": "Prompt", "name": title, "text": text}]
        database.save_prompts(prompts)
        return redirect(url_for("admin") + "?tab=prompts&success=updated")
    return render_template("edit-prompt.html", user=current_user(), role=current_role(),
                          name=current_name(), key=key, prompt=prompts[key])

@app.route("/admin/delete-prompt/<key>")
def admin_delete_prompt(key):
    if not require_admin(): return redirect(url_for("login"))
    database.delete_prompt(key)
    return redirect(url_for("admin") + "?tab=prompts&success=deleted")

@app.route("/admin/delete-all-prompts")
def admin_delete_all_prompts():
    if not require_admin(): return redirect(url_for("login"))
    database.save_prompts({})
    return redirect(url_for("admin") + "?tab=prompts&success=all_deleted")

@app.route("/owner")
def owner():
    if not require_owner(): return redirect(url_for("login"))
    return render_template("owner.html", user=current_user(), role=current_role(),
                          name=current_name(), all_users=database.load_users())

@app.route("/owner/add-user", methods=["POST"])
def owner_add_user():
    if not require_owner(): return redirect(url_for("login"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "user").strip()
    name = request.form.get("name", "").strip() or username
    if not username or not password: return redirect(url_for("owner") + "?tab=roles&error=missing")
    if role not in ("admin", "owner", "manager", "hr", "staff", "user"): role = "user"
    if current_role() == "owner" and role == "admin": role = "owner"
    database.add_user(username, password, role, name)
    return redirect(url_for("owner") + "?tab=roles&success=added")

@app.route("/owner/delete-user/<username>")
def owner_delete_user(username):
    if not require_owner(): return redirect(url_for("login"))
    if username == current_user(): return redirect(url_for("owner") + "?tab=roles&error=self")
    if username == "admin": return redirect(url_for("owner") + "?tab=roles&error=protected")
    database.delete_user(username)
    return redirect(url_for("owner") + "?tab=roles&success=deleted")

@app.route("/owner/update-role", methods=["POST"])
def owner_update_role():
    if not require_owner(): return redirect(url_for("login"))
    username = request.form.get("username", "").strip()
    role = request.form.get("role", "").strip()
    if username == "admin": return redirect(url_for("owner") + "?tab=roles&error=protected")
    if username and role in ("admin", "owner", "manager", "hr", "staff", "user"):
        if current_role() == "owner" and role == "admin": role = "owner"
        database.update_user(username, role=role)
    return redirect(url_for("owner") + "?tab=roles&success=updated")

# ============================================
# TOOLS
# ============================================

@app.route("/tools/invoice")
def invoice_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("invoice.html", name=current_name())

@app.route("/tools/gst")
def gst_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("gst.html", name=current_name())

@app.route("/tools/emi")
def emi_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("emi.html", name=current_name())

@app.route("/tools/age")
def age_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("age.html", name=current_name())

@app.route("/tools/number-to-words")
def number_to_words_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("number-to-words.html", name=current_name())

@app.route("/tools/unit-converter")
def unit_converter_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("unit-converter.html", name=current_name())

@app.route("/tools/text-tools")
def text_tools():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("text-tools.html", name=current_name())

@app.route("/tools/qr-code")
def qr_code_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("qr-code.html", name=current_name())

@app.route("/tools/qr-code/process", methods=["POST"])
def qr_code_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        import qrcode
        text = request.form.get("text", "").strip()
        size = int(request.form.get("size", 300))
        if not text: return "Kuch text daalo", 400
        if size < 100 or size > 1000: size = 300
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(text); qr.make(fit=True)
        img = qr.make_image(fill_color="#1a1a1a", back_color="white").convert("RGB")
        img = img.resize((size, size), Image.LANCZOS)
        output = io.BytesIO(); img.save(output, format="PNG"); output.seek(0)
        return send_file(output, mimetype="image/png", as_attachment=True, download_name="gd-pulse-qr.png")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/image-resize")
def image_resize_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("image-resize.html", name=current_name())

@app.route("/tools/image-resize/process", methods=["POST"])
def image_resize_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        file = request.files.get("image")
        if not file or file.filename == "": return "Koi image select nahi ki", 400
        width = int(request.form.get("width", 0)); height = int(request.form.get("height", 0))
        if width <= 0 or height <= 0: return "Sahi width/height daalo", 400
        img = Image.open(file.stream); resized = img.resize((width, height), Image.LANCZOS)
        output = io.BytesIO(); fmt = img.format if img.format else "PNG"
        if fmt not in ("JPEG","PNG","WEBP","GIF","BMP"): fmt = "PNG"
        if fmt == "JPEG" and resized.mode in ("RGBA","P"): resized = resized.convert("RGB")
        resized.save(output, format=fmt); output.seek(0)
        base = os.path.splitext(file.filename)[0]; ext = fmt.lower() if fmt != "JPEG" else "jpg"
        return send_file(output, mimetype=f"image/{ext}", as_attachment=True, download_name=f"{base}_{width}x{height}.{ext}")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/image-compress")
def image_compress_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("image-compress.html", name=current_name())

@app.route("/tools/image-compress/process", methods=["POST"])
def image_compress_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        file = request.files.get("image")
        if not file or file.filename == "": return "Koi image select nahi ki", 400
        quality = int(request.form.get("quality", 70))
        if quality < 1 or quality > 100: return "Quality 1 se 100 ke beech honi chahiye", 400
        img = Image.open(file.stream)
        if img.mode in ("RGBA","P","LA"): img = img.convert("RGB")
        output = io.BytesIO(); img.save(output, format="JPEG", quality=quality, optimize=True); output.seek(0)
        base = os.path.splitext(file.filename)[0]
        return send_file(output, mimetype="image/jpeg", as_attachment=True, download_name=f"{base}_compressed.jpg")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/image-crop")
def image_crop_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("image-crop.html", name=current_name())

@app.route("/tools/image-crop/process", methods=["POST"])
def image_crop_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        file = request.files.get("image")
        if not file or file.filename == "": return "Koi image select nahi ki", 400
        x = int(request.form.get("x", 0)); y = int(request.form.get("y", 0))
        width = int(request.form.get("width", 0)); height = int(request.form.get("height", 0))
        if width <= 0 or height <= 0: return "Sahi width/height daalo", 400
        img = Image.open(file.stream); img_w, img_h = img.size
        x = max(0, min(x, img_w - 1)); y = max(0, min(y, img_h - 1))
        width = min(width, img_w - x); height = min(height, img_h - y)
        cropped = img.crop((x, y, x + width, y + height))
        output = io.BytesIO(); fmt = img.format if img.format else "PNG"
        if fmt not in ("JPEG","PNG","WEBP","GIF","BMP"): fmt = "PNG"
        if fmt == "JPEG" and cropped.mode in ("RGBA","P"): cropped = cropped.convert("RGB")
        cropped.save(output, format=fmt); output.seek(0)
        base = os.path.splitext(file.filename)[0]; ext = fmt.lower() if fmt != "JPEG" else "jpg"
        return send_file(output, mimetype=f"image/{ext}", as_attachment=True, download_name=f"{base}_cropped.{ext}")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/photo-to-pdf")
def photo_to_pdf_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("photo-to-pdf.html", name=current_name())

@app.route("/tools/photo-to-pdf/process", methods=["POST"])
def photo_to_pdf_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        files = request.files.getlist("images")
        files = [f for f in files if f and f.filename != ""]
        if not files: return "Koi image select nahi ki", 400
        images = []
        for f in files:
            img = Image.open(f.stream)
            if img.mode != "RGB": img = img.convert("RGB")
            images.append(img)
        first = images[0]; rest = images[1:]
        output = io.BytesIO()
        first.save(output, format="PDF", save_all=True, append_images=rest); output.seek(0)
        return send_file(output, mimetype="application/pdf", as_attachment=True, download_name="gd-pulse-images.pdf")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/pdf-merge")
def pdf_merge_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("pdf-merge.html", name=current_name())

@app.route("/tools/pdf-merge/process", methods=["POST"])
def pdf_merge_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        from pypdf import PdfWriter, PdfReader
        files = request.files.getlist("pdfs")
        files = [f for f in files if f and f.filename != ""]
        if len(files) < 2: return "Kam se kam 2 PDF files select karo", 400
        writer = PdfWriter()
        for f in files:
            reader = PdfReader(f.stream)
            for page in reader.pages: writer.add_page(page)
        output = io.BytesIO(); writer.write(output); output.seek(0)
        return send_file(output, mimetype="application/pdf", as_attachment=True, download_name="gd-pulse-merged.pdf")
    except Exception as e: return f"Error: {str(e)}", 500

@app.route("/tools/video-to-mp3")
def video_to_mp3_tool():
    if not require_staff(): return redirect(url_for("login"))
    return render_template("video-to-mp3.html", name=current_name())

@app.route("/tools/video-to-mp3/process", methods=["POST"])
def video_to_mp3_process():
    if not require_staff(): return redirect(url_for("login"))
    try:
        file = request.files.get("video")
        if not file or file.filename == "": return "Koi video select nahi ki", 400
        input_path = "/tmp/input_video"; output_path = "/tmp/output_audio.mp3"
        file.save(input_path)
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(output_path, codec="mp3", verbose=False, logger=None)
        clip.close()
        base = os.path.splitext(file.filename)[0]
        return send_file(output_path, mimetype="audio/mpeg", as_attachment=True, download_name=f"{base}.mp3")
    except Exception as e: return f"Error: {str(e)}", 500

@app.errorhandler(413)
def too_large(e):
    return "File bahut badi hai. Max 25MB allowed hai.", 413

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
