"""Survey results storage: PostgreSQL (production) or local JSON files (development)."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any, Iterator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(ROOT, "data", "results", "choices.jsonl")
SESSIONS_PATH = os.path.join(ROOT, "data", "results", "active_sessions.json")
COMPLETED_TOKENS_PATH = os.path.join(ROOT, "data", "results", "completed_tokens.json")

_SCHEMA_READY = False

CHOICE_COLUMNS = (
    "response_id",
    "participant_id",
    "timestamp",
    "survey_mode",
    "session_questions",
    "question_number",
    "code_id",
    "description",
    "category",
    "category_label",
    "choice_label",
    "chosen_source",
    "has_injected_bug",
    "bug_type",
    "bug_id",
    "mapping",
)


class StorageUnavailableError(RuntimeError):
    """Kalici depolama kullanilamiyor."""


def is_render_host() -> bool:
    return os.getenv("RENDER") == "true"


def database_url() -> str | None:
    url = (os.getenv("DATABASE_URL") or "").strip()
    return url or None


def use_postgres() -> bool:
    return database_url() is not None


def storage_backend() -> str:
    return "postgres" if use_postgres() else "file"


def assert_persistent_storage() -> None:
    """Render'da gecici diske yazmayi engelle."""
    if is_render_host() and not use_postgres():
        raise StorageUnavailableError(
            "Render ortaminda DATABASE_URL zorunludur. "
            "Anket cevaplari gecici diske kaydedilmez."
        )


def verify_postgres_connection() -> tuple[bool, str | None]:
    if not use_postgres():
        return False, "DATABASE_URL ayarli degil"
    try:
        ensure_schema()
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True, None
    except Exception as exc:
        return False, str(exc)


def storage_operational() -> bool:
    if is_render_host():
        ok, _ = verify_postgres_connection()
        return ok
    return True


def _connection_url() -> str:
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if "render.com" in url and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


@contextmanager
def _pg_conn() -> Iterator[Any]:
    import time

    import psycopg2
    from psycopg2.extras import RealDictCursor

    last_exc: Exception | None = None
    for attempt in range(4):
        try:
            conn = psycopg2.connect(
                _connection_url(),
                cursor_factory=RealDictCursor,
                connect_timeout=10,
            )
            break
        except Exception as exc:
            last_exc = exc
            if attempt < 3:
                time.sleep(1.5 * (attempt + 1))
    else:
        raise last_exc  # type: ignore[misc]

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_schema() -> None:
    global _SCHEMA_READY
    if _SCHEMA_READY or not use_postgres():
        return
    with _pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_choices (
                    id SERIAL PRIMARY KEY,
                    response_id TEXT,
                    participant_id TEXT,
                    timestamp TIMESTAMPTZ,
                    survey_mode TEXT,
                    session_questions INT,
                    question_number INT,
                    code_id TEXT,
                    description TEXT,
                    category TEXT,
                    category_label TEXT,
                    choice_label TEXT,
                    chosen_source TEXT,
                    has_injected_bug BOOLEAN,
                    bug_type TEXT,
                    bug_id TEXT,
                    mapping JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS completed_participants (
                    token TEXT PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_sessions (
                    response_id TEXT PRIMARY KEY,
                    state JSONB NOT NULL,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
    _SCHEMA_READY = True


def append_result(row: dict[str, Any]) -> None:
    assert_persistent_storage()
    if use_postgres():
        ensure_schema()
        from psycopg2.extras import Json

        payload = {key: row.get(key) for key in CHOICE_COLUMNS}
        cols = [k for k in CHOICE_COLUMNS if payload.get(k) is not None]
        values = []
        for key in cols:
            value = payload[key]
            if key == "mapping" and value is not None:
                if isinstance(value, str):
                    value = json.loads(value)
                values.append(Json(value))
            else:
                values.append(value)
        placeholders = ", ".join("%s" for _ in cols)
        column_sql = ", ".join(cols)
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO survey_choices ({column_sql}) VALUES ({placeholders})",
                    values,
                )
        return

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_rows() -> list[dict[str, Any]]:
    if is_render_host() and not use_postgres():
        return []
    if use_postgres():
        ensure_schema()
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT response_id, participant_id, timestamp, survey_mode,
                           session_questions, question_number, code_id, description,
                           category, category_label, choice_label, chosen_source,
                           has_injected_bug, bug_type, bug_id, mapping
                    FROM survey_choices
                    ORDER BY id
                    """
                )
                rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            if item.get("timestamp") is not None:
                item["timestamp"] = item["timestamp"].isoformat()
            if item.get("has_injected_bug") is not None:
                item["has_injected_bug"] = bool(item["has_injected_bug"])
            out.append(item)
        return out

    if not os.path.exists(RESULTS_PATH):
        return []
    rows: list[dict[str, Any]] = []
    with open(RESULTS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


class SurveySessionStore:
    """5 soruluk anket durumunu sunucu tarafinda tutar."""

    def __init__(self, path: str = SESSIONS_PATH) -> None:
        self.path = path

    def _load_file(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_file(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, question_ids: list[str]) -> str:
        assert_persistent_storage()
        import uuid

        response_id = str(uuid.uuid4())
        state = {
            "question_ids": question_ids,
            "index": 0,
            "total": len(question_ids),
            "completed": False,
        }
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO survey_sessions (response_id, state)
                        VALUES (%s, %s)
                        ON CONFLICT (response_id) DO UPDATE SET state = EXCLUDED.state
                        """,
                        (response_id, json.dumps(state)),
                    )
            return response_id

        data = self._load_file()
        data[response_id] = state
        self._save_file(data)
        return response_id

    def get(self, response_id: str | None) -> dict | None:
        if not response_id:
            return None
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state FROM survey_sessions WHERE response_id = %s",
                        (response_id,),
                    )
                    row = cur.fetchone()
            return dict(row["state"]) if row else None

        return self._load_file().get(response_id)

    def advance(self, response_id: str) -> dict | None:
        state = self.get(response_id)
        if not state:
            return None
        state["index"] = int(state.get("index", 0)) + 1
        if state["index"] >= int(state.get("total", 5)):
            state["completed"] = True
        self._upsert(response_id, state)
        return state

    def delete(self, response_id: str | None) -> None:
        if not response_id:
            return
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM survey_sessions WHERE response_id = %s",
                        (response_id,),
                    )
            return

        data = self._load_file()
        if response_id in data:
            del data[response_id]
            self._save_file(data)

    def _upsert(self, response_id: str, state: dict) -> None:
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO survey_sessions (response_id, state)
                        VALUES (%s, %s)
                        ON CONFLICT (response_id) DO UPDATE SET state = EXCLUDED.state
                        """,
                        (response_id, json.dumps(state)),
                    )
            return

        data = self._load_file()
        data[response_id] = state
        self._save_file(data)


class CompletedParticipantStore:
    """Tamamlayan katilimcilari sunucu tarafinda isaretler."""

    def __init__(self, path: str = COMPLETED_TOKENS_PATH) -> None:
        self.path = path

    def has_token(self, token: str | None) -> bool:
        if not token:
            return False
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM completed_participants WHERE token = %s",
                        (token,),
                    )
                    return cur.fetchone() is not None

        return token in self._load_file()

    def register(self, token: str) -> None:
        assert_persistent_storage()
        if use_postgres():
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO completed_participants (token)
                        VALUES (%s)
                        ON CONFLICT (token) DO NOTHING
                        """,
                        (token,),
                    )
            return

        tokens = self._load_file()
        tokens.add(token)
        self._save_file(tokens)

    def _load_file(self) -> set[str]:
        if not os.path.exists(self.path):
            return set()
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return {str(x) for x in data}
        except (json.JSONDecodeError, OSError):
            pass
        return set()

    def _save_file(self, tokens: set[str]) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(sorted(tokens), f, ensure_ascii=False, indent=2)


