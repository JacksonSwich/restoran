"""Подключение к MySQL через pymysql."""

import pymysql
from config import DB_CONFIG


def get_connection():
    """Вернуть новое соединение с БД."""
    return pymysql.connect(**DB_CONFIG)


def execute(query: str, params: tuple | None = None) -> int:
    """Выполнить INSERT/UPDATE/DELETE и вернуть количество затронутых строк."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def fetch_one(query: str, params: tuple | None = None) -> dict | None:
    """Вернуть одну запись или None."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()
    finally:
        conn.close()


def fetch_all(query: str, params: tuple | None = None) -> list[dict]:
    """Вернуть все записи."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def execute_insert(query: str, params: tuple | None = None) -> int:
    """Выполнить INSERT и вернуть id новой записи."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
