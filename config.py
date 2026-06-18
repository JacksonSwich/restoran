"""Конфигурация подключения к БД."""

import pymysql.cursors

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "restaurant_management",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}
