# ATH - house style

Read `AGENTS.md` in the repository root before writing or changing any code in
this project, and follow it instead of your own defaults.

It covers the three-layer split (`app.py` -> `*_service.py` -> `database.py`,
which is the only file allowed to contain SQL), how deletes remove child
records first inside one transaction, the exact wording of user-facing
messages, the Add/Manage page layout every Streamlit page uses, how to run the
tests, and the fact that Python must be run through `.venv`.

Match the existing style rather than your own, and do not restructure code you
were not asked to change.
