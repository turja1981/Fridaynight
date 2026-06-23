from __future__ import annotations
import os
import tempfile
import pytest
from modules.audit.audit_logger import AuditLogger


@pytest.fixture
def audit(tmp_path):
    db_file = str(tmp_path / "test_audit.db")
    return AuditLogger(db_path=db_file)


class TestAuditLogger:
    def test_log_returns_event_id(self, audit):
        event_id = audit.log(
            event_type="chat",
            user_id="u1",
            input_text="What is my claim status?",
            output_text="Claim CLM-001 is under review.",
        )
        assert isinstance(event_id, str)
        assert len(event_id) > 0

    def test_log_event_is_retrievable(self, audit):
        audit.log(
            event_type="chat",
            user_id="user_abc",
            input_text="Hello",
            output_text="Hi there",
            decision="auto_approved",
        )
        results = audit.query(user_id="user_abc")
        assert len(results) == 1
        assert results[0]["user_id"] == "user_abc"
        assert results[0]["decision"] == "auto_approved"

    def test_query_by_event_type(self, audit):
        audit.log(event_type="chat", user_id="u1", input_text="a", output_text="b")
        audit.log(event_type="rag_query", user_id="u1", input_text="c", output_text="d")
        chat_results = audit.query(event_type="chat")
        assert all(r["event_type"] == "chat" for r in chat_results)

    def test_pii_detected_flag(self, audit):
        audit.log(
            event_type="chat",
            user_id="u2",
            input_text="My Aadhaar is ...",
            output_text="redacted",
            pii_detected=True,
        )
        summary = audit.get_summary()
        assert summary["pii_events"] >= 1

    def test_get_summary_structure(self, audit):
        audit.log(event_type="chat", user_id="u1", input_text="x", output_text="y", decision="auto_approved")
        audit.log(event_type="chat", user_id="u1", input_text="z", output_text="w", decision="blocked")
        summary = audit.get_summary()
        assert "total_events" in summary
        assert "auto_approved" in summary
        assert "blocked" in summary
        assert "escalated" in summary
        assert "pii_events" in summary
        assert summary["total_events"] == 2
        assert summary["auto_approved"] == 1
        assert summary["blocked"] == 1

    def test_multiple_users_isolated(self, audit):
        audit.log(event_type="chat", user_id="alice", input_text="q1", output_text="a1")
        audit.log(event_type="chat", user_id="bob", input_text="q2", output_text="a2")
        alice_events = audit.query(user_id="alice")
        bob_events = audit.query(user_id="bob")
        assert len(alice_events) == 1
        assert len(bob_events) == 1

    def test_long_text_is_truncated(self, audit):
        long_text = "x" * 5000
        event_id = audit.log(event_type="chat", user_id="u1", input_text=long_text, output_text="ok")
        results = audit.query(user_id="u1")
        assert len(results[0]["input_text"]) <= 2000
