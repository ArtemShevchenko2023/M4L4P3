import sqlite3
from datetime import datetime
from config import DATABASE 
import os
import cv2

class DatabaseManager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT
            )
        ''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                note_id INTEGER,
                note_bio TEXT,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')


            conn.commit()