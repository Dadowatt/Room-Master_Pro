import mysql.connector
from dotenv import load_dotenv
import os
from contextlib import contextmanager

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

@contextmanager
def get_cursor(dictionary=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        
try:
    with get_cursor(dictionary=True) as cursor:
        print("Connexion réussie à la base de données MySQL")
except mysql.connector.Error as e:
    print(f"Erreur de connexion : {e}")
