"""Подключение к MySQL через pymysql с пулом соединений и кешем запросов."""

import queue
import threading
import time
from typing import Any

import pymysql
from config import DB_CONFIG


# ---------------------------------------------------------------------------
# Connection pool
# ---------------------------------------------------------------------------

class ConnectionPool:
    """Потокобезопасный пул соединений MySQL.

    Использует ``queue.Queue`` для хранения готовых соединений.
    Если пул исчерпан, создаётся временное соединение (оно будет закрыто
    при возврате, а не положено обратно в очередь).
    """

    def __init__(
        self,
        pool_size: int = 5,
        pool_name: str = "default",
        **kwargs: Any,
    ) -> None:
        self.pool_size = pool_size
        self.pool_name = pool_name
        self._lock = threading.Lock()
        self._pool: queue.Queue = queue.Queue(maxsize=pool_size)
        self._kwargs: dict = kwargs or DB_CONFIG
        self._initialized: bool = False

    # -- helpers -----------------------------------------------------------

    def _create_connection(self) -> pymysql.connections.Connection:
        """Создать новое (сырое) соединение."""
        return pymysql.connect(**self._kwargs)

    @staticmethod
    def _is_alive(conn: pymysql.connections.Connection) -> bool:
        """Проверить, живо ли соединение (без авто-переподключения)."""
        try:
            conn.ping(reconnect=False)
            return True
        except Exception:
            return False

    def _init_pool(self) -> None:
        """Лениво заполнить очередь соединениями (thread-safe)."""
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            for _ in range(self.pool_size):
                self._pool.put(self._create_connection())
            self._initialized = True

    # -- public API --------------------------------------------------------

    def acquire(self) -> pymysql.connections.Connection:
        """Взять соединение из пула (или создать временное)."""
        self._init_pool()
        try:
            conn = self._pool.get_nowait()
        except queue.Empty:
            # Пул исчерпан — временное соединение (не кладём обратно)
            conn = self._create_connection()

        # Авто-переподключение: заменить битое
        if not self._is_alive(conn):
            try:
                conn.close()
            except Exception:
                pass
            conn = self._create_connection()

        return conn

    def release(self, conn: pymysql.connections.Connection) -> None:
        """Вернуть соединение в пул (или закрыть, если очередь полна)."""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            try:
                conn.close()
            except Exception:
                pass

    def close_all(self) -> None:
        """Закрыть все соединения в пуле."""
        with self._lock:
            while not self._pool.empty():
                try:
                    self._pool.get_nowait().close()
                except Exception:
                    pass
            self._initialized = False


# ---------------------------------------------------------------------------
# Module-level singleton pool
# ---------------------------------------------------------------------------

_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()


def get_pool() -> ConnectionPool:
    """Вернуть (создав при первом вызове) глобальный экземпляр пула.

    Параметры пула можно изменить до первого вызова через
    ``configure_pool()``.
    """
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ConnectionPool()
    return _pool


def configure_pool(
    pool_size: int = 5,
    pool_name: str = "default",
    **kwargs: Any,
) -> None:
    """Настроить глобальный пул (пересоздать, если уже существует).

    Вызов до первого использования позволяет переопределить
    ``pool_size``, ``pool_name`` и/или параметры соединения.
    """
    global _pool
    new_pool = ConnectionPool(pool_size=pool_size, pool_name=pool_name, **kwargs)
    with _pool_lock:
        if _pool is not None:
            _pool.close_all()
        _pool = new_pool


def close_pool() -> None:
    """Закрыть все соединения и сбросить глобальный пул + кеш."""
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.close_all()
            _pool = None
    clear_cache()


# ---------------------------------------------------------------------------
# Query cache (dict + TTL)
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[Any, float]] = {}
_cache_lock = threading.Lock()
CACHE_TTL: int = 30  # seconds — переопределяется через configure_cache()


def configure_cache(ttl_seconds: int = 30) -> None:
    """Установить время жизни кешированных результатов (по умолчанию 30 с)."""
    global CACHE_TTL
    CACHE_TTL = ttl_seconds


def _cache_key(query: str, params: tuple | None) -> str:
    """Строковый ключ для кеша."""
    return f"{query}:{params}"


def _get_from_cache(key: str) -> Any:
    """Вернуть закешированный результат или None."""
    with _cache_lock:
        if key in _cache:
            result, timestamp = _cache[key]
            if time.time() - timestamp < CACHE_TTL:
                return result
            # Просрочено — удалить
            del _cache[key]
    return None


def _set_cache(key: str, result: Any) -> None:
    """Положить результат в кеш."""
    with _cache_lock:
        _cache[key] = (result, time.time())


def clear_cache() -> None:
    """Очистить весь кеш запросов."""
    with _cache_lock:
        _cache.clear()


def cache_info() -> dict:
    """Вернуть статистику кеша."""
    with _cache_lock:
        now = time.time()
        total = len(_cache)
        active = sum(1 for _, ts in _cache.values() if now - ts < CACHE_TTL)
        return {
            "total_entries": total,
            "active_entries": active,
            "expired_entries": total - active,
            "ttl_seconds": CACHE_TTL,
        }


# ---------------------------------------------------------------------------
# Public functions (signatures сохранены)
# ---------------------------------------------------------------------------

def execute(query: str, params: tuple | None = None) -> int:
    """Выполнить INSERT/UPDATE/DELETE и вернуть количество затронутых строк."""
    pool = get_pool()
    conn = pool.acquire()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()
        return cur.rowcount
    finally:
        pool.release(conn)


def fetch_one(query: str, params: tuple | None = None) -> dict | None:
    """Вернуть одну запись или None (с кешированием)."""
    key = _cache_key(query, params)
    cached = _get_from_cache(key)
    if cached is not None:
        return cached

    pool = get_pool()
    conn = pool.acquire()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchone()
        _set_cache(key, result)
        return result
    finally:
        pool.release(conn)


def fetch_all(query: str, params: tuple | None = None) -> list[dict]:
    """Вернуть все записи (с кешированием)."""
    key = _cache_key(query, params)
    cached = _get_from_cache(key)
    if cached is not None:
        return cached

    pool = get_pool()
    conn = pool.acquire()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            result = cur.fetchall()
        _set_cache(key, result)
        return result
    finally:
        pool.release(conn)


def execute_insert(query: str, params: tuple | None = None) -> int:
    """Выполнить INSERT и вернуть id новой записи."""
    pool = get_pool()
    conn = pool.acquire()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        pool.release(conn)
