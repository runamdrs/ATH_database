# ATH

A Streamlit app over a MySQL database. Athletes build profiles, log workouts,
share achievements, join activities and earn Activity Points toward sponsor
rewards.

Coursework for CSC350 Databases.

## Setup

You need Python and a MySQL server with the `ath` database loaded.

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then copy the secrets template and fill in your own MySQL password:

```powershell
copy .streamlit\secrets.example.toml .streamlit\secrets.toml
```

`secrets.toml` is gitignored. Never put a host, user or password in source
code or in a commit.

## Running

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

## Tests

```powershell
.venv\Scripts\python.exe -m unittest tests.test_assigned_services
```

The tests patch the service layer and never touch a real database, so they
run without MySQL. They cover every service and render all seven pages.

## Layout

```
app.py                      entry point - imports main() and calls it
ui/ath.py                   the whole Streamlit interface, inside main()
services/*_service.py       validation, business rules, user-facing messages
services/delete_summary.py  turns delete counts into a sentence
db/database.py              every SQL statement in the project
sql/                        one-off scripts that change the shared database
tests/                      the test suite
```

Three layers, strictly: the UI never writes SQL, the services never open a
connection, and `db/database.py` is the only file that talks to MySQL. Imports
name their package — `from db.database import ...`, `from services.x import ...`.

## Contributing

Read [AGENTS.md](AGENTS.md) before changing any code. It is the house style:
the layering above, how deletes remove child records first inside one
transaction, the exact wording of user-facing messages, and the Add/Manage
layout every page follows.
