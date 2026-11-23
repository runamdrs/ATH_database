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
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        connection.close()


def run_write(query, params=None):
    """Run an INSERT/UPDATE/DELETE, commit it, and return how many
    rows were affected. Without commit() MySQL discards the change."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()


def run_write_many(statements):
    """Run several writes as ONE transaction and return how many rows
    each of them affected, as {label: rowcount}.

    `statements` is a list of (label, query, params). They all share a
    single connection, so the one commit() at the end saves them
    together, and if any statement fails, rollback() undoes the ones
    before it: the database is left exactly as it was. This is what
    makes a child-first delete safe (see the DELETEs below)."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        affected = {}
        try:
            for label, query, params in statements:
                cursor.execute(query, params or ())
                affected[label] = cursor.rowcount
            connection.commit()
            return affected
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
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
        SELECT SportID, Name, Type
        FROM sport
        ORDER BY Name
        """
    )


def get_all_workouts():
    return run_select(
        """
        SELECT w.WorkoutID, w.AthleteID, a.Name AS Athlete, w.ScheduledDate,
               w.WorkoutType, w.Duration, w.CompletionStatus, w.TrainingNotes
        FROM workout w
        JOIN athlete a ON a.AthleteID = w.AthleteID
        ORDER BY w.ScheduledDate DESC, w.WorkoutID DESC
        """
    )


def get_all_sponsors():
    return run_select(
        """
        SELECT SponsorID, Company, SponsorType, ContactInformation
        FROM sponsor
        ORDER BY Company, SponsorID
        """
    )


def get_rewards_for_athlete(athlete_id):
    return run_select(
        """
        SELECT r.RewardID, r.Description, r.PointsRequired, r.Availability,
               r.ExpirationDate, s.Company AS Sponsor,
               COALESCE(
                   (SELECT SUM(ap.PointsEarned)
                    FROM activity_point ap
                    WHERE ap.AthleteID = %s),
                   0
               ) AS AthletePoints,
               CASE
                   WHEN r.PointsRequired <= COALESCE(
                       (SELECT SUM(ap.PointsEarned)
                        FROM activity_point ap
                        WHERE ap.AthleteID = %s),
                       0
                   )
                    AND r.Availability > 0
                    AND r.ExpirationDate >= CURDATE()
                   THEN 1
                   ELSE 0
               END AS IsEligible
        FROM reward r
        JOIN sponsor s ON s.SponsorID = r.SponsorID
        ORDER BY r.PointsRequired, r.Description
        """,
        (athlete_id, athlete_id),
    )


def get_all_redemptions():
    return run_select(
        """
        SELECT rr.RedemptionID, rr.AthleteID, a.Name AS Athlete,
               rr.RewardID, r.Description AS Reward, s.Company AS Sponsor,
               rr.RedemptionDate, rr.Status
        FROM reward_redemption rr
        JOIN athlete a ON a.AthleteID = rr.AthleteID
        JOIN reward r ON r.RewardID = rr.RewardID
        JOIN sponsor s ON s.SponsorID = r.SponsorID
        ORDER BY rr.RedemptionDate DESC, rr.RedemptionID DESC
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


def get_workout_by_id(workout_id):
    rows = run_select(
        """
        SELECT WorkoutID, AthleteID, ScheduledDate, WorkoutType, Duration,
               CompletionStatus, TrainingNotes
        FROM workout
        WHERE WorkoutID = %s
        """,
        (workout_id,)
    )
    return rows[0] if rows else None


def get_sport_by_id(sport_id):
    rows = run_select(
        """
        SELECT SportID, Name, Type
        FROM sport
        WHERE SportID = %s
        """,
        (sport_id,)
    )
    return rows[0] if rows else None


