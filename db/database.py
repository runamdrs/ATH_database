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
    # athlete_sport has no page of its own, so the athlete table lists
    # each athlete's sports as one comma-separated column.
    return run_select(
        """
        SELECT a.AthleteID, a.Name, a.Username, a.Email, a.Location, a.SkillLevel,
               (SELECT GROUP_CONCAT(s.Name ORDER BY s.Name SEPARATOR ', ')
                FROM athlete_sport x
                JOIN sport s ON s.SportID = x.SportID
                WHERE x.AthleteID = a.AthleteID) AS Sports
        FROM athlete a
        ORDER BY a.AthleteID
        """
    )


def get_all_achievements():
    # JOIN athlete so the table shows who earned it, not just an ID.
    return run_select(
        """
        SELECT ac.AchievementID, ac.AthleteID, a.Name AS Athlete, ac.Title,
               ac.Description, ac.DateEarned
        FROM achievement ac
        JOIN athlete a ON a.AthleteID = ac.AthleteID
        ORDER BY ac.AchievementID
        """
    )


def get_all_activities():
    # JOIN sport and athlete so the table shows the sport's name and the
    # organizer's name, not just their IDs.
    rows = run_select(
        """
        SELECT a.ActivityID, a.AthleteID, o.Name AS Organizer, s.Name AS Sport,
               a.Type, a.Date, a.Time, a.Duration, a.Location, a.MaxParticipants
        FROM activity a
        JOIN sport s ON s.SportID = a.SportID
        JOIN athlete o ON o.AthleteID = a.AthleteID
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


def get_roster(activity_id):
    """Everyone who joined one activity, with their status."""
    return run_select(
        """
        SELECT p.AthleteID, a.Name AS Athlete, p.JoinDate, p.ParticipationStatus
        FROM activity_participant p
        JOIN athlete a ON a.AthleteID = p.AthleteID
        WHERE p.ActivityID = %s
        ORDER BY p.JoinDate, a.Name
        """,
        (activity_id,)
    )


def get_all_recruiters():
    return run_select(
        """
        SELECT RecruiterID, Name, Organization, Email
        FROM recruiter
        ORDER BY Name, RecruiterID
        """
    )


def get_interest_for_athlete(athlete_id):
    """Every recruiter interested in one athlete, with the recruiter's name."""
    return run_select(
        """
        SELECT ra.RecruiterID, r.Name AS Recruiter, r.Organization,
               ra.InterestDate, ra.Status, ra.Notes
        FROM recruiter_athlete ra
        JOIN recruiter r ON r.RecruiterID = ra.RecruiterID
        WHERE ra.AthleteID = %s
        ORDER BY ra.InterestDate DESC, r.Name
        """,
        (athlete_id,)
    )


def get_all_posts():
    return run_select(
        """
        SELECT p.PostID, a.Name AS Athlete, p.Content, p.DateCreated, p.MediaURL,
               (SELECT COUNT(*) FROM comment c WHERE c.PostID = p.PostID) AS Comments
        FROM post p
        JOIN athlete a ON a.AthleteID = p.AthleteID
        ORDER BY p.DateCreated DESC, p.PostID DESC
        """
    )


def get_all_points():
    # LEFT JOIN because a points record may come from an activity, a
    # workout, or neither (a manual award), so both IDs can be NULL.
    return run_select(
        """
        SELECT ap.PointTransactionID, ap.AthleteID, a.Name AS Athlete,
               act.Type AS Activity, w.WorkoutType AS Workout,
               ap.PointsEarned, ap.Reason, ap.DateEarned
        FROM activity_point ap
        JOIN athlete a ON a.AthleteID = ap.AthleteID
        LEFT JOIN activity act ON act.ActivityID = ap.ActivityID
        LEFT JOIN workout w ON w.WorkoutID = ap.WorkoutID
        ORDER BY ap.DateEarned DESC, ap.PointTransactionID DESC
        """
    )


def get_comments_for_post(post_id):
    return run_select(
        """
        SELECT c.CommentID, c.AthleteID, a.Name AS Athlete, c.Text, c.DateCreated
        FROM comment c
        JOIN athlete a ON a.AthleteID = c.AthleteID
        WHERE c.PostID = %s
        ORDER BY c.DateCreated, c.CommentID
        """,
        (post_id,)
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


def get_sport_ids_for_athlete(athlete_id):
    """The SportIDs linked to one athlete, to pre-fill the sports picker."""
    rows = run_select(
        "SELECT SportID FROM athlete_sport WHERE AthleteID = %s",
        (athlete_id,)
    )
    return [row["SportID"] for row in rows]


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


def get_point_by_id(point_id):
    rows = run_select(
        """
        SELECT PointTransactionID, AthleteID, ActivityID, WorkoutID,
               PointsEarned, Reason, DateEarned
        FROM activity_point
        WHERE PointTransactionID = %s
        """,
        (point_id,)
    )
    return rows[0] if rows else None


def get_comment_by_id(comment_id):
    rows = run_select(
        """
        SELECT CommentID, AthleteID, PostID, Text, DateCreated
        FROM comment
        WHERE CommentID = %s
        """,
        (comment_id,)
    )
    return rows[0] if rows else None


def get_participant(activity_id, athlete_id):
    # activity_participant has a two-column primary key, so both halves
    # are needed to find one row.
    rows = run_select(
        """
        SELECT ActivityID, AthleteID, JoinDate, ParticipationStatus
        FROM activity_participant
        WHERE ActivityID = %s AND AthleteID = %s
        """,
        (activity_id, athlete_id)
    )
    return rows[0] if rows else None


def get_recruiter_interest(recruiter_id, athlete_id):
    # recruiter_athlete has a two-column primary key, so both halves
    # are needed to find one row.
    rows = run_select(
        """
        SELECT RecruiterID, AthleteID, InterestDate, Status, Notes
        FROM recruiter_athlete
        WHERE RecruiterID = %s AND AthleteID = %s
        """,
        (recruiter_id, athlete_id)
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

def insert_athlete(name, username, email, location, skill_level, sport_ids=()):
    """Insert an athlete and one athlete_sport row per chosen sport, in
    one transaction. Returns {table: rows inserted}."""
    statements = [(
        "athlete",
        """
        INSERT INTO athlete (Name, Username, Email, Location, SkillLevel)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, username, email, location, skill_level)
    )]
    # LAST_INSERT_ID() is the AthleteID MySQL just generated on this
    # connection. athlete_sport has no AUTO_INCREMENT column, so these
    # inserts do not change it.
    for sport_id in sport_ids:
        statements.append((
            f"athlete_sport {sport_id}",
            "INSERT INTO athlete_sport (AthleteID, SportID) VALUES (LAST_INSERT_ID(), %s)",
            (sport_id,)
        ))
    return run_write_many(statements)


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

def update_athlete(athlete_id, name, username, email, location, skill_level,
                   sport_ids=()):
    """Update an athlete and replace their sport links, in one
    transaction. Returns {table: rows affected}; "athlete" is 0 when no
    athlete with that ID exists."""
    statements = [
        ("athlete", """
            UPDATE athlete
            SET Name = %s, Username = %s, Email = %s, Location = %s, SkillLevel = %s
            WHERE AthleteID = %s
         """, (name, username, email, location, skill_level, athlete_id)),
        # Simplest way to change the links: drop the old ones, add the
        # chosen ones. Both happen in the same transaction.
        ("athlete_sport", "DELETE FROM athlete_sport WHERE AthleteID = %s",
         (athlete_id,)),
    ]
    for sport_id in sport_ids:
        statements.append((
            f"athlete_sport {sport_id}",
            "INSERT INTO athlete_sport (AthleteID, SportID) VALUES (%s, %s)",
            (athlete_id, sport_id)
        ))
    return run_write_many(statements)


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


# ---------------------------------------------------------------
# activity_participant: written by "Join" and by status changes.
# ---------------------------------------------------------------

def insert_participant(activity_id, athlete_id):
    """Register an athlete for an activity. Inserts 0 rows when the
    activity does not exist or is already full."""
    return run_write(
        """
        INSERT INTO activity_participant
            (ActivityID, AthleteID, JoinDate, ParticipationStatus)
        SELECT a.ActivityID, %s, CURDATE(), 'Registered'
        FROM activity a
        WHERE a.ActivityID = %s
          AND (a.MaxParticipants IS NULL
               OR (SELECT COUNT(*) FROM activity_participant p
                   WHERE p.ActivityID = a.ActivityID) < a.MaxParticipants)
        """,
        (athlete_id, activity_id)
    )


def update_participant_status(activity_id, athlete_id, status, points):
    """Change a participant's status. When it becomes 'Attended', also
    award `points` in activity_point, once per athlete and activity, in
    the same transaction. Returns {table: rows affected}."""
    statements = [
        ("activity_participant", """
            UPDATE activity_participant
            SET ParticipationStatus = %s
            WHERE ActivityID = %s AND AthleteID = %s
         """, (status, activity_id, athlete_id)),
    ]
    if status == "Attended" and points > 0:
        # NOT EXISTS stops a second award when someone is marked Attended
        # twice; the EXISTS makes sure the participant really is there.
        statements.append(("activity_point", """
            INSERT INTO activity_point
                (AthleteID, ActivityID, WorkoutID, PointsEarned, Reason, DateEarned)
            SELECT %s, %s, NULL, %s, 'Attended activity', NOW()
            FROM DUAL
            WHERE EXISTS (
                SELECT 1 FROM activity_participant
                WHERE ActivityID = %s AND AthleteID = %s
            )
              AND NOT EXISTS (
                SELECT 1 FROM activity_point
                WHERE AthleteID = %s AND ActivityID = %s
                  AND Reason = 'Attended activity'
            )
         """, (athlete_id, activity_id, points, activity_id, athlete_id,
               athlete_id, activity_id)))
    return run_write_many(statements)


def delete_participant(activity_id, athlete_id):
    """Take an athlete off an activity. No table references
    activity_participant, so this is a single statement; points already
    earned for the activity stay in activity_point."""
    return run_write_many([
        ("activity_participant", """
            DELETE FROM activity_participant
            WHERE ActivityID = %s AND AthleteID = %s
         """, (activity_id, athlete_id)),
    ])


# ---------------------------------------------------------------
# recruiter_athlete: a recruiter's interest in an athlete. It has
# columns of its own (date, status, notes), so it is written from
# the athlete's page, not from a page of its own.
# ---------------------------------------------------------------

def insert_recruiter_interest(recruiter_id, athlete_id, status, notes):
    return run_write(
        """
        INSERT INTO recruiter_athlete
            (RecruiterID, AthleteID, InterestDate, Status, Notes)
        VALUES (%s, %s, CURDATE(), %s, %s)
        """,
        (recruiter_id, athlete_id, status, notes)
    )


def update_recruiter_interest(recruiter_id, athlete_id, status, notes):
    return run_write(
        """
        UPDATE recruiter_athlete
        SET Status = %s, Notes = %s
        WHERE RecruiterID = %s AND AthleteID = %s
        """,
        (status, notes, recruiter_id, athlete_id)
    )


def delete_recruiter_interest(recruiter_id, athlete_id):
    """Withdraw a recruiter's interest. Nothing references
    recruiter_athlete, so this is a single statement inside
    run_write_many() to keep the usual {table: rows deleted} shape."""
    return run_write_many([
        ("recruiter_athlete", """
            DELETE FROM recruiter_athlete
            WHERE RecruiterID = %s AND AthleteID = %s
         """, (recruiter_id, athlete_id)),
    ])


# ---------------------------------------------------------------
# activity_point: Activity Points earned by athletes. Awarded
# automatically for attending an activity, or entered by hand.
# ---------------------------------------------------------------

def insert_point(athlete_id, activity_id, workout_id, points_earned, reason,
                 date_earned):
    return run_write(
        """
        INSERT INTO activity_point
            (AthleteID, ActivityID, WorkoutID, PointsEarned, Reason, DateEarned)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (athlete_id, activity_id, workout_id, points_earned, reason, date_earned)
    )


def update_point(point_id, athlete_id, activity_id, workout_id, points_earned,
                 reason, date_earned):
    return run_write(
        """
        UPDATE activity_point
        SET AthleteID = %s, ActivityID = %s, WorkoutID = %s, PointsEarned = %s,
            Reason = %s, DateEarned = %s
        WHERE PointTransactionID = %s
        """,
        (athlete_id, activity_id, workout_id, points_earned, reason, date_earned,
         point_id)
    )


def delete_point(point_id):
    """Delete a points record. Nothing references activity_point, so
    this is a single statement inside run_write_many() to keep the
    usual {table: rows deleted} shape."""
    return run_write_many([
        ("activity_point", "DELETE FROM activity_point WHERE PointTransactionID = %s",
         (point_id,)),
    ])


# ---------------------------------------------------------------
# post and comment
# ---------------------------------------------------------------

def insert_post(athlete_id, content, media_url):
    return run_write(
        """
        INSERT INTO post (AthleteID, Content, DateCreated, MediaURL)
        VALUES (%s, %s, NOW(), %s)
        """,
        (athlete_id, content, media_url)
    )


def insert_comment(athlete_id, post_id, text):
    return run_write(
        """
        INSERT INTO comment (AthleteID, PostID, Text, DateCreated)
        VALUES (%s, %s, %s, NOW())
        """,
        (athlete_id, post_id, text)
    )


def update_comment(comment_id, text):
    # Only the text can change: the author and the post stay the same.
    return run_write(
        "UPDATE comment SET Text = %s WHERE CommentID = %s",
        (text, comment_id)
    )


def delete_comment(comment_id):
    """Delete a comment. Nothing references comment, so this is a single
    statement inside run_write_many() to keep the usual shape."""
    return run_write_many([
        ("comment", "DELETE FROM comment WHERE CommentID = %s", (comment_id,)),
    ])
