import mysql.connector
import streamlit as st


# ---------------------------------------------------------------
# Part 1: sample data
# Rows mirror the INSERT statements in ATH_database.sql so the
# interface looks the same before and after the MySQL swap.
# ---------------------------------------------------------------

def get_all_athletes():
    return [
        {"AthleteID": 1, "Name": "Alex Morgan", "Username": "alexmorgan",
         "Email": "alex.morgan@example.com", "Location": "Hickory, NC",
         "SkillLevel": "Advanced"},
        {"AthleteID": 2, "Name": "Jordan Lee", "Username": "jordanlee",
         "Email": "jordan.lee@example.com", "Location": "Charlotte, NC",
         "SkillLevel": "Intermediate"},
        {"AthleteID": 3, "Name": "Taylor Smith", "Username": "taylorsmith",
         "Email": "taylor.smith@example.com", "Location": "Atlanta, GA",
         "SkillLevel": "Advanced"},
        {"AthleteID": 4, "Name": "Chris Davis", "Username": "chrisdavis",
         "Email": "chris.davis@example.com", "Location": "Columbia, SC",
         "SkillLevel": "Beginner"},
        {"AthleteID": 5, "Name": "Sam Wilson", "Username": "samwilson",
         "Email": "sam.wilson@example.com", "Location": "Greenville, SC",
         "SkillLevel": "Intermediate"},
    ]


def get_all_achievements():
    return [
        {"AchievementID": 1, "AthleteID": 1, "Title": "Tournament Top 10",
         "Description": "Finished in the top ten at a golf tournament.",
         "DateEarned": "2026-10-10"},
        {"AchievementID": 2, "AthleteID": 2, "Title": "Team MVP",
         "Description": "Recognized for outstanding basketball performance.",
         "DateEarned": "2026-09-25"},
        {"AchievementID": 3, "AthleteID": 3, "Title": "Scoring Leader",
         "Description": "Led the team in goals during the season.",
         "DateEarned": "2026-10-05"},
        {"AchievementID": 4, "AthleteID": 4, "Title": "Personal Best",
         "Description": "Achieved a personal best in the 100-meter freestyle.",
         "DateEarned": "2026-10-12"},
        {"AchievementID": 5, "AthleteID": 5, "Title": "Sprint Record",
         "Description": "Set a new personal record in the 100-meter sprint.",
         "DateEarned": "2026-10-15"},
    ]


# ---------------------------------------------------------------
# Database connection (used in Part 2)
# ---------------------------------------------------------------

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["db_host"],
        port=st.secrets["db_port"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        database=st.secrets["db_name"]
    )
