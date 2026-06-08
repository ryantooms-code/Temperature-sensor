"""
database.py - SQLite3 database layer
Handles DB init, inserting readings, and querying data.
Database stored at: /home/toomsey/assignement/sense_data.db
"""

import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "/home/toomsey/assignement/sense_data.db")


def get_connection():
    """Return a SQLite connection with row_factory for dict-like access."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the sensor_readings table if it doesn't exist."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   DATETIME DEFAULT (datetime('now', 'localtime')),
                temperature REAL NOT NULL,
                humidity    REAL NOT NULL,
                pressure    REAL NOT NULL,
                status      TEXT NOT NULL
            )
        """)
        conn.commit()
        logger.info("Database initialised at %s", DB_PATH)
    finally:
        conn.close()


def insert_reading(temperature: float, humidity: float, pressure: float, status: str):
    """Insert a new sensor reading row."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO sensor_readings (temperature, humidity, pressure, status)
            VALUES (?, ?, ?, ?)
            """,
            (round(temperature, 2), round(humidity, 2), round(pressure, 2), status)
        )
        conn.commit()
        logger.debug("Inserted reading — temp=%.2f hum=%.2f pres=%.2f status=%s",
                     temperature, humidity, pressure, status)
    finally:
        conn.close()


def get_latest_reading():
    """Return the most recently inserted reading as a Row object."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 1"
        )
        return cur.fetchone()
    finally:
        conn.close()


def get_all_readings(limit: int = 500):
    """Return up to `limit` most recent readings, newest first."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?", (limit,)
        )
        return cur.fetchall()
    finally:
        conn.close()
