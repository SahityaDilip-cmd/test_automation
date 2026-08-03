# QA Practice App (UI + API + DB)

A small local web app you can use to **learn automation** with the stack your organization uses:

**BDD + Playwright + Python + Allure** (plus API and database checks).

This repository currently contains **only the application under test**.  
You will build the automation project yourself (recommended for learning).

---

## What you get

| Layer | What exists |
|--------|-------------|
| **UI** | Login, dashboard, create/update/delete tasks |
| **API** | REST endpoints under `/api/*` |
| **DB** | SQLite file `practice.db` (created on first run) |

Stable selectors are available via `data-testid` attributes (good for Playwright).

---

## Quick start

```bash
# 1) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2) Install app dependency
pip install -r requirements.txt

# 3) Start the app
python -m app.app
```

Open: **http://127.0.0.1:5000/**

### Demo users

| Username | Password |
|----------|----------|
| `admin`  | `admin123` |
| `tester` | `test123`  |

---

## UI pages

| Page | URL |
|------|-----|
| Login | `/login` |
| Dashboard (task list) | `/dashboard` |
| Create task | `/tasks/new` |
| Logout | `/logout` |

---

## API reference

Base URL: `http://127.0.0.1:5000`

### Public

```http
GET  /api/health
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

`/api/login` returns an `api_key` you can reuse as the `X-API-Key` header.

### Authenticated (header required)

```http
X-API-Key: admin:admin123
```

| Method | Endpoint | Notes |
|--------|----------|--------|
| `GET` | `/api/tasks` | List my tasks (`?mine=false` for all) |
| `GET` | `/api/tasks/<id>` | Get one task |
| `POST` | `/api/tasks` | Create task |
| `PATCH` | `/api/tasks/<id>` | Update status |
| `DELETE` | `/api/tasks/<id>` | Delete task |
| `GET` | `/api/db/tasks/<id>` | DB-style lookup helper |

### Create task example

```bash
curl -X POST http://127.0.0.1:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin:admin123" \
  -d '{"title":"API created task","description":"via curl","status":"open"}'
```

Allowed statuses: `open`, `in_progress`, `done`.

---

## Database

- File: `practice.db` (project root, auto-created)
- Tables: `users`, `tasks`

Useful while learning DB assertions:

```bash
sqlite3 practice.db "SELECT id, title, status FROM tasks;"
```

Or from Python tests later:

```python
import sqlite3
conn = sqlite3.connect("practice.db")
row = conn.execute("SELECT * FROM tasks WHERE id = ?", (1,)).fetchone()
```

---

## Suggested automation learning path

Build this **yourself** in a separate folder (for example `automation/`) or a new repo.

1. **Manual explore** — login, create a task, call `/api/health`, inspect `practice.db`
2. **Playwright smoke** — open login page, assert heading
3. **UI login test** — valid + invalid credentials
4. **UI create task** — form submit + flash/table assert
5. **Add BDD** — move scenarios into `.feature` files (`pytest-bdd` or Behave)
6. **Add Allure** — attach screenshots/steps
7. **API tests** — login + create + get task
8. **UI + API + DB flow** — create via UI, verify via API and SQLite
9. **Push to Git** after each small milestone

### Example BDD scenario to aim for later

```gherkin
Feature: Task lifecycle
  Scenario: Create task via UI and verify via API and DB
    Given a logged-in user "admin"
    When the user creates a task titled "Learn Playwright"
    Then the task is visible on the dashboard
    And the API returns the task for that user
    And the task exists in the database
```

---

## Project layout

```text
app/
  app.py              # Flask UI + API
  db.py               # SQLite access
  templates/          # HTML pages
  static/styles.css
requirements.txt
README.md
practice.db           # created at runtime (gitignored)
```

---

## Notes for learners

- Prefer `data-testid` selectors in Playwright.
- Keep secrets/demo passwords only in local/test config.
- Reset data by deleting `practice.db` and restarting the app.
- Do not wait until the framework is “perfect” — automate one flow, then improve structure (Page Objects, fixtures, BDD).
