from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_dashboard import render_dashboard


def test_dashboard_snapshot_renders_all_six_panels_and_thresholds(tmp_path: Path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "ts": now,
            "event": "request_received",
            "service": "api",
            "correlation_id": "req-12345678",
        },
        {
            "ts": now,
            "event": "response_sent",
            "service": "api",
            "latency_ms": 120,
            "ttft_ms": 40,
            "cost_usd": 0.001,
            "tokens_in": 10,
            "tokens_out": 20,
            "quality_score": 0.9,
            "tool_success": True,
        },
    ]
    log_path = tmp_path / "logs.jsonl"
    log_path.write_text(
        "\n".join(json.dumps(record) for record in records), encoding="utf-8"
    )

    dashboard = render_dashboard(
        Path("config/dashboard.yaml"), log_path
    )

    for panel in (
        "Latency percentiles and TTFT",
        "Request traffic",
        "Error rate and retrieval success",
        "Cost over time",
        "Input and output tokens",
        "Quality proxy",
        "P95 ≤ 3,000 ms",
        "Errors ≤ 2%; retrieval ≥ 90%",
    ):
        assert panel in dashboard
