from __future__ import annotations

import argparse
import html
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio


def percentile(values: list[float], percent: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percent / 100 * len(ordered)) - 1)
    return ordered[index]


def load_recent_records(log_path: Path, window_minutes: int) -> list[dict]:
    if not log_path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    records = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
        if timestamp >= cutoff:
            records.append(record)
    return records


def render_dashboard(config_path: Path, log_path: Path) -> str:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))["dashboard"]
    records = load_recent_records(log_path, config["time_range_minutes"])
    responses = [row for row in records if row.get("event") == "response_sent"]
    requests = [row for row in records if row.get("event") == "request_received"]
    failures = [row for row in records if row.get("event") == "request_failed"]
    tool_results = [row for row in records if row.get("tool_success") is not None]
    successes = [row for row in tool_results if row.get("tool_success") is True]

    def nums(rows: list[dict], field: str) -> list[float]:
        return [float(row[field]) for row in rows if isinstance(row.get(field), (int, float))]

    def show(value: float | None, unit: str = "") -> str:
        return "—" if value is None else f"{value:,.2f}{unit}"

    error_rate = (len(failures) / len(requests) * 100) if requests else None
    retrieval_rate = (len(successes) / len(tool_results) * 100) if tool_results else None
    window = config["time_range_minutes"]
    cards = [
        (
            "Latency percentiles and TTFT",
            [
                ("P50", show(percentile(nums(responses, "latency_ms"), 50), " ms")),
                ("P95", show(percentile(nums(responses, "latency_ms"), 95), " ms")),
                ("P99", show(percentile(nums(responses, "latency_ms"), 99), " ms")),
                ("TTFT P95", show(percentile(nums(responses, "ttft_ms"), 95), " ms")),
            ],
            "P95 ≤ 3,000 ms",
        ),
        (
            "Request traffic",
            [("Requests", str(len(requests))), ("Rate", show(len(requests) / window, " req/min"))],
            "Rate ≥ 1 req/min",
        ),
        (
            "Error rate and retrieval success",
            [("Error rate", show(error_rate, "%")), ("Retrieval success", show(retrieval_rate, "%"))],
            "Errors ≤ 2%; retrieval ≥ 90%",
        ),
        (
            "Cost over time",
            [("Total", show(sum(nums(responses, "cost_usd")), " USD")), ("Responses", str(len(responses)))],
            "Total ≤ 2.50 USD",
        ),
        (
            "Input and output tokens",
            [("Input", show(sum(nums(responses, "tokens_in")))), ("Output", show(sum(nums(responses, "tokens_out"))))],
            "Total ≤ 50,000 tokens",
        ),
        (
            "Quality proxy",
            [("Mean", show(sum(nums(responses, "quality_score")) / len(nums(responses, "quality_score")) if nums(responses, "quality_score") else None, " / 1"))],
            "Mean ≥ 0.75",
        ),
    ]
    panels = "\n".join(
        "<section class='panel'><h2>{}</h2><div class='metrics'>{}</div><p class='threshold'>{}</p></section>".format(
            html.escape(title),
            "".join(
                "<div class='metric'><span>{}</span><strong>{}</strong></div>".format(
                    html.escape(label), html.escape(value)
                )
                for label, value in values
            ),
            html.escape(threshold),
        )
        for title, values, threshold in cards
    )
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{html.escape(config['title'])}</title>
<style>
body{{margin:0;background:#0b1220;color:#e7edf7;font:15px system-ui,sans-serif}}
main{{max-width:1180px;margin:40px auto;padding:0 24px}}header{{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:24px}}
h1{{font-size:28px;margin:0 0 8px}}.meta{{color:#9aabc4}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}
.panel{{background:#131e30;border:1px solid #253550;border-radius:12px;padding:20px;min-height:150px}}h2{{font-size:17px;margin:0 0 18px}}
.metrics{{display:flex;flex-wrap:wrap;gap:20px}}.metric{{display:grid;gap:5px}}.metric span,.threshold{{font-size:12px;color:#9aabc4}}.metric strong{{font-size:22px}}
.threshold{{border-top:1px solid #253550;padding-top:12px;margin:20px 0 0}}@media(max-width:700px){{header{{display:block}}.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><header><div><h1>{html.escape(config['title'])}</h1><div class="meta">Last {window} minutes · source: {html.escape(str(log_path))} · refresh target: {config['refresh_seconds']}s</div></div><div class="meta">Snapshot: {generated}</div></header>
<div class="grid">{panels}</div></main></body></html>"""


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Tạo snapshot dashboard từ structured JSONL logs")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "config" / "dashboard.yaml")
    parser.add_argument("--logs", type=Path, default=REPO_ROOT / "data" / "logs.jsonl")
    parser.add_argument(
        "--output", type=Path, default=REPO_ROOT / "submission" / "evidence" / "11-dashboard-overview.html"
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_dashboard(args.config, args.logs), encoding="utf-8")
    print(f"Dashboard snapshot written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
