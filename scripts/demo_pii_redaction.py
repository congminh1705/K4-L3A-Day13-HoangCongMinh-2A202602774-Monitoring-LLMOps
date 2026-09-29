from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app.logging_config as logging_config


samples = {
    "email": "test.user@example.invalid",
    "phone_vn": "0901234567",
    "cccd": "001203004567",
    "credit_card": "4111 1111 1111 1111",
}
message = "Synthetic test values: " + "; ".join(
    f"{name}={value}" for name, value in samples.items()
)

with tempfile.TemporaryDirectory(prefix="day13-pii-demo-") as temp_dir:
    log_path = Path(temp_dir) / "demo.jsonl"
    logging_config.LOG_PATH = log_path
    logging_config.configure_logging()
    logging_config.get_logger().info("pii_redaction_demo", payload={"message": message})
    record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])

serialized = json.dumps(record, ensure_ascii=False)
markers = [
    "[REDACTED_EMAIL]",
    "[REDACTED_PHONE_VN]",
    "[REDACTED_CCCD]",
    "[REDACTED_CREDIT_CARD]",
]
assert all(value not in serialized for value in samples.values())
assert all(marker in serialized for marker in markers)

print("PII redaction demo through configured structlog processor")
print("Synthetic input (test-only):")
print(message)
print("JSONL event written to a temporary file (then removed):")
print(json.dumps(record, ensure_ascii=False, indent=2))
print("PASS: all 4 synthetic values were redacted before JSONL write")
