# Flask ERP – MVC Folder & File Structure

This document defines a **production‑ready, industry‑agnostic ERP folder structure** using **Flask (MVC)** with **HTML templates, CSS, and JavaScript**. It is suitable for **SaaS or on‑prem ERP systems** and scales from MVP to enterprise.

---

## 1. Architecture Overview

The system follows **MVC + Service Layer**:

* **Model (M)** → Database entities
* **View (V)** → Jinja2 templates + static assets
* **Controller (C)** → Flask routes (Blueprints)
* **Service Layer** → Business logic (ERP rules)

This separation keeps routes thin, logic reusable, and templates clean.

---

## 2. Root Project Structure

```
erp_system/
├── app.py
├── wsgi.py
├── config.py
├── requirements.txt
├── .env
├── README.md
│
├── app/
├── tests/
├── scripts/
└── migrations/
```

### Root File Purpose

| File             | Purpose                         |
| ---------------- | ------------------------------- |
| app.py           | Application entry (development) |
| wsgi.py          | Production server entry         |
| config.py        | Environment configurations      |
| requirements.txt | Python dependencies             |
| .env             | Secrets & environment vars      |

---

## 3. Application Core (`app/`)

```
app/
├── __init__.py
├── core/
├── models/
├── auth/
├── finance/
├── hr/
├── sales/
├── procurement/
├── inventory/
├── projects/
├── reports/
├── api/
├── templates/
├── static/
└── migrations/
```

---

## 4. Core System Layer (`app/core/`)

Shared logic used by all modules.

```
core/
├── __init__.py
├── extensions.py
├── security.py
├── decorators.py
├── middleware.py
├── constants.py
└── utils.py
```

| File          | Responsibility           |
| ------------- | ------------------------ |
| extensions.py | DB, Login, Migrate, CSRF |
| security.py   | RBAC, permissions        |
| decorators.py | Auth & role checks       |
| middleware.py | Request hooks            |
| utils.py      | Helpers                  |

---

## 5. Models Layer (`app/models/`)

Centralized shared models.

```
models/
├── __init__.py
├── base.py
├── user.py
├── role.py
├── permission.py
├── company.py
└── audit_log.py
```

* `base.py` → ID, timestamps, soft delete
* `audit_log.py` → compliance & tracking

---

## 6. ERP Module Structure (Generic)

Each ERP module follows the **same internal structure**.

```
<module>/
├── __init__.py
├── routes.py
├── services.py
├── models.py
└── templates/<module>/
```

### Example: Finance Module

```
finance/
├── __init__.py
├── routes.py
├── services.py
├── models.py
└── templates/finance/
    ├── dashboard.html
    ├── invoices.html
    ├── payments.html
    └── reports.html
```

| File        | Purpose                       |
| ----------- | ----------------------------- |
| routes.py   | Controllers (Flask Blueprint) |
| services.py | Business logic                |
| models.py   | Module‑specific tables        |
| templates/  | UI views                      |

---

## 7. Authentication Module (`app/auth/`)

```
auth/
├── __init__.py
├── routes.py
├── services.py
├── forms.py
└── templates/auth/
    ├── login.html
    ├── register.html
    └── reset_password.html
```

Handles:

* Login / Logout
* Password reset
* Session control

---

## 8. Templates Layer (`app/templates/`)

Global shared UI components.

```
templates/
├── base.html
├── layout.html
├── navbar.html
├── sidebar.html
├── footer.html
├── dashboard.html
└── errors/
    ├── 403.html
    ├── 404.html
    └── 500.html
```

### Template Rules

* `base.html` → HTML skeleton
* `layout.html` → App shell
* Module templates extend layout

---

## 9. Static Assets (`app/static/`)

```
static/
├── css/
│   ├── main.css
│   ├── theme.css
│   ├── components.css
│   └── modules/
│       ├── finance.css
│       ├── hr.css
│       └── sales.css
│
├── js/
│   ├── main.js
│   ├── utils.js
│   ├── ajax.js
│   ├── charts.js
│   └── modules/
│       ├── finance.js
│       ├── hr.js
│       └── sales.js
│
├── img/
└── fonts/
```

Frontend behavior:

* JS handles AJAX & UI logic
* CSS modular per ERP module

---

## 10. API Layer (`app/api/`)

Optional REST API for mobile / integrations.

```
api/
├── __init__.py
└── v1/
    ├── __init__.py
    ├── auth.py
    ├── finance.py
    └── common.py
```

---

## 11. Tests (`tests/`)

```
tests/
├── conftest.py
├── test_auth.py
├── test_finance.py
└── test_inventory.py
```

Used for:

* Unit tests
* Integration tests

---

## 12. Scripts (`scripts/`)

```
scripts/
├── seed_db.py
├── create_admin.py
└── migrate_data.py
```

Automation & maintenance tasks.

---

## 13. MVC Request Flow

```
Browser
 → JS / Form
 → routes.py (Controller)
 → services.py (Logic)
 → models.py (DB)
 → Template (View)
 → Response
```

---

## 14. Why This Structure Works for All Industries

* No industry‑locked assumptions
* Supports product + service businesses
* Easy to extend vertically
* SaaS‑ready
* Enterprise security friendly

---

## 15. Recommended Next Steps

* Add RBAC module
* Add multi‑tenant support
* Introduce workflow engine
* Convert services to async tasks
* Apply UI themes (dark / glass)

---

**Author:** ERP Architecture Blueprint
**Framework:** Flask (MVC)
**Scope:** Enterprise / SaaS ERP
RBAC folder + permission matrix
Multi-tenant SaaS structure

Workflow / approval engine structure

Database naming conventions

Deployment structure (Gunicorn, Nginx)