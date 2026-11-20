# ATH

Read [AGENTS.md](AGENTS.md) before writing or changing any code in this
repository. It is the house style for this project: the three-layer split
(`app.py` → `*_service.py` → `database.py`), how deletes remove child records
first inside one transaction, the wording of user-facing messages, the
Add/Manage page layout, and how to run the app and the tests through `.venv`.

Match the existing style rather than your own defaults, and do not restructure
code you were not asked to change.
