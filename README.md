# 🏢 VendorBridge — Procurement & Vendor Management ERP

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![HTML](https://img.shields.io/badge/HTML5-CSS3-orange?logo=html5)
![License](https://img.shields.io/badge/License-MIT-green)

> A full-featured **Procurement & Vendor Management ERP** built with Python (Flask) + HTML/CSS/JS. Designed to digitize and streamline procurement operations for organizations.

---

## 📌 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [User Roles](#user-roles)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Demo Accounts](#demo-accounts)
- [Workflow](#workflow)
- [Screenshots](#screenshots)

---

## 📖 About the Project

**VendorBridge** is a centralized ERP platform that manages the complete procurement lifecycle — from vendor registration to invoice generation. It eliminates manual procurement inefficiencies by enabling structured workflows, centralized vendor communication, and real-time procurement tracking.

Built as part of a Hackathon project to demonstrate proper ERP architecture with role-based workflows and intuitive UI/UX.

---

## ✨ Features

| Module | Functionality |
|--------|--------------|
| 🔐 **Authentication** | Login, Signup, Role-based access, Session handling |
| 📊 **Dashboard** | Pending approvals, Active RFQs, Analytics cards, Quick actions |
| 🏪 **Vendor Management** | Register vendors, GST details, Categories, Status tracking, Search & filter |
| 📋 **RFQ Creation** | Create RFQs, Add items/quantities, Set deadlines, Assign vendors |
| 💬 **Quotation Submission** | Vendors submit pricing, delivery timelines, notes |
| ⚖️ **Quotation Comparison** | Side-by-side comparison, Lowest price highlight, Delivery timeline |
| ✅ **Approval Workflow** | Approve/Reject with remarks, Status tracking, Timeline |
| 📦 **Purchase Orders** | Auto-generated PO numbers, Tax calculations, Status updates |
| 🧾 **Invoice Generation** | Generate from PO, Download PDF, Print invoice, Send via email |
| 📜 **Activity Logs** | Audit trail, Notifications, Procurement timeline |
| 📈 **Reports & Analytics** | Vendor performance, Spending summaries, Procurement stats |

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Manage users, Manage vendors, View analytics |
| **Procurement Officer** | Create RFQs, Compare quotations, Generate POs & Invoices |
| **Manager / Approver** | Approve or reject procurement requests, Monitor workflows |
| **Vendor** | Submit quotations, Track RFQ status, View purchase orders |

---

## 🛠 Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** JSON file / SQLite
- **PDF Generation:** jsPDF / html2canvas
- **Version Control:** Git & GitHub

---

## 📁 Project Structure

```
VendorBridge/
├── app.py                  # Main Flask application
├── database.py             # Database helper functions
├── data.json               # JSON data store
├── vendorbridge.db         # SQLite database
├── requirements.txt        # Python dependencies
├── static/
│   └── style.css           # Global styles
├── templates/
│   ├── login.html          # Login page
│   ├── dashboard.html      # Dashboard
│   ├── vendors.html        # Vendor management
│   ├── rfq.html            # RFQ creation
│   ├── quotations.html     # Quotation submission & comparison
│   ├── orders.html         # Purchase orders
│   ├── invoices.html       # Invoice generation
│   └── logs.html           # Activity logs
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed
- Git installed

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/thakuruma/VendorBridge.git
cd VendorBridge
```

**2. Create virtual environment**
```bash
python -m venv venv
```

**3. Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Run the application**
```bash
python app.py
```

**6. Open in browser**
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@vb.com | admin123 |
| Procurement Officer | officer@vb.com | officer123 |
| Manager | manager@vb.com | manager123 |
| Vendor | vendor@vb.com | vendor123 |

---

## 🔄 Basic Workflow

```
1. Procurement Officer creates an RFQ
        ↓
2. Vendors receive invitations & submit quotations
        ↓
3. Procurement team compares quotations
        ↓
4. Approval workflow is initiated
        ↓
5. Approved quotation generates a Purchase Order
        ↓
6. Invoice is generated from the Purchase Order
        ↓
7. Invoice is printed or emailed directly
        ↓
8. All activities tracked through logs & analytics
```

---

## 🎨 Mockup

View the original UI mockup here:
👉 [Excalidraw Mockup](https://app.excalidraw.com/l/65VNwvy7c4X/5ywnm0v3qhK)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- Built during a Hackathon challenge
- Problem Statement provided by the organizing team
- Powered by Flask & love for clean code ❤️
