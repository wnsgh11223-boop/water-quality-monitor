import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "weather_history.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                city        TEXT NOT NULL,
                temp_now    INTEGER,
                temp_max    INTEGER,
                temp_min    INTEGER,
                desc        TEXT,
                precip      INTEGER,
                type        TEXT NOT NULL
            )
        """)
        conn.commit()


def save_weather(data: dict, log_type: str = "자동 알림"):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO weather_log (recorded_at, city, temp_now, temp_max, temp_min, desc, precip, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            data["city"],
            data["temp_now"],
            data["temp_max"],
            data["temp_min"],
            data["desc"],
            data["precip"],
            log_type,
        ))
        conn.commit()


def get_history(limit: int = 20):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT recorded_at, type, city, temp_now, temp_max, temp_min, desc, precip
            FROM weather_log
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [
        {
            "recorded_at": r[0],
            "type":        r[1],
            "city":        r[2],
            "temp_now":    r[3],
            "temp_max":    r[4],
            "temp_min":    r[5],
            "desc":        r[6],
            "precip":      r[7],
        }
        for r in rows
    ]
