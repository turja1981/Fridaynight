from __future__ import annotations
import pytest
from modules.model_router.router import ModelRouter


class TestModelRouter:
    def setup_method(self):
        self.router = ModelRouter()

    def test_routes_greeting_to_haiku(self):
        model = self.router.route("hello there")
        assert model == "claude-haiku-4-5-20251001"

    def test_routes_status_to_haiku(self):
        model = self.router.route("what is the status?")
        assert model == "claude-haiku-4-5-20251001"

    def test_routes_analysis_to_opus(self):
        model = self.router.route("analyze and synthesize all quarterly trends comprehensively")
        assert model == "claude-opus-4-8"

    def test_routes_compare_to_opus(self):
        model = self.router.route("compare and evaluate the detailed research findings")
        assert model == "claude-opus-4-8"

    def test_routes_medium_to_sonnet(self):
        # 25 words, no low/high keywords → medium → sonnet
        model = self.router.route("please review this insurance claim " * 5)
        assert model == "claude-sonnet-4-6"

    def test_long_input_routes_to_opus(self):
        long_task = "process this insurance claim request " * 51  # >200 words
        model = self.router.route(long_task)
        assert model == "claude-opus-4-8"

    def test_short_input_routes_to_haiku(self):
        model = self.router.route("ok thanks yes")
        assert model == "claude-haiku-4-5-20251001"

    def test_explicit_complexity_override(self):
        assert self.router.route("analyze everything", complexity="low") == "claude-haiku-4-5-20251001"
        assert self.router.route("hello", complexity="high") == "claude-opus-4-8"
        assert self.router.route("hello", complexity="medium") == "claude-sonnet-4-6"

    def test_track_usage_accumulates(self):
        self.router.track_usage("claude-haiku-4-5-20251001", 100)
        self.router.track_usage("claude-haiku-4-5-20251001", 200)
        report = self.router.get_cost_report()
        assert report["claude-haiku-4-5-20251001"]["calls"] == 2
        assert report["claude-haiku-4-5-20251001"]["tokens"] == 300

    def test_cost_report_structure(self):
        self.router.track_usage("claude-sonnet-4-6", 500)
        report = self.router.get_cost_report()
        assert "claude-sonnet-4-6" in report
        entry = report["claude-sonnet-4-6"]
        assert "calls" in entry
        assert "tokens" in entry
        assert "cost_usd" in entry
        assert entry["cost_usd"] > 0

    # ── multi-provider routing ─────────────────────────────────────────────

    def test_route_with_provider_anthropic_low(self):
        provider, model = self.router.route_with_provider("hello", provider="anthropic")
        assert provider == "anthropic"
        assert model == "claude-haiku-4-5-20251001"

    def test_route_with_provider_anthropic_high(self):
        provider, model = self.router.route_with_provider(
            "analyze and synthesize", provider="anthropic"
        )
        assert provider == "anthropic"
        assert model == "claude-opus-4-8"

    def test_route_with_provider_openai_low(self):
        provider, model = self.router.route_with_provider("hello", provider="openai")
        assert provider == "openai"
        assert model == "gpt-4o-mini"

    def test_route_with_provider_openai_high(self):
        provider, model = self.router.route_with_provider(
            "analyze and synthesize", provider="openai"
        )
        assert provider == "openai"
        assert model == "gpt-4o"

    def test_route_with_provider_google_low(self):
        provider, model = self.router.route_with_provider("hello", provider="google")
        assert provider == "google"
        assert model == "gemini-1.5-flash"

    def test_route_with_provider_google_high(self):
        provider, model = self.router.route_with_provider(
            "analyze and synthesize", provider="google"
        )
        assert provider == "google"
        assert model == "gemini-1.5-pro"

    def test_route_with_provider_unknown_falls_back_to_anthropic_models(self):
        provider, model = self.router.route_with_provider("hello", provider="unknown")
        assert provider == "unknown"
        assert "claude" in model

    def test_openai_model_cost_tracked(self):
        self.router.track_usage("gpt-4o-mini", 1000)
        report = self.router.get_cost_report()
        assert report["gpt-4o-mini"]["cost_usd"] > 0

    def test_google_model_cost_tracked(self):
        self.router.track_usage("gemini-1.5-pro", 1000)
        report = self.router.get_cost_report()
        assert report["gemini-1.5-pro"]["cost_usd"] > 0
