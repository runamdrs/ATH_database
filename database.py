import mysql.connector
import streamlit as st


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
        database=st.secrets["db_name"]
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


def get_all_sports():
    return run_select(
        """
        SELECT SportID, Name
        FROM sport
        ORDER BY Name
        """
    )


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