def get_sponsor_by_id(sponsor_id):
    rows = run_select(
        """
        SELECT SponsorID, Company, SponsorType, ContactInformation
        FROM sponsor
        WHERE SponsorID = %s
        """,
        (sponsor_id,)
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
#
# MySQL refuses to delete a row while another table still references
# it (error 1451) - that is referential integrity stopping us from
# leaving orphan records behind. So each delete below removes the
# records that depend on the row first and the row itself last, and
# run_write_many() wraps the whole chain in a single transaction:
# either all of it is committed or none of it is.
#
# Every delete returns {table: rows deleted}, so the caller can tell
# the user exactly what went with the record. The parent's own entry
# is 0 when no record with that ID exists.
# ---------------------------------------------------------------

def delete_athlete(athlete_id):
    """Delete an athlete and everything that references them."""
    return run_write_many([
        # Deepest first: activity_point references the athlete, their
        # activities and their workouts, so it has to go before all three.
        ("activity_point", """
            DELETE FROM activity_point
            WHERE AthleteID = %s
               OR ActivityID IN (SELECT ActivityID FROM activity WHERE AthleteID = %s)
               OR WorkoutID IN (SELECT WorkoutID FROM workout WHERE AthleteID = %s)
         """, (athlete_id, athlete_id, athlete_id)),
        # Other athletes may have joined this athlete's activities, so
        # those rows have to go too, not just this athlete's own.
        ("activity_participant", """
            DELETE FROM activity_participant
            WHERE AthleteID = %s
               OR ActivityID IN (SELECT ActivityID FROM activity WHERE AthleteID = %s)
         """, (athlete_id, athlete_id)),
        # Same idea: comments by this athlete, plus everyone's comments
        # on this athlete's posts.
        ("comment", """
            DELETE FROM comment
            WHERE AthleteID = %s
               OR PostID IN (SELECT PostID FROM post WHERE AthleteID = %s)
         """, (athlete_id, athlete_id)),
        ("post", "DELETE FROM post WHERE AthleteID = %s", (athlete_id,)),
        ("activity", "DELETE FROM activity WHERE AthleteID = %s", (athlete_id,)),
        ("workout", "DELETE FROM workout WHERE AthleteID = %s", (athlete_id,)),
        ("achievement", "DELETE FROM achievement WHERE AthleteID = %s", (athlete_id,)),
        ("athlete_sport", "DELETE FROM athlete_sport WHERE AthleteID = %s", (athlete_id,)),
        ("recruiter_athlete", "DELETE FROM recruiter_athlete WHERE AthleteID = %s",
         (athlete_id,)),
        ("reward_redemption", "DELETE FROM reward_redemption WHERE AthleteID = %s",
         (athlete_id,)),
        # And only now the athlete themselves.
        ("athlete", "DELETE FROM athlete WHERE AthleteID = %s", (athlete_id,)),
    ])


def delete_achievement(achievement_id):
    """Delete an achievement. No table references achievement, so this
    is a single statement - run_write_many() is used anyway to keep
    every delete returning the same {table: rows deleted} shape."""
    return run_write_many([
        ("achievement", "DELETE FROM achievement WHERE AchievementID = %s",
         (achievement_id,)),
    ])


def delete_activity(activity_id):
    """Delete an activity along with its points and participants."""
    return run_write_many([
        ("activity_point", "DELETE FROM activity_point WHERE ActivityID = %s",
         (activity_id,)),
        ("activity_participant", "DELETE FROM activity_participant WHERE ActivityID = %s",
         (activity_id,)),
        ("activity", "DELETE FROM activity WHERE ActivityID = %s", (activity_id,)),
    ])


def insert_workout(athlete_id, scheduled_date, workout_type, duration,
                   completion_status, training_notes):
    return run_write(
        """
        INSERT INTO workout
            (AthleteID, ScheduledDate, WorkoutType, Duration,
             CompletionStatus, TrainingNotes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (athlete_id, scheduled_date, workout_type, duration,
         completion_status, training_notes),
    )


def update_workout(workout_id, athlete_id, scheduled_date, workout_type,
                   duration, completion_status, training_notes):
    return run_write(
        """
        UPDATE workout
        SET AthleteID = %s, ScheduledDate = %s, WorkoutType = %s,
            Duration = %s, CompletionStatus = %s, TrainingNotes = %s
        WHERE WorkoutID = %s
        """,
        (athlete_id, scheduled_date, workout_type, duration,
         completion_status, training_notes, workout_id),
    )


def delete_workout(workout_id):
    """Delete a workout along with the points earned for it."""
    return run_write_many([
        ("activity_point", "DELETE FROM activity_point WHERE WorkoutID = %s",
         (workout_id,)),
        ("workout", "DELETE FROM workout WHERE WorkoutID = %s", (workout_id,)),
    ])


def insert_sport(name, sport_type):
    return run_write(
        "INSERT INTO sport (Name, Type) VALUES (%s, %s)",
        (name, sport_type),
    )


def update_sport(sport_id, name, sport_type):
    return run_write(
        "UPDATE sport SET Name = %s, Type = %s WHERE SportID = %s",
        (name, sport_type, sport_id),
    )


def delete_sport(sport_id):
    """Delete a sport along with its activities (and their points and
    participants), its achievements and the athletes' links to it."""
    return run_write_many([
        ("activity_point", """
            DELETE FROM activity_point
            WHERE ActivityID IN (SELECT ActivityID FROM activity WHERE SportID = %s)
         """, (sport_id,)),
        ("activity_participant", """
            DELETE FROM activity_participant
            WHERE ActivityID IN (SELECT ActivityID FROM activity WHERE SportID = %s)
         """, (sport_id,)),
        ("activity", "DELETE FROM activity WHERE SportID = %s", (sport_id,)),
        ("achievement", "DELETE FROM achievement WHERE SportID = %s", (sport_id,)),
        ("athlete_sport", "DELETE FROM athlete_sport WHERE SportID = %s", (sport_id,)),
        ("sport", "DELETE FROM sport WHERE SportID = %s", (sport_id,)),
    ])


def insert_sponsor(company, sponsor_type, contact_information):
    return run_write(
        """
        INSERT INTO sponsor (Company, SponsorType, ContactInformation)
        VALUES (%s, %s, %s)
        """,
        (company, sponsor_type, contact_information),
    )


def update_sponsor(sponsor_id, company, sponsor_type, contact_information):
    return run_write(
        """
        UPDATE sponsor
        SET Company = %s, SponsorType = %s, ContactInformation = %s
        WHERE SponsorID = %s
        """,
        (company, sponsor_type, contact_information, sponsor_id),
    )


def delete_sponsor(sponsor_id):
    """Delete a sponsor along with its rewards and the redemptions of
    those rewards."""
    return run_write_many([
        ("reward_redemption", """
            DELETE FROM reward_redemption
            WHERE RewardID IN (SELECT RewardID FROM reward WHERE SponsorID = %s)
         """, (sponsor_id,)),
        ("reward", "DELETE FROM reward WHERE SponsorID = %s", (sponsor_id,)),
        ("sponsor", "DELETE FROM sponsor WHERE SponsorID = %s", (sponsor_id,)),
    ])


def insert_eligible_redemption(athlete_id, reward_id):
    return run_write(
        """
        INSERT INTO reward_redemption
            (AthleteID, RewardID, RedemptionDate, Status)
        SELECT %s, r.RewardID, CURDATE(), 'Pending'
        FROM reward r
        WHERE r.RewardID = %s
          AND r.Availability > 0
          AND r.ExpirationDate >= CURDATE()
          AND r.PointsRequired <= COALESCE(
              (SELECT SUM(ap.PointsEarned)
               FROM activity_point ap
               WHERE ap.AthleteID = %s),
              0
          )
          AND EXISTS (
              SELECT 1
              FROM athlete a
              WHERE a.AthleteID = %s
          )
        """,
        (athlete_id, reward_id, athlete_id, athlete_id),
    )
