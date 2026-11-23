# sql/

One-off scripts that change the shared database. Nothing here runs by itself
and nothing here is imported by the app — `db/database.py` holds every query
the app actually issues.

**Never run one of these without asking the rest of the team first.** They
alter the schema everyone shares.

| File | What it is |
|---|---|
| `ath_schema_and_data.sql` | **The script to submit and to set up a new machine.** Creates the `ath` database, all fifteen tables, the `athlete_portfolio` view and the sample data, exported on 2026-11-23 after the AUTO_INCREMENT fix. It drops and recreates the tables, so never run it against the shared database |
| `fix_auto_increment.sql` | Gives each single-column primary key an `AUTO_INCREMENT`, so an `INSERT` that does not name the key still works. **Already applied in full on 2026-11-23** |
| `restore_foreign_keys.sql` | Puts back the ten foreign keys the script above drops. Only needed if that script failed partway |
| `backup_before_auto_increment.sql` | `mysqldump` of the whole `ath` database, 2026-11-20 |
| `backup_2026-11-23_before_auto_increment.sql` | `mysqldump` taken immediately before the migration was run |

## State as of 2026-11-23

`fix_auto_increment.sql` has been applied in full. All thirty statements
succeeded — ten foreign keys dropped, ten primary keys altered, the same ten
foreign keys added back.

Verified afterwards:

- every table with a single-column primary key has `AUTO_INCREMENT`
  (`achievement`, `activity`, `activity_point`, `athlete`, `comment`, `post`,
  `recruiter`, `reward`, `reward_redemption`, `sponsor`, `sport`, `workout`)
- the foreign keys are byte-for-byte what they were before: 20 constrained
  columns, same names, same referenced tables, same `NO ACTION` rules
- all 15 tables have exactly the row counts they had before
- every Add form in the app inserts successfully, checked through the real
  service functions with `commit()` swapped for `rollback()` so no probe row
  survived

The junction tables (`activity_participant`, `athlete_sport`,
`recruiter_athlete`) have no `AUTO_INCREMENT` and should not get one — their
keys are composite and both halves come from the dropdowns, so there is
nothing for MySQL to generate.

Re-running `fix_auto_increment.sql` is harmless if it is ever needed again: a
column that already has `AUTO_INCREMENT` is left alone.

## Running one

```powershell
mysql -h <host> -u <user> -p ath < sql/fix_auto_increment.sql
```

Take a fresh dump first:

```powershell
mysqldump -h <host> -u <user> -p --databases ath --routines --triggers --events --single-transaction > sql/backup_YYYY-MM-DD.sql
```
