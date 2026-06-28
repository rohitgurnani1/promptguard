"""SQLite-backed evaluation run history."""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from promptguard.config import Config
from promptguard.eval.metrics import EvalRunResult
from promptguard.history.serialization import result_from_dict, result_to_dict

DEFAULT_HISTORY_DIR = Path.home() / ".promptguard"
DEFAULT_HISTORY_DB = DEFAULT_HISTORY_DIR / "history.db"


def resolve_history_db_path(db_path: Optional[str] = None) -> str:
    """Resolve and normalize the SQLite database path."""
    raw = (db_path or Config.HISTORY_DB_PATH or "").strip()
    if not raw:
        path = DEFAULT_HISTORY_DB
    else:
        path = Path(raw).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    return str(path.resolve())


@dataclass
class RunSummary:
    id: str
    created_at: str
    provider: str
    model_name: str
    scorer: str
    num_attacks: int
    num_defenses: int
    avg_asr: float


class RunHistoryStore:
    """Persist and retrieve evaluation runs."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = resolve_history_db_path(db_path)
        parent = Path(self.db_path).parent
        if parent.name:
            parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(
        self,
        provider: str,
        model_name: str,
        config: Dict[str, Any],
        result: EvalRunResult,
        run_id: Optional[str] = None,
    ) -> str:
        run_id = run_id or str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        config_json = json.dumps(config)
        result_json = json.dumps(result_to_dict(result))

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (id, created_at, provider, model_name, config_json, result_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, created_at, provider, model_name, config_json, result_json),
            )
            conn.commit()

        return run_id

    def list_runs(self, limit: int = 50) -> List[RunSummary]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, provider, model_name, config_json, result_json
                FROM runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        summaries: List[RunSummary] = []
        for row in rows:
            config = json.loads(row[4])
            result = result_from_dict(json.loads(row[5]))
            avg_asr = (
                sum(s.asr for s in result.summaries) / len(result.summaries)
                if result.summaries
                else 0.0
            )
            summaries.append(
                RunSummary(
                    id=row[0],
                    created_at=row[1],
                    provider=row[2],
                    model_name=row[3],
                    scorer=config.get("scorer", "heuristic"),
                    num_attacks=len({r.attack_name for r in result.attack_records}),
                    num_defenses=len(result.summaries),
                    avg_asr=avg_asr,
                )
            )
        return summaries

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, created_at, provider, model_name, config_json, result_json
                FROM runs WHERE id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "created_at": row[1],
            "provider": row[2],
            "model_name": row[3],
            "config": json.loads(row[4]),
            "result": result_from_dict(json.loads(row[5])),
        }

    def get_result(self, run_id: str) -> Optional[EvalRunResult]:
        record = self.get(run_id)
        if record is None:
            return None
        return record["result"]

    def delete(self, run_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            conn.commit()
            return cursor.rowcount > 0
