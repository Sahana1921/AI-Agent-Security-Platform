import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "security.db"
)


def create_database():
    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            classification TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            decision TEXT NOT NULL,
            matched_rules INTEGER NOT NULL,
            detected_by TEXT NOT NULL,
            ml_confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_security_event(
    prompt,
    classification,
    risk_score,
    risk_level,
    decision,
    matched_rules,
    detected_by,
    ml_confidence
):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO security_events (
            prompt,
            classification,
            risk_score,
            risk_level,
            decision,
            matched_rules,
            detected_by,
            ml_confidence,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prompt,
        classification,
        risk_score,
        risk_level,
        decision,
        matched_rules,
        detected_by,
        ml_confidence,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_all_events():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM security_events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()
    connection.close()

    return [dict(event) for event in events]