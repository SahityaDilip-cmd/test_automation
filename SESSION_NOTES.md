# Session notes — QA automation learning path

Saved from Cursor cloud agent chat (2026-08-03).

Agent URL: https://cursor.com/agents/bc-befd59a7-6037-459e-bcf0-e95cb4185f1b  
PR (practice app): https://github.com/SahityaDilip-cmd/test_automation/pull/1

---

## Goal

Shift toward automation roles using a stack close to the organization:

**BDD + Playwright + Cursor + Python + Allure**  
Practice layers: **UI + API + DB**

## Decision made in this chat

- Do **not** auto-generate the full automation framework.
- Add a **practice application only** (option A) so automation can be built step by step by the learner.

## Practice app summary

- Local Flask app: `http://127.0.0.1:5000/`
- UI: login, dashboard, create/update/delete tasks
- API: `/api/health`, `/api/login`, `/api/tasks` CRUD
- DB: SQLite `practice.db`
- Selectors: `data-testid` attributes for Playwright

### Demo users

| Username | Password  |
|----------|-----------|
| admin    | admin123  |
| tester   | test123   |

### Run the app

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.app
```

## Agreed learning order

1. Manually explore the app (UI + API + DB)
2. Init automation project (venv, deps, folder layout)
3. First Playwright smoke test (no BDD yet)
4. UI login tests (valid + invalid)
5. UI create-task flow
6. Add BDD (pytest-bdd or Behave — confirm org preference)
7. Add Allure reporting
8. API tests
9. Combined UI + API + DB scenario
10. Push to Git after each small milestone

## Example target BDD scenario (later)

```gherkin
Feature: Task lifecycle
  Scenario: Create task via UI and verify via API and DB
    Given a logged-in user "admin"
    When the user creates a task titled "Learn Playwright"
    Then the task is visible on the dashboard
    And the API returns the task for that user
    And the task exists in the database
```

## Next step when continuing

Say: **“ready for step 1”**  
Then set up the automation folder and first Playwright smoke test (guided, not auto-generated as a full framework).
