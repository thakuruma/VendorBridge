from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from database import get_db, init_db
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os, random, string, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
app.secret_key = 'vendorbridge2026'
CORS(app)

init_db()

# ─── AUTH ───────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=? AND password=?',
                         (data['email'], data['password'])).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return jsonify({'success': True, 'role': user['role']})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    db = get_db()
    try:
        db.execute('INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)',
                  (data['name'], data['email'], data['password'], data.get('role', 'officer')))
        db.commit()
        db.close()
        return jsonify({'success': True})
    except:
        db.close()
        return jsonify({'success': False, 'message': 'Email already exists'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── DASHBOARD ──────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/api/dashboard-stats')
def dashboard_stats():
    db = get_db()
    vendors = db.execute('SELECT COUNT(*) as c FROM vendors').fetchone()['c']
    rfqs = db.execute('SELECT COUNT(*) as c FROM rfqs').fetchone()['c']
    pos = db.execute('SELECT COUNT(*) as c FROM purchase_orders').fetchone()['c']
    invoices = db.execute('SELECT COUNT(*) as c FROM invoices').fetchone()['c']
    db.close()
    return jsonify({'vendors': vendors, 'rfqs': rfqs, 'pos': pos, 'invoices': invoices})

# ─── VENDORS ────────────────────────────────────────
@app.route('/vendors')
def vendors():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('vendors.html')

@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    db = get_db()
    vendors = db.execute('SELECT * FROM vendors').fetchall()
    db.close()
    return jsonify([dict(v) for v in vendors])

@app.route('/api/vendors', methods=['POST'])
def add_vendor():
    data = request.json
    db = get_db()
    db.execute('INSERT INTO vendors (name, email, phone, category, gst, status) VALUES (?,?,?,?,?,?)',
              (data['name'], data['email'], data['phone'], data['category'], data['gst'], 'active'))
    db.commit()
    db.close()
    return jsonify({'success': True})

@app.route('/api/vendors/<int:id>', methods=['DELETE'])
def delete_vendor(id):
    db = get_db()
    db.execute('DELETE FROM vendors WHERE id=?', (id,))
    db.commit()
    db.close()
    return jsonify({'success': True})

# ─── RFQ ────────────────────────────────────────────
@app.route('/rfq')
def rfq():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('rfq.html')

@app.route('/api/rfqs', methods=['GET'])
def get_rfqs():
    db = get_db()
    rfqs = db.execute('''SELECT r.*, v.name as vendor_name 
                         FROM rfqs r LEFT JOIN vendors v ON r.vendor_id = v.id''').fetchall()
    db.close()
    return jsonify([dict(r) for r in rfqs])

@app.route('/api/rfqs', methods=['POST'])
def create_rfq():
    data = request.json
    db = get_db()
    db.execute('INSERT INTO rfqs (title, description, quantity, deadline, vendor_id, created_by) VALUES (?,?,?,?,?,?)',
              (data['title'], data['description'], data['quantity'], data['deadline'],
               data['vendor_id'], session.get('user_id', 1)))
    db.commit()
    db.close()
    return jsonify({'success': True})

# ─── QUOTATIONS ─────────────────────────────────────
@app.route('/quotations')
def quotations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('quotations.html')

@app.route('/api/quotations', methods=['GET'])
def get_quotations():
    db = get_db()
    quotes = db.execute('''SELECT q.*, r.title as rfq_title, v.name as vendor_name
                           FROM quotations q 
                           JOIN rfqs r ON q.rfq_id = r.id
                           JOIN vendors v ON q.vendor_id = v.id''').fetchall()
    db.close()
    return jsonify([dict(q) for q in quotes])

@app.route('/api/quotations', methods=['POST'])
def add_quotation():
    data = request.json
    db = get_db()
    db.execute('INSERT INTO quotations (rfq_id, vendor_id, price, delivery_days, notes) VALUES (?,?,?,?,?)',
              (data['rfq_id'], data['vendor_id'], data['price'], data['delivery_days'], data['notes']))
    db.commit()
    db.close()
    return jsonify({'success': True})

@app.route('/api/quotations/<int:id>/approve', methods=['POST'])
def approve_quotation(id):
    db = get_db()
    db.execute('UPDATE quotations SET status=? WHERE id=?', ('approved', id))
    quote = db.execute('SELECT * FROM quotations WHERE id=?', (id,)).fetchone()
    po_number = 'PO-' + ''.join(random.choices(string.digits, k=6))
    db.execute('INSERT INTO purchase_orders (po_number, rfq_id, vendor_id, quotation_id, total_amount) VALUES (?,?,?,?,?)',
              (po_number, quote['rfq_id'], quote['vendor_id'], id, quote['price']))
    db.commit()
    db.close()
    return jsonify({'success': True, 'po_number': po_number})

# ─── PURCHASE ORDERS ────────────────────────────────
@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('orders.html')

@app.route('/api/orders', methods=['GET'])
def get_orders():
    db = get_db()
    orders = db.execute('''SELECT p.*, v.name as vendor_name 
                           FROM purchase_orders p 
                           JOIN vendors v ON p.vendor_id = v.id''').fetchall()
    db.close()
    return jsonify([dict(o) for o in orders])

@app.route('/api/orders/<int:id>/invoice', methods=['POST'])
def generate_invoice(id):
    db = get_db()
    order = db.execute('SELECT * FROM purchase_orders WHERE id=?', (id,)).fetchone()
    invoice_number = 'INV-' + ''.join(random.choices(string.digits, k=6))
    tax = order['total_amount'] * 0.18
    total = order['total_amount'] + tax
    db.execute('INSERT INTO invoices (invoice_number, po_id, amount, tax, total) VALUES (?,?,?,?,?)',
              (invoice_number, id, order['total_amount'], tax, total))
    db.execute('UPDATE purchase_orders SET status=? WHERE id=?', ('invoiced', id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'invoice_number': invoice_number})

# ─── INVOICES ───────────────────────────────────────
@app.route('/invoices')
def invoices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('invoices.html')

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    db = get_db()
    invs = db.execute('''SELECT i.*, p.po_number, v.name as vendor_name
                         FROM invoices i
                         JOIN purchase_orders p ON i.po_id = p.id
                         JOIN vendors v ON p.vendor_id = v.id''').fetchall()
    db.close()
    return jsonify([dict(i) for i in invs])

@app.route('/api/invoices/<int:id>/pdf')
def download_invoice_pdf(id):
    db = get_db()
    inv = db.execute('''SELECT i.*, p.po_number, v.name as vendor_name
                        FROM invoices i
                        JOIN purchase_orders p ON i.po_id = p.id
                        JOIN vendors v ON p.vendor_id = v.id
                        WHERE i.id=?''', (id,)).fetchone()
    db.close()

    filename = f"invoice_{inv['invoice_number']}.pdf"
    filepath = os.path.join('static', filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, "VendorBridge Invoice")
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Invoice Number: {inv['invoice_number']}")
    c.drawString(50, 680, f"PO Number: {inv['po_number']}")
    c.drawString(50, 660, f"Vendor: {inv['vendor_name']}")
    c.drawString(50, 620, f"Amount: Rs. {inv['amount']:.2f}")
    c.drawString(50, 600, f"Tax (18% GST): Rs. {inv['tax']:.2f}")
    c.drawString(50, 580, f"Total: Rs. {inv['total']:.2f}")
    c.drawString(50, 540, f"Status: {inv['status']}")
    c.save()

    return jsonify({'success': True, 'url': f'/static/{filename}'})


@app.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('logs.html')

@app.route('/api/logs')
def get_logs():
    db = get_db()
    vendors = db.execute('SELECT id, name, "Vendor Added" as action, "vendor" as type FROM vendors').fetchall()
    rfqs = db.execute('SELECT id, title as name, "RFQ Created" as action, "rfq" as type FROM rfqs').fetchall()
    quotes = db.execute('SELECT id, price as name, "Quotation Submitted" as action, "quotation" as type FROM quotations').fetchall()
    pos = db.execute('SELECT id, po_number as name, "Purchase Order Created" as action, "po" as type FROM purchase_orders').fetchall()
    invs = db.execute('SELECT id, invoice_number as name, "Invoice Generated" as action, "invoice" as type FROM invoices').fetchall()
    db.close()

    all_logs = []
    for v in vendors:
        all_logs.append({'action': v['action'], 'detail': v['name'], 'type': v['type'], 'icon': '🏭'})
    for r in rfqs:
        all_logs.append({'action': r['action'], 'detail': r['name'], 'type': r['type'], 'icon': '📋'})
    for q in quotes:
        all_logs.append({'action': q['action'], 'detail': f"Rs. {q['name']}", 'type': q['type'], 'icon': '💬'})
    for p in pos:
        all_logs.append({'action': p['action'], 'detail': p['name'], 'type': p['type'], 'icon': '📦'})
    for i in invs:
        all_logs.append({'action': i['action'], 'detail': i['name'], 'type': i['type'], 'icon': '🧾'})

    return jsonify(all_logs)

    # ─── REPORTS ────────────────────────────────────────
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/api/reports')
def get_reports():
    db = get_db()
    total_vendors = db.execute('SELECT COUNT(*) as c FROM vendors').fetchone()['c']
    total_rfqs = db.execute('SELECT COUNT(*) as c FROM rfqs').fetchone()['c']
    total_pos = db.execute('SELECT COUNT(*) as c FROM purchase_orders').fetchone()['c']
    total_invoices = db.execute('SELECT COUNT(*) as c FROM invoices').fetchone()['c']
    total_spending = db.execute('SELECT SUM(total) as t FROM invoices').fetchone()['t'] or 0
    top_vendors = db.execute('''
        SELECT v.name, COUNT(p.id) as orders, SUM(p.total_amount) as total
        FROM vendors v
        LEFT JOIN purchase_orders p ON v.id = p.vendor_id
        GROUP BY v.id ORDER BY orders DESC
    ''').fetchall()
    db.close()
    return jsonify({
        'total_vendors': total_vendors,
        'total_rfqs': total_rfqs,
        'total_pos': total_pos,
        'total_invoices': total_invoices,
        'total_spending': round(total_spending, 2),
        'top_vendors': [dict(v) for v in top_vendors]
    })

# ─── EMAIL INVOICE ──────────────────────────────────
@app.route('/api/invoices/<int:id>/email', methods=['POST'])
def email_invoice(id):
    data = request.json
    recipient_email = data.get('email')

    db = get_db()
    inv = db.execute('''SELECT i.*, p.po_number, v.name as vendor_name, v.email as vendor_email
                        FROM invoices i
                        JOIN purchase_orders p ON i.po_id = p.id
                        JOIN vendors v ON p.vendor_id = v.id
                        WHERE i.id=?''', (id,)).fetchone()
    db.close()

    # Generate PDF first
    filename = f"invoice_{inv['invoice_number']}.pdf"
    filepath = os.path.join('static', filename)

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, "VendorBridge Invoice")
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Invoice Number: {inv['invoice_number']}")
    c.drawString(50, 680, f"PO Number: {inv['po_number']}")
    c.drawString(50, 660, f"Vendor: {inv['vendor_name']}")
    c.drawString(50, 620, f"Amount: Rs. {inv['amount']:.2f}")
    c.drawString(50, 600, f"Tax (18% GST): Rs. {inv['tax']:.2f}")
    c.drawString(50, 580, f"Total: Rs. {inv['total']:.2f}")
    c.save()

    try:
        # Email config - use your gmail
        sender_email = "vendorbridge2026@gmail.com"
        sender_password = "your_app_password"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Invoice {inv['invoice_number']} from VendorBridge"

        body = f"""
Dear {inv['vendor_name']},

Please find attached your invoice from VendorBridge.

Invoice Details:
- Invoice Number: {inv['invoice_number']}
- PO Number: {inv['po_number']}
- Amount: Rs. {inv['amount']:.2f}
- Tax (18% GST): Rs. {inv['tax']:.2f}
- Total Amount: Rs. {inv['total']:.2f}

Thank you for your business!

Best regards,
VendorBridge Team
        """
        msg.attach(MIMEText(body, 'plain'))

        # Attach PDF
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        return jsonify({'success': True, 'message': 'Email sent successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)