#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from harnesslib import (
    HarnessError,
    git_runtime_dir,
    load_json,
    repository_root,
    utc_now,
    validate_json_schema,
    write_json,
)
from build_orchestrator import next_action

TERMINAL_OR_BLOCKING = {"BLOCKED", "REQUIRES_HUMAN_DECISION", "COMPLETE", "FINALIZE_SESSION"}
AGENT_ACTIONS = {"IMPLEMENT_TASK", "REPAIR_TASK", "RUN_REVIEW", "RUN_DOMAIN_REVIEW", "RUN_VALIDATOR"}
COMMAND_ACTIONS = {"RUN_PREFLIGHT", "RUN_POSTFLIGHT", "COMMIT_TASK", "FINALIZE_SESSION"}

ACTION_GUIDANCE: dict[str, dict[str, Any]] = {
    "RUN_PREFLIGHT": {
        "summary": "Run preflight before any implementation work.",
        "record_result": False,
        "stop_after": True,
    },
    "IMPLEMENT_TASK": {
        "summary": "Delegate the task context packet to build-agent and require structured implementation JSON.",
        "record_result": True,
        "stop_after": False,
    },
    "REPAIR_TASK": {
        "summary": "Delegate the repair packet to build-agent and require structured implementation JSON.",
        "record_result": True,
        "stop_after": False,
    },
    "RUN_POSTFLIGHT": {
        "summary": "Run deterministic postflight and record the postflight JSON result.",
        "record_result": True,
        "stop_after": False,
    },
    "RUN_REVIEW": {
        "summary": "Delegate to the required reviewer and require structured review JSON.",
        "record_result": True,
        "stop_after": False,
    },
    "RUN_DOMAIN_REVIEW": {
        "summary": "Delegate to the domain reviewer and require structured domain-review JSON.",
        "record_result": True,
        "stop_after": False,
    },
    "RUN_VALIDATOR": {
        "summary": "Delegate to validator-agent and require structured task-validation JSON.",
        "record_result": True,
        "stop_after": False,
    },
    "COMMIT_TASK": {
        "summary": "Run governed commit and record docs/commit-results/<task-id>.json.",
        "record_result": True,
        "stop_after": True,
    },
    "FINALIZE_SESSION": {
        "summary": "No task remains. Stop build-next/build-auto and run /finalize-session explicitly if desired.",
        "record_result": False,
        "stop_after": True,
    },
    "BLOCKED": {
        "summary": "The run is blocked. Stop and resolve the blocker.",
        "record_result": False,
        "stop_after": True,
    },
    "REQUIRES_HUMAN_DECISION": {
        "summary": "The run requires a human decision. Stop and document the decision before resuming.",
        "record_result": False,
        "stop_after": True,
    },
    "COMPLETE": {
        "summary": "The run is complete. Stop.",
        "record_result": False,
        "stop_after": True,
    },
}


def _load_run_id(repo: Path) -> str:
    manifest = load_json(repo / "tasks/run_manifest.json")
    return manifest["run_id"]


def _driver_dir(repo: Path, run_id: str) -> Path:
    p = git_runtime_dir(repo) / "runs" / run_id / "driver"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _validate_action(repo: Path, action: dict[str, Any]) -> None:
    action_path = action.get("action_path")
    if action_path:
        # The action path can be absolute inside .git/agent-harness; validate it directly.
        validate_json_schema(Path(action_path), repo / "schemas/orchestrator-action.schema.json")


def _next_steps(action: dict[str, Any], mode: str) -> list[str]:
    name = action.get("action")
    steps: list[str] = []
    if name in COMMAND_ACTIONS and action.get("command"):
        steps.append(f"Run: {action['command']}")
    if name in AGENT_ACTIONS:
        agent = action.get("required_agent")
        context = action.get("context_packet")
        expected = action.get("expected_output")
        if context:
            steps.append(f"Open context packet: {context}")
        steps.append(f"Delegate to agent: {agent}")
        if expected:
            steps.append(f"Agent must write structured output: {expected}")
    if ACTION_GUIDANCE.get(name, {}).get("record_result"):
        expected = action.get("expected_output") or "<RESULT-PATH>"
        steps.append(f"Record result: python -B scripts/build_orchestrator.py record-result --action-id {action['action_id']} --result {expected}")
    if mode == "next":
        steps.append("After the boundary is recorded, stop and inspect build status before running /build-next again.")
    else:
        steps.append("After recording the result, call the driver again to discover the next action; stop on a blocking or terminal boundary.")
    return steps


def begin(mode: str) -> int:
    repo = repository_root()
    run_id = _load_run_id(repo)
    action = next_action(repo)
    _validate_action(repo, action)
    name = action.get("action")
    guidance = ACTION_GUIDANCE.get(name, {"summary": "Execute the returned orchestrator action exactly.", "record_result": True, "stop_after": False})
    receipt = {
        "schema_version": "1.0",
        "verdict": "PASS",
        "mode": "build-next" if mode == "next" else "build-auto",
        "created_at": utc_now(),
        "run_id": run_id,
        "action": action,
        "boundary_policy": {
            "build_next_stops_after_commit_or_blocker": mode == "next",
            "build_auto_continues_until_terminal_or_blocking_boundary": mode == "auto",
            "manual_build_orchestrator_next_required": False,
        },
        "guidance": {
            "summary": guidance.get("summary"),
            "action_kind": "agent" if name in AGENT_ACTIONS else ("command" if name in COMMAND_ACTIONS else "terminal"),
            "record_result_required": bool(guidance.get("record_result")),
            "stop_after_action": bool(guidance.get("stop_after")),
            "next_steps": _next_steps(action, mode),
        },
    }
    out = _driver_dir(repo, run_id) / f"{receipt['mode']}-{utc_now().replace(':', '').replace('+', 'Z')}.json"
    write_json(out, receipt)
    receipt["receipt_path"] = str(out)
    print(json.dumps(receipt, indent=2))
    if name in TERMINAL_OR_BLOCKING:
        return 2 if name in {"BLOCKED", "REQUIRES_HUMAN_DECISION"} else 0
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Discover the next orchestrator action for build-next/build-auto without requiring a manual build_orchestrator.py next call.")
    ap.add_argument("mode", choices=["next", "auto"], help="next = one-task checkpoint mode; auto = continue-until-terminal driver mode")
    args = ap.parse_args()
    try:
        return begin(args.mode)
    except Exception as exc:
        print(json.dumps({"verdict": "FAIL", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
