import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["db_host"],
        port=st.secrets["db_port"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        database=st.secrets["db_name"]
    )
