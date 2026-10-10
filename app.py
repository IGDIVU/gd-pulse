@app.route("/purav/carting/invoice-items")
def purav_invoice_items():
    g = purav_guard()
    if g: return g
    return render_template("purav/invoice-items.html", user=current_user(), role=current_role(),
                          name=current_name(), customers=database.get_customers(),
                          materials=database.get_materials(),
                          today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/purav/carting/invoice-items/add", methods=["POST"])
def purav_invoice_items_add():
    g = purav_guard()
    if g: return g
    customer_id = request.form.get("customer_id", "").strip()
    if not customer_id:
        return redirect(url_for("purav_invoice_items") + "?error=missing")
    customer = database.get_customer(customer_id) or {}

    # Collect items from form
    items = []
    descs = request.form.getlist("item_desc[]")
    hsns = request.form.getlist("item_hsn[]")
    qtys = request.form.getlist("item_qty[]")
    units = request.form.getlist("item_unit[]")
    rates = request.form.getlist("item_rate[]")
    cgsts = request.form.getlist("item_cgst[]")
    sgsts = request.form.getlist("item_sgst[]")
    mrps = request.form.getlist("item_mrp[]")

    subtotal = 0
    total_cgst = 0
    total_sgst = 0

    for i in range(len(descs)):
        desc = descs[i].strip()
        if not desc: continue
        try:
            qty = float(qtys[i] or 0)
            rate = float(rates[i] or 0)
            cgst_p = float(cgsts[i] or 0)
            sgst_p = float(sgsts[i] or 0)
            mrp = float(mrps[i] or 0) if i < len(mrps) else 0
        except ValueError:
            continue
        amount = qty * rate
        subtotal += amount
        total_cgst += amount * cgst_p / 100
        total_sgst += amount * sgst_p / 100
        items.append({
            "desc": desc, "hsn": hsns[i] if i < len(hsns) else "",
            "qty": qty, "unit": units[i] if i < len(units) else "Ton",
            "rate": rate, "mrp": mrp, "amount": amount,
            "cgst_pct": cgst_p, "sgst_pct": sgst_p,
            "cgst_amt": amount * cgst_p / 100,
            "sgst_amt": amount * sgst_p / 100
        })

    if not items:
        return redirect(url_for("purav_invoice_items") + "?error=noitems")

    total = subtotal + total_cgst + total_sgst
    total_rounded = round(total)
    round_off = total_rounded - total

    invoice_id = str(uuid.uuid4())[:8]
    invoice_no = database.next_item_invoice_no()

    database.add_item_invoice({
        "id": invoice_id, "invoice_no": invoice_no,
        "date": request.form.get("date", datetime.now().strftime("%Y-%m-%d")),
        "due_date": request.form.get("due_date", ""),
        "customer_id": customer_id, "customer_name": customer.get("name", ""),
        "customer_gstin": customer.get("gstin", ""),
        "customer_address": customer.get("address", ""),
        "customer_state": customer.get("state", ""),
        "customer_pan": customer.get("pan", ""),
        "items": items,
        "subtotal": subtotal, "cgst": total_cgst, "sgst": total_sgst,
        "total": total_rounded, "round_off": round_off,
        "items_per_page": int(request.form.get("items_per_page", 19) or 19),
        "notes": request.form.get("notes", "").strip(),
        "created_at": datetime.now().isoformat()
    })
    return redirect(url_for("purav_invoice_items_view", iid=invoice_id) + "?success=created")

@app.route("/purav/carting/invoice-items/view/<iid>")
def purav_invoice_items_view(iid):
    g = purav_guard()
    if g: return g
    inv = database.get_item_invoice(iid)
    if not inv: return redirect(url_for("purav_invoice_items"))
    return render_template("purav/invoice-items-print.html", user=current_user(), role=current_role(),
                          name=current_name(), invoice=inv, settings=database.get_settings())

@app.route("/purav/carting/invoice-items/delete/<iid>")
def purav_invoice_items_delete(iid):
    g = purav_guard()
    if g: return g
    database.delete_item_invoice(iid)
    return redirect(url_for("purav_invoice_items") + "?success=deleted")