def get_storage_stats() -> dict[str, Any]:
    """Depolama ozeti: katilimci, cevap, baglanti durumu."""
    stats: dict[str, Any] = {
        "backend": storage_backend(),
        "database_configured": use_postgres(),
        "database_connected": False,
        "database_error": None,
        "choices_count": 0,
        "participant_count": 0,
        "completed_tokens": 0,
        "active_sessions": 0,
        "results_file": RESULTS_PATH,
        "results_file_exists": os.path.exists(RESULTS_PATH),
    }

    if use_postgres():
        try:
            ensure_schema()
            with _pg_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) AS n FROM survey_choices")
                    stats["choices_count"] = int(cur.fetchone()["n"])
                    cur.execute(
                        """
                        SELECT COUNT(DISTINCT COALESCE(response_id, participant_id)) AS n
                        FROM survey_choices
                        WHERE COALESCE(response_id, participant_id) IS NOT NULL
                        """
                    )
                    stats["participant_count"] = int(cur.fetchone()["n"])
                    cur.execute("SELECT COUNT(*) AS n FROM completed_participants")
                    stats["completed_tokens"] = int(cur.fetchone()["n"])
                    cur.execute("SELECT COUNT(*) AS n FROM survey_sessions")
                    stats["active_sessions"] = int(cur.fetchone()["n"])
            stats["database_connected"] = True
        except Exception as exc:
            stats["database_error"] = str(exc)
        return stats

    rows = load_rows()
    stats["choices_count"] = len(rows)
    stats["participant_count"] = len(
        {
            r.get("response_id") or r.get("participant_id")
            for r in rows
            if r.get("response_id") or r.get("participant_id")
        }
    )
    store = CompletedParticipantStore()
    stats["completed_tokens"] = len(store._load_file())
    session_data = SurveySessionStore()._load_file()
    stats["active_sessions"] = len(session_data)
    return stats


def fetch_recent_choices(limit: int = 10) -> list[dict[str, Any]]:
    """Son kaydedilen cevaplari getir."""
    if use_postgres():
        ensure_schema()
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT response_id, participant_id, timestamp, question_number,
                           code_id, chosen_source, choice_label, category_label
                    FROM survey_choices
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            if item.get("timestamp") is not None:
                item["timestamp"] = item["timestamp"].isoformat()
            out.append(item)
        return out

    rows = load_rows()
    trimmed = rows[-limit:] if limit else rows
    return [
        {
            "response_id": r.get("response_id") or r.get("participant_id"),
            "timestamp": r.get("timestamp"),
            "question_number": r.get("question_number"),
            "code_id": r.get("code_id"),
            "chosen_source": r.get("chosen_source"),
            "choice_label": r.get("choice_label"),
            "category_label": r.get("category_label"),
        }
        for r in reversed(trimmed)
    ]


def storage_health() -> dict[str, Any]:
    """Canli ortam saglik ozeti."""
    stats = get_storage_stats()
    if use_postgres():
        connected, error = verify_postgres_connection()
    else:
        connected = not is_render_host()
        error = "DATABASE_URL ayarli degil" if is_render_host() else None
    return {
        "operational": storage_operational(),
        "backend": storage_backend(),
        "persistent": use_postgres(),
        "render_host": is_render_host(),
        "database_connected": connected,
        "database_error": error,
        "choices_count": stats.get("choices_count", 0),
        "participant_count": stats.get("participant_count", 0),
    }
