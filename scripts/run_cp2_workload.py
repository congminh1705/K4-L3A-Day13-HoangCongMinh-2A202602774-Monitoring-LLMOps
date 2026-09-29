from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

from app.agent import LabAgent
from app.prompt_management import DEFAULT_PROMPT_TEMPLATE
from app.tracing import get_langfuse_client

PROMPT_NAME = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")
PROMPT_V1 = (
    "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\n"
    "Answer using the provided docs. If the docs do not answer the question, say so clearly."
)
PROMPT_V2 = (
    "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\n"
    "Answer in at most three concise sentences. Use the docs and state when information is missing."
)
SHARED_INPUT = "What is the refund policy?"


def get_prompt(client, label: str):
    prompt = client.get_prompt(
        PROMPT_NAME,
        label=label,
        type="text",
        fallback=DEFAULT_PROMPT_TEMPLATE,
        cache_ttl_seconds=0,
        fetch_timeout_seconds=8,
        max_retries=0,
    )
    if getattr(prompt, "is_fallback", False):
        raise LookupError(f"Prompt label '{label}' is not configured")
    return prompt


def ensure_prompt_versions(client) -> tuple[int, int]:
    try:
        baseline = get_prompt(client, "baseline")
    except Exception:
        baseline = client.create_prompt(
            name=PROMPT_NAME,
            type="text",
            prompt=PROMPT_V1,
            labels=["baseline", "production"],
            commit_message="CP2 baseline prompt v1",
        )
    try:
        candidate = get_prompt(client, "candidate")
    except Exception:
        candidate = client.create_prompt(
            name=PROMPT_NAME,
            type="text",
            prompt=PROMPT_V2,
            labels=["candidate"],
            commit_message="CP2 candidate prompt v2: concise response format",
        )
    return int(baseline.version), int(candidate.version)


def run_request(agent: LabAgent, label: str, session_id: str, message: str) -> str:
    os.environ["LANGFUSE_PROMPT_LABEL"] = label
    correlation_id = f"req-{uuid.uuid4().hex[:8]}"
    agent.run(
        user_id="cp2-student",
        feature="qa",
        session_id=session_id,
        message=message,
        correlation_id=correlation_id,
    )
    return correlation_id


def main() -> int:
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        print("Langfuse keys are not configured; CP2 trace workload cannot run.")
        return 1

    client = get_langfuse_client()
    try:
        baseline_version, candidate_version = ensure_prompt_versions(client)

        # Run the exact same input against both labels while production remains on v1.
        baseline_correlation_id = run_request(
            LabAgent(), "baseline", "cp2-baseline", SHARED_INPUT
        )
        candidate_correlation_id = run_request(
            LabAgent(), "candidate", "cp2-candidate", SHARED_INPUT
        )

        # Promote v2 briefly, verify the production label, then roll it back to v1.
        client.update_prompt(
            name=PROMPT_NAME, version=candidate_version, new_labels=["candidate", "production"]
        )
        promoted_version = int(get_prompt(client, "production").version)
        client.update_prompt(
            name=PROMPT_NAME, version=candidate_version, new_labels=["candidate"]
        )
        client.update_prompt(
            name=PROMPT_NAME,
            version=baseline_version,
            new_labels=["baseline", "production"],
        )
        rolled_back_version = int(get_prompt(client, "production").version)

        correlations = [baseline_correlation_id, candidate_correlation_id]
        workload_messages = [
            "What is your refund policy?",
            "Explain why metrics traces and logs work together",
            "Summarize the monitoring policy for production logging",
            "Can I get help with policy and monitoring?",
            "What should be logged for a customer phone number?",
            "Summarize the observability workflow",
            "What should not appear in app logs?",
            "How do I debug tail latency?",
            "What is the policy for payment card information?",
            "How should alerts be designed?",
        ]
        for index, message in enumerate(workload_messages, start=1):
            correlations.append(
                run_request(LabAgent(), "production", f"cp2-workload-{index:02d}", message)
            )
        client.flush()

        print(f"prompt_name={PROMPT_NAME}")
        print(f"baseline_version={baseline_version}; baseline_label=baseline")
        print(f"candidate_version={candidate_version}; candidate_label=candidate")
        print(f"shared_input={SHARED_INPUT}")
        print(f"baseline_correlation_id={baseline_correlation_id}")
        print(f"candidate_correlation_id={candidate_correlation_id}")
        print(f"production_promoted_version={promoted_version}")
        print(f"production_rolled_back_version={rolled_back_version}")
        print(f"additional_traces_requested={len(workload_messages)}")
        print(f"correlation_ids={','.join(correlations)}")
        return 0
    finally:
        client.flush()


if __name__ == "__main__":
    raise SystemExit(main())
