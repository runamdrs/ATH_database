import mysql.connector
import streamlit as st
from mysql.connector.constants import ClientFlag


# ---------------------------------------------------------------
# Data layer: the only file that talks to MySQL.
# Credentials come from .streamlit/secrets.toml (gitignored),
# never from this source file.
# ---------------------------------------------------------------

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["db_host"],
        port=st.secrets.get("db_port", 3306),  # 3306 is MySQL's default
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        database=st.secrets["db_name"],
        # By default an UPDATE that leaves the values unchanged reports
        # 0 rows. FOUND_ROWS makes rowcount count the rows the WHERE
        # matched instead, so "0" really means "no such record".
        client_flags=[ClientFlag.FOUND_ROWS]
    )


def run_select(query, params=None):
    """Run a SELECT and return the rows as a list of dicts,
    the same shape the sample data used in Part 1."""
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        connection.close()


def run_write(query, params=None):
    """Run an INSERT/UPDATE/DELETE, commit it, and return how many
    rows were affected. Without commit() MySQL discards the change."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount
    finally:
        connection.close()


def get_all_athletes():
    return run_select(
        """
        SELECT AthleteID, Name, Username, Email, Location, SkillLevel
        FROM athlete
        ORDER BY AthleteID
        """
    )


def get_all_achievements():
    return run_select(
        """
        SELECT AchievementID, AthleteID, Title, Description, DateEarned
        FROM achievement
        ORDER BY AchievementID
        """
    )


def get_all_activities():
    # JOIN sport so the table shows the sport's name, not just its ID.
    rows = run_select(
        """
        SELECT a.ActivityID, a.AthleteID, s.Name AS Sport, a.Type,
               a.Date, a.Time, a.Duration, a.Location, a.MaxParticipants
        FROM activity a
        JOIN sport s ON s.SportID = a.SportID
        ORDER BY a.ActivityID
        """
    )
    # MySQL Connector returns TIME columns as a timedelta, which the
    # table would show as "0 days 09:00:00". Turn it into "09:00".
    for row in rows:
        minutes = int(row["Time"].total_seconds()) // 60
        row["Time"] = f"{minutes // 60:02d}:{minutes % 60:02d}"
    return rows


def get_all_sports():
    return run_select(
        """
        SELECT SportID, Name
        FROM sport
        ORDER BY Name
        """
    )


# ---------------------------------------------------------------
# Single-record SELECTs: used to pre-fill the update forms with
# the record's current values (raw IDs, not display names).
# ---------------------------------------------------------------

def get_athlete_by_id(athlete_id):
    rows = run_select(
        """
        SELECT AthleteID, Name, Username, Email, Location, SkillLevel
        FROM athlete
        WHERE AthleteID = %s
        """,
        (athlete_id,)
    )
    return rows[0] if rows else None


def get_achievement_by_id(achievement_id):
    rows = run_select(
        """
        SELECT AchievementID, AthleteID, SportID, Title, Description, DateEarned
        FROM achievement
        WHERE AchievementID = %s
        """,
        (achievement_id,)
    )
    return rows[0] if rows else None


def get_activity_by_id(activity_id):
    rows = run_select(
        """
        SELECT ActivityID, AthleteID, SportID, Type, Date, Time, Duration,
               Location, MaxParticipants
        FROM activity
        WHERE ActivityID = %s
        """,
        (activity_id,)
    )
    return rows[0] if rows else None


# ---------------------------------------------------------------
# INSERTs: values are passed separately as a tuple and MySQL
# Connector fills in the %s placeholders safely. Never build SQL
# with f-strings or + (that opens the door to SQL injection).
# ---------------------------------------------------------------

def insert_athlete(name, username, email, location, skill_level):
    return run_write(
        """
        INSERT INTO athlete (Name, Username, Email, Location, SkillLevel)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, username, email, location, skill_level)
    )


def insert_achievement(athlete_id, sport_id, title, description, date_earned):
    return run_write(
        """
        INSERT INTO achievement (AthleteID, SportID, Title, Description, DateEarned)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (athlete_id, sport_id, title, description, date_earned)
    )


def insert_activity(athlete_id, sport_id, activity_type, date, time, duration,
                    location, max_participants):
    return run_write(
        """
        INSERT INTO activity (AthleteID, SportID, Type, Date, Time, Duration,
                              Location, MaxParticipants)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (athlete_id, sport_id, activity_type, date, time, duration,
         location, max_participants)
    )


# ---------------------------------------------------------------
# UPDATEs: the WHERE on the primary key makes sure only one row
# changes. run_write() returns the rowcount, so 0 means no record
# with that ID exists.
# ---------------------------------------------------------------

def update_athlete(athlete_id, name, username, email, location, skill_level):
    return run_write(
        """
        UPDATE athlete
        SET Name = %s, Username = %s, Email = %s, Location = %s, SkillLevel = %s
        WHERE AthleteID = %s
        """,
        (name, username, email, location, skill_level, athlete_id)
    )


def update_achievement(achievement_id, athlete_id, sport_id, title, description,
                       date_earned):
    return run_write(
        """
        UPDATE achievement
        SET AthleteID = %s, SportID = %s, Title = %s, Description = %s,
            DateEarned = %s
        WHERE AchievementID = %s
        """,
        (athlete_id, sport_id, title, description, date_earned, achievement_id)
    )


def update_activity(activity_id, athlete_id, sport_id, activity_type, date, time,
                    duration, location, max_participants):
    return run_write(
        """
        UPDATE activity
        SET AthleteID = %s, SportID = %s, Type = %s, Date = %s, Time = %s,
            Duration = %s, Location = %s, MaxParticipants = %s
        WHERE ActivityID = %s
        """,
        (athlete_id, sport_id, activity_type, date, time, duration,
         location, max_participants, activity_id)
    )


# ---------------------------------------------------------------
# DELETEs: always with a WHERE on the primary key. A DELETE
# without WHERE would empty the whole table.
# ---------------------------------------------------------------

def delete_athlete(athlete_id):
    return run_write(
        "DELETE FROM athlete WHERE AthleteID = %s",
        (athlete_id,)
    )


def delete_achievement(achievement_id):
    return run_write(
        "DELETE FROM achievement WHERE AchievementID = %s",
        (achievement_id,)
    )


def delete_activity(activity_id):
    return run_write(
        "DELETE FROM activity WHERE ActivityID = %s",
        (activity_id,)
    )
