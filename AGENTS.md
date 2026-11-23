# Working on ATH — conventions for AI assistants and teammates

This file is the house style for this repository. If you are an AI assistant
(Claude Code, Cursor, Copilot, Codex, …) working in this project, read this
before writing or changing any code, and follow it even when you would
normally do things differently.

The project already has one consistent style. **Match it.** Do not introduce a
second way of doing the same thing, and do not "modernise", reformat or
restructure code that you were not asked to change.

If something here conflicts with what the user asks for, the user wins — but
say that you are departing from this file and why.

---

## 0. Making your assistant read this

The rules live in **this file**. Every other file listed below is a three-line
pointer to it, so that whichever tool a teammate uses picks the rules up by
itself. Keep it that way: add rules here only, so the pointers can never
disagree with the rules.

| Tool | File it reads automatically |
|---|---|
| Codex CLI, Zed, Amp, most newer agents | `AGENTS.md` (this file) |
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursor/rules/ath-house-style.mdc` (older versions: `.cursorrules`) |
| GitHub Copilot in VS Code / Visual Studio | `.github/copilot-instructions.md` |
| Gemini CLI / Gemini Code Assist | `GEMINI.md` |
| Windsurf | `.windsurfrules` |
| Cline / Roo Code | `.clinerules` |
| JetBrains Junie | `.junie/guidelines.md` |
| ChatGPT, Claude, Gemini in a browser | nothing automatic — paste this whole file into the chat before asking for code |

If your tool is not in the table, look in its documentation for "project
rules", "custom instructions" or "context files", point it at `AGENTS.md`, and
add the pointer file to the repo so the next person does not have to. These
filenames change as the tools are updated, so check your own tool's docs
rather than trusting this table.

Whatever you use: after it has read this, ask it to summarise the delete rule
in §3 and the page layout in §7 back to you. If it cannot, it did not load the
file, and you should paste it in manually.

---

## 1. What the app is

ATH is a Streamlit app over a MySQL database. Athletes build profiles, log
workouts, share achievements, join activities and earn Activity Points toward
sponsor rewards. It is coursework for a databases class, so the code is meant
to be **readable and explainable**, not clever.

Three layers, strictly, one package each:

| File | Job | Rule |
|---|---|---|
| `app.py` | entry point — two lines, imports `main` and calls it | No UI, no logic, no SQL |
| `ui/ath.py` | Streamlit UI only | Never imports `mysql.connector`, never writes SQL |
| `services/*_service.py` | validation, business rules, user-facing messages | Never opens a connection itself |
| `db/database.py` | all SQL | The **only** file that talks to MySQL |
| `services/delete_summary.py` | turns delete counts into a sentence | No SQL, no Streamlit |

If you need new data, add a function to `db/database.py`, expose it through a
service, and call that service from `ui/ath.py`. Never shortcut a layer.

Imports always name the package: `from db.database import ...` inside a
service, `from services.athlete_service import ...` inside the UI. Each of
`ui/`, `db/` and `services/` holds an empty `__init__.py`, which is what makes
the folder a package those imports can reach.

The whole interface lives inside `main()` in `ui/ath.py`, and `app.py` in the
project root calls it:

```python
from ui.ath import main

main()
```

Streamlit still runs `app.py`, so the interface file can move or be renamed
without changing how the app is launched. `show_result()` stays at module
level, above `main()` — it is a helper, not part of the interface flow.

---

## 2. db/database.py

- Every query is parameterised with `%s` and a tuple. **Never** build SQL with
  f-strings, `+` or `.format()` — that is a SQL injection hole, and it is
  explicitly marked in the file's comments.
- `run_select(query, params)` for reads, `run_write(query, params)` for a
  single write, `run_write_many(statements)` for several writes that must
  succeed or fail together.
- `get_all_<thing>()` returns a list of dicts for the tables.
  `get_<thing>_by_id(id)` returns one dict or `None`, and is used to pre-fill
  update forms.
- JOIN in SQL so the UI shows names, not raw IDs:

  ```python
  SELECT a.ActivityID, a.AthleteID, s.Name AS Sport, a.Type, ...
  FROM activity a
  JOIN sport s ON s.SportID = a.SportID
  ```

- Every UPDATE and DELETE has a `WHERE` on the primary key.
- The connection sets the `FOUND_ROWS` client flag, so `rowcount` after an
  UPDATE counts the rows the `WHERE` matched. That is how the services tell
  "nothing changed" from "no such record" — `rowcount == 0` means the record
  does not exist.

---

## 3. Deleting: child records first, in one transaction

MySQL refuses to delete a row while another table still references it
(error 1451). We do **not** work around that with `ON DELETE CASCADE` in the
schema and we do **not** just show the error. Each delete removes the records
that depend on the row first and the row itself last, inside a single
transaction:

```python
def delete_activity(activity_id):
    """Delete an activity along with its points and participants."""
    return run_write_many([
        ("activity_point", "DELETE FROM activity_point WHERE ActivityID = %s",
         (activity_id,)),
        ("activity_participant", "DELETE FROM activity_participant WHERE ActivityID = %s",
         (activity_id,)),
        ("activity", "DELETE FROM activity WHERE ActivityID = %s", (activity_id,)),
    ])
```

Rules:

- Order matters: the deepest dependant goes first, the record itself last.
- `activity_point` references athletes, activities **and** workouts, so it is
  always deleted before any of those three.
- Remember other people's rows: deleting an athlete also removes everyone
  else's `activity_participant` rows for that athlete's activities, and
  everyone else's `comment` rows on that athlete's posts.
- Every delete returns `{table: rows deleted}`. The record's own entry is `0`
  when no such record existed.
- If you add a table with a foreign key, add it to the delete chain of its
  parent **and** say so in the parent's docstring.

The current foreign keys (checked against `information_schema`, not guessed):

```
athlete   <- achievement, activity, activity_participant, activity_point,
             athlete_sport, comment, post, recruiter_athlete,
             reward_redemption, workout
activity  <- activity_participant, activity_point
workout   <- activity_point
post      <- comment
sport     <- achievement, activity, athlete_sport
sponsor   <- reward            reward <- reward_redemption
recruiter <- recruiter_athlete
achievement, athlete_portfolio (a VIEW) — nothing depends on them
```

---

## 4. Service modules

Every `services/*_service.py` has the same shape, in this order:

```python
import mysql.connector

from database import (
    get_all_sports, get_sport_by_id,
    insert_sport, update_sport, delete_sport,
)
from delete_summary import describe_related


def list_sports():            # or search_sports(...) where the page filters
    """One line saying what comes back."""


def get_sport_options():
    """Map SportID -> name for a dropdown, so users pick a sport
    instead of typing an ID."""


def get_sport_details(sport_id):
    """Return one sport's current values (to pre-fill the update form)."""


def check_sport_input(name, sport_type):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (name, sport_type)."""


def add_sport(name, sport_type):
    """Validate the input, then insert it. Returns (success, message)."""


def edit_sport(sport_id, name, sport_type):
    """Validate the input, then update the sport. Returns (success, message)."""


def remove_sport(sport_id):
    """Delete the sport together with …, in one transaction.
    Returns (success, message)."""
```

Non-negotiable parts:

- **One validator per entity**, `check_<thing>_input(...)`, returning
  `(error, values)` and used by *both* add and edit. Never copy validation
  between the two functions.
- Validation also cleans: `.strip()` the text, and turn an empty optional
  field into `None` so it is stored as SQL `NULL`:
  `location = (location or "").strip() or None`.
- Every public function returns `(success: bool, message: str)` for writes,
  or plain data for reads. `ui/ath.py` never sees an exception.

---

## 5. Error handling

Always the same two branches, in this order, with the exception named `e`
(the name `error` is taken by the validation message):

```python
    try:
        insert_sport(name, sport_type)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # sport.Name is UNIQUE in the schema
            return False, "A sport with that name already exists."
        return False, f"Could not add sport: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add sport: {e.msg}"
```

| errno | Means | Typical message |
|---|---|---|
| 1062 | duplicate value in a UNIQUE column | "That username or email is already taken." |
| 1452 | foreign key violation on insert/update | "That athlete or sport no longer exists." |
| 1451 | something still references this row | "This sport is in use and cannot be deleted." |

Only write an `IntegrityError` branch when there is a specific error you can
explain. `sponsor` has no UNIQUE column and no foreign key of its own, so
`sponsor_service` has only the general `except mysql.connector.Error` — with a
comment saying why.

Where the database cannot enforce a rule, enforce it in the service and say so
in a comment. `sponsor.Company` has no UNIQUE index, which is why
`is_duplicate_company()` exists while athletes and sports rely on errno 1062.

---

## 6. Messages the user sees

Keep the wording and the order of words identical across services:

| Situation | Message |
|---|---|
| Added | `f'Added sport "{name}".'` |
| Updated | `f'Updated sport "{name}".'` |
| Deleted | `"Deleted sport." + describe_related(deleted, "sport")` |
| Record gone | `"No matching sport found."` |
| Validation | A full sentence naming the field: `"Sport type is required."` |

Never `"Sport deleted."`, never `"That sport no longer exists."` — the verb
comes first, and the "missing record" wording is the one in the table.

`describe_related()` appends what else was removed, e.g.
*"Deleted athlete. Also deleted 10 points records, 6 comments and 3 activities."*
When you add a table to a delete chain, add its singular/plural label to
`RECORD_NAMES` in `services/delete_summary.py` or it will show as a raw table name.

---

## 7. ui/ath.py — the page layout

Every CRUD page has exactly two sections: **Add**, then **Manage**. Copy the
Athletes page and adapt it; do not invent a different arrangement. Every page
sits one level in, inside `main()`; the example below is written flush left so
it stays readable.

```python
elif section == "Sports":
    st.header("Sports")

    st.dataframe(list_sports())

    st.subheader("Add a Sport")
    with st.form("add_sport"):
        name = st.text_input("Sport name")
        sport_type = st.text_input("Type")
        submitted = st.form_submit_button("Add Sport")

    if submitted:                      # handled immediately after its form
        show_result(*add_sport(name, sport_type))

    st.subheader("Manage Sports")
    # The radio sits outside the form so the form re-renders when it changes.
    mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="sport_mode")
    sport_options = get_sport_options()

    if not sport_options:
        st.info("No sports available.")
    else:
        sport_id = st.selectbox(
            "Sport",
            options=list(sport_options),
            format_func=lambda sport_id: sport_options[sport_id],
            key="manage_sport_id",
        )
        current = get_sport_details(sport_id)

        with st.form("manage_sport"):
            if mode == "Update":
                # The ID in each key gives every sport fresh, pre-filled widgets.
                new_name = st.text_input("Sport name", value=current["Name"],
                                         key=f"sport_name_{sport_id}")
                ...
            else:
                st.warning("Deleting this sport also deletes …")
                confirm = st.checkbox("Confirm deletion")
            submitted = st.form_submit_button(mode)

        if submitted:
            if mode == "Update":
                show_result(*edit_sport(sport_id, new_name, new_sport_type))
            elif not confirm:
                st.warning("Please confirm deletion.")
            else:
                show_result(*remove_sport(sport_id))
```

Why each piece is the way it is:

- **`st.form`** groups the inputs so changing one widget does not submit.
- **The radio and the picker live outside the form.** Widgets inside a form do
  not rerun the page, so the fields could not be pre-filled with the chosen
  record's values.
- **Widget keys end in the record ID** (`key=f"sport_name_{sport_id}"`), which
  gives every record its own freshly pre-filled widgets.
- **Dropdowns show names and keep IDs**: `options=list(the_options)` plus
  `format_func=lambda id: the_options[id]`. Users never type an ID.
- **Delete mode always shows** an `st.warning` naming everything that will be
  removed with the record, plus a `st.checkbox("Confirm deletion")`. If the box
  is unticked, answer `st.warning("Please confirm deletion.")` and do nothing.
- **`show_result(success, message)`** handles every outcome: it stores the
  message and reruns on success (so the table above refreshes) and shows
  `st.error` on failure. Do not call `st.success` directly before a rerun.

---

## 8. Comments and docstrings

The code is read by a marker and by teammates who did not write it, so:

- Every public function gets a docstring that says what it returns.
- Comment the **why**, not the what: why the radio is outside the form, why
  `FOUND_ROWS` is set, why a table is deleted before another one.
- Keep lines under about 88 characters, 4-space indent, no tabs.
- Plain names: `athlete_id`, `sport_options`, `current`. No one-letter names
  except `e` for a caught exception.

---

## 9. Tests

`tests/test_assigned_services.py` covers the services and renders every page.
Run it before you say you are done:

```
.venv\Scripts\python.exe -m unittest tests.test_assigned_services
```

Conventions:

- Patch at the **service** level (`patch("services.sport_service.get_all_sports", …)`),
  not inside `db/database.py`, so no test needs a live database. That includes
  the single-record lookups (`services.sport_service.get_sport_by_id`).
- To test transactions, use a fake connection that records the statements it
  was given and whether `commit()` or `rollback()` was called — see
  `RecordingConnection` in the test file.
- If you must try something against the real database, wrap it so that
  `commit()` calls `rollback()` instead, and check the row counts afterwards.
  Never leave test data in the shared database.

---

## 10. Environment

- The virtual environment is `.venv` in the project root. Always run Python
  through it, never a bare `python`:

  ```
  .venv\Scripts\python.exe -m streamlit run app.py
  .venv\Scripts\python.exe -m unittest tests.test_assigned_services
  ```

- Database credentials live in `.streamlit/secrets.toml`, which is gitignored.
  `.streamlit/secrets.example.toml` shows the keys. **Never** put a host, user or password
  in source code, in a commit, or in a message to anyone.
- Do not add dependencies. If you genuinely need one, say so first and update
  `requirements.txt` in the same change.

---

## 11. Known issues — do not "fix" silently

- **AUTO_INCREMENT: fixed on 2026-11-23, do not undo.** Every table with a
  single-column primary key now has it, so every Add form works. Getting
  there meant dropping ten foreign keys, altering the columns and adding the
  constraints back — `sql/fix_auto_increment.sql`, which has now been run in
  full. The three junction tables (`activity_participant`, `athlete_sport`,
  `recruiter_athlete`) deliberately have none: their keys are composite and
  both halves come from the dropdowns.

  If you create a table, give its primary key `AUTO_INCREMENT` in the
  `CREATE TABLE`, or its first `INSERT` will fail with
  `Field '<PK>' doesn't have a default value`.
- `athlete_portfolio` is a **VIEW**, not a table. Never insert into or delete
  from it.
- Do not run schema changes, `DROP`, `TRUNCATE` or bulk updates against the
  shared database without asking first.
- **No hand-made indexes, on purpose.** Primary keys, UNIQUE columns and
  foreign keys already carry one, and the largest table holds 134 rows, so an
  extra index would cost storage and slow down every write without speeding
  any query up. Do not add one — or the `EXPLAIN` plumbing to justify one —
  unless the data grows enough to make it worth measuring.

---

## 12. Before you call the work done

1. Does it follow the layering in §1 (no SQL outside `db/database.py`)?
2. Is every query parameterised?
3. If you added a foreign key, is it in the parent's delete chain and in
   `RECORD_NAMES`?
4. Do add and edit share one `check_*_input()`?
5. Are the messages worded exactly as in §6?
6. Does the new page section look like §7, down to the confirmation checkbox?
7. Does every import name its package (`db.database`, `services.…`, `ui.…`)?
8. Do all the tests pass?
9. Did you leave the shared database exactly as you found it?
