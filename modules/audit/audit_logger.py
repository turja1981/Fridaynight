from __future__ import annotations
import sqlite3
import json
import time
import uuid
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuditEvent:
    event_id: str
    timestamp: float
    user_id: str
    event_type: str          # "chat", "rag_query", "agent_run", "auth", "hitl_decision"
    input_text: str
    output_text: str
    model_used: str
    agent_used: str
    confidence_score: float
    decision: str            # "auto_approved", "escalated", "pending_review", "blocked"
    tool_calls: list
    pii_detected: bool
    latency_ms: float
    adapter: str
    metadata: dict


class AuditLogger:
    """Append-only SQLite audit log for all AI decisions — covers IRDAI/RBI/ISO compliance."""

    def __init__(self, db_path: str = "./data/audit.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    event_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    input_text TEXT,
                    output_text TEXT,
                    model_used TEXT,
                    agent_used TEXT,
                    confidence_score REAL,
                    decision TEXT,
                    tool_calls TEXT,
                    pii_detected INTEGER,
                    latency_ms REAL,
                    adapter TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_log(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_log(event_type)")

    def log(
        self,
        event_type: str,
        user_id: str,
        input_text: str,
        output_text: str,
        model_used: str = "",
        agent_used: str = "",
        confidence_score: float = 0.0,
        decision: str = "",
        tool_calls: list | None = None,
        pii_detected: bool = False,
        latency_ms: float = 0.0,
        adapter: str = "",
        metadata: dict | None = None,
    ) -> str:
        event_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO audit_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id, time.time(), user_id, event_type,
                    input_text[:2000], output_text[:2000],
                    model_used, agent_used, confidence_score, decision,
                    json.dumps(tool_calls or []), int(pii_detected),
                    latency_ms, adapter, json.dumps(metadata or {}),
                ),
            )
        return event_id

    def query(
        self,
        user_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        conditions, params = [], []
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        params += [limit, offset]
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                f"SELECT * FROM audit_log {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                params,
            ).fetchall()
        return [
            {**dict(r), "tool_calls": json.loads(r["tool_calls"]), "metadata": json.loads(r["metadata"])}
            for r in rows
        ]

    def get_summary(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
            blocked = conn.execute("SELECT COUNT(*) FROM audit_log WHERE decision='blocked'").fetchone()[0]
            pii_events = conn.execute("SELECT COUNT(*) FROM audit_log WHERE pii_detected=1").fetchone()[0]
            auto_approved = conn.execute("SELECT COUNT(*) FROM audit_log WHERE decision='auto_approved'").fetchone()[0]
            escalated = conn.execute("SELECT COUNT(*) FROM audit_log WHERE decision='escalated'").fetchone()[0]
        return {
            "total_events": total,
            "auto_approved": auto_approved,
            "escalated": escalated,
            "blocked": blocked,
            "pii_events": pii_events,
        }
