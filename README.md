# ATH

A Streamlit app over a MySQL database. Athletes build profiles, log workouts,
share achievements, join activities and earn Activity Points toward sponsor
rewards.

Coursework for CSC350 Databases.

## Setup

You need Python 3.11+ and MySQL 8.

**1. Create the database.** `sql/ath_schema_and_data.sql` creates the `ath`
database with all fifteen tables, the `athlete_portfolio` view and the
sample data. It drops and recreates the ATH tables, so only run it on a
server where you want a fresh copy:

```powershell
mysql -u root -p < sql\ath_schema_and_data.sql
```

(In MySQL Workbench: *File → Open SQL Script*, pick the file, then run it.)

**2. Install the Python packages** into a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**3. Add your database login.** Copy the secrets template and fill in your
own MySQL password:

```powershell
copy .streamlit\secrets.example.toml .streamlit\secrets.toml
```

`secrets.toml` is gitignored. Never put a host, user or password in source
code or in a commit.

## Running

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

The app opens at http://localhost:8501.

### Logging in

There are no passwords. Pick an athlete in the sidebar's **Logged in as**
dropdown to act as that user. Everything you add is saved under that
athlete, and the "Manage My …" sections only offer your own records, so
switching profiles changes what you can edit or delete. To create a new
user, open **New here? Create a profile** under the dropdown; the new athlete
is logged in straight away. You can edit or delete only your own profile.

### Pages

| Page | What you can do |
|---|---|
| Athletes | search and filter athletes; edit or delete your own profile (and sports); recruiter interest |
| Achievements | search by title, filter by date; add, edit and delete your achievements |
| Activities | search and filter by sport; organize activities; join one; organizers manage the roster and award points for attendance |
| Workouts | log, edit and delete your workouts |
| Points | your Activity Points history; add, edit and delete your points records |
| Sports | the sports list (shared, not owned by anyone) |
| Sponsors | the sponsor list (shared, not owned by anyone) |
| Posts | post as yourself; comment on any post; edit and delete your comments |
| Reward Redemptions | see which rewards your points qualify you for and request one |

## Tests

```powershell
.venv\Scripts\python.exe -m unittest tests.test_assigned_services
```

The tests patch the service layer and never touch a real database, so they
run without MySQL. They cover every service, render all nine pages, and
check that switching the logged-in athlete changes what can be managed.

## Layout

```
app.py                      entry point - imports main() and calls it
ui/ath.py                   the whole Streamlit interface, inside main()
services/*_service.py       validation, business rules, user-facing messages
services/delete_summary.py  turns delete counts into a sentence
services/ownership.py       check_owner(): users may only change their own records
db/database.py              every SQL statement in the project
sql/                        the create-and-populate script, plus one-off scripts
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
