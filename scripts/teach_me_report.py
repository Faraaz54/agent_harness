#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from harnesslib import HarnessError, current_branch, current_head, load_json, repository_root, utc_now, write_json

STATUS_ORDER = {
    "passed": 0,
    "implemented": 1,
    "in_progress": 2,
    "changes_requested": 3,
    "blocked": 4,
    "deferred": 5,
    "pending": 6,
}

CHECKLIST_SECTIONS = [
    ("problem", "Problem and why it existed"),
    ("intent", "Intent, goal and constraints"),
    ("expectations", "Expectations and done/not-done boundary"),
    ("context", "Context and available environment"),
    ("tasks", "Tasks completed and task status"),
    ("solution", "Solution design and implementation flow"),
    ("decisions", "Design decisions and alternatives"),
    ("edge_cases", "Edge cases and failure modes"),
    ("validation", "Tests, reviews and validation evidence"),
    ("impact", "Impact and broader project meaning"),
    ("current_status", "Current status, blockers, deferred work and next steps"),
]


def read_text(path: Path, limit: int = 12000) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit]


def manifest_artifact(manifest: dict[str, Any], kind: str) -> str | None:
    for artifact in manifest.get("source_artifacts", []):
        if artifact.get("kind") == kind:
            return artifact.get("path")
    return None


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return load_json(path)
    except Exception:
        return {"_unreadable": str(path)}


def collect_glob_json(repo: Path, pattern: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(repo.glob(pattern)):
        if path.is_file():
            obj = load_optional_json(path)
            obj["_path"] = str(path.relative_to(repo))
            items.append(obj)
    return items


def load_task_contract_map(repo: Path, task_contract_path: str | None) -> dict[str, dict[str, Any]]:
    if not task_contract_path:
        return {}
    obj = load_optional_json(repo / task_contract_path)
    tasks = obj.get("tasks", []) if isinstance(obj, dict) else []
    return {str(task.get("task_id")): task for task in tasks if task.get("task_id")}


def summarize_test_expectations(test_expectations: dict[str, Any] | None) -> dict[str, Any]:
    tiers = ["unit", "integration", "local_e2e", "cloud_e2e"]
    if not isinstance(test_expectations, dict):
        return {
            "available": False,
            "highest_required_tier": "unknown",
            "required_tiers": [],
            "missing_tiers": tiers,
            "tiers": {tier: {"required": None, "summary": "missing"} for tier in tiers},
        }
    result = {
        "available": True,
        "highest_required_tier": test_expectations.get("highest_required_tier") or "unknown",
        "tier_rationale": test_expectations.get("tier_rationale") or "",
        "required_tiers": [],
        "missing_tiers": [],
        "tiers": {},
    }
    for tier in tiers:
        obj = test_expectations.get(tier)
        if not isinstance(obj, dict):
            result["missing_tiers"].append(tier)
            result["tiers"][tier] = {"required": None, "summary": "missing"}
            continue
        required = obj.get("required") is True
        if required:
            result["required_tiers"].append(tier)
            summary = "; ".join(str(x) for x in obj.get("what_to_test", [])[:3]) or "required but unspecified"
        else:
            summary = obj.get("not_required_reason") or "not required; no reason recorded"
        result["tiers"][tier] = {
            "required": required,
            "summary": summary,
            "evidence_required": obj.get("evidence_required", []),
        }
    return result


def build_testing_coverage(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = ["unit", "integration", "local_e2e", "cloud_e2e"]
    coverage = {tier: {"required": 0, "not_required": 0, "missing": 0} for tier in tiers}
    missing_contracts = []
    for task in tasks:
        summary = task.get("test_expectations_summary", {})
        if not summary.get("available"):
            missing_contracts.append(task.get("task_id"))
        for tier in tiers:
            status = summary.get("tiers", {}).get(tier, {}).get("required")
            if status is True:
                coverage[tier]["required"] += 1
            elif status is False:
                coverage[tier]["not_required"] += 1
            else:
                coverage[tier]["missing"] += 1
    return {"tiers": coverage, "missing_contract_tasks": missing_contracts}


def task_summary(task: dict[str, Any], contract_task: dict[str, Any] | None = None) -> dict[str, Any]:
    reviews = task.get("reviews", {}) or {}
    test_expectations = (contract_task or {}).get("test_expectations") or task.get("test_expectations")
    return {
        "task_id": task.get("task_id"),
        "status": task.get("status"),
        "commit_sha": (task.get("implementation", {}) or {}).get("commit_sha"),
        "files_changed": (task.get("implementation", {}) or {}).get("files_changed", []),
        "verification_status": (task.get("verification", {}) or {}).get("status"),
        "reviews": {name: data.get("status") for name, data in reviews.items()},
        "domain_review": (task.get("domain_review", {}) or {}).get("status"),
        "validator": (task.get("validator", {}) or {}).get("status"),
        "blockers": task.get("blockers", []),
        "test_expectations_summary": summarize_test_expectations(test_expectations),
    }


def extract_goal(intent_text: str) -> str:
    lines = intent_text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## goal"):
            chunk = []
            for nxt in lines[idx + 1 :]:
                if nxt.startswith("## "):
                    break
                if nxt.strip():
                    chunk.append(nxt.strip())
            return " ".join(chunk)[:500]
    return "Goal not detected from intent file."


def infer_learning_status(checklist_path: Path) -> str:
    if not checklist_path.is_file():
        return "LEARNING_PENDING"
    text = checklist_path.read_text(encoding="utf-8", errors="replace")
    if "[ ]" in text or "[~]" in text:
        return "LEARNING_IN_PROGRESS"
    if "[x]" in text.lower():
        return "LEARNING_COMPLETE"
    return "LEARNING_PENDING"


def build_checklist(model: dict[str, Any], existing: str = "") -> str:
    run_id = model["run_id"]
    lines = [
        f"# Teach-Me Checklist — {run_id}",
        "",
        f"Generated: `{model['generated_at']}`",
        "",
        "Use `[x]` for mastered, `[~]` for partial, `[ ]` for not yet demonstrated.",
        "",
    ]
    for key, title in CHECKLIST_SECTIONS:
        lines += [f"## {title}", "", "- [ ] Human can restate the core idea without reading the report."]
        if key == "tasks":
            for task in model.get("tasks", []):
                lines.append(f"- [ ] Human can explain task `{task['task_id']}` and why its status is `{task['status']}`.")
        elif key == "validation":
            lines += [
                "- [ ] Human can explain which tests/reviews/validators ran.",
                "- [ ] Human can explain what evidence proves the work and what evidence is still missing.",
            ]
        elif key == "current_status":
            lines += [
                "- [ ] Human can explain completed, blocked, deferred and pending work.",
                "- [ ] Human can explain the next safest action.",
            ]
        else:
            lines.append(f"- [ ] Human can explain the {title.lower()}.")
        lines.append("")
    lines += [
        "## Restatement log",
        "",
        "- Date/time:",
        "- Human restatement:",
        "- Gaps found:",
        "- Explanation given:",
        "",
        "## Quiz log",
        "",
        "- Questions asked:",
        "- Answers given:",
        "- Corrections needed:",
        "",
        "## Learning verdict",
        "",
        "Status: `LEARNING_PENDING`",
        "",
    ]
    if existing.strip():
        lines += ["---", "", "## Previous checklist content", "", existing]
    return "\n".join(lines)


def markdown_report(model: dict[str, Any]) -> str:
    lines = [
        f"# Teach-Me Report — {model['run_id']}",
        "",
        f"Generated: `{model['generated_at']}`",
        f"Branch: `{model.get('branch')}`",
        f"Head: `{str(model.get('head') or '')[:12]}`",
        f"Learning status: `{model.get('learning_status')}`",
        "",
        "## Mental model",
        "",
        "```text",
        "Intent → Context → Expectations → Task contracts → Build loop → Reviews → Validation → Commit → Reports → Teach-me",
        "```",
        "",
        "## Goal",
        "",
        model.get("goal") or "Goal not available.",
        "",
        "## Run status",
        "",
        f"- Engineering status: `{model.get('engineering_status')}`",
        f"- Current stage: `{model.get('current_stage')}`",
        f"- Completed tasks: `{model.get('counts', {}).get('passed', 0)}`",
        f"- Blocked tasks: `{model.get('counts', {}).get('blocked', 0)}`",
        f"- Deferred tasks: `{model.get('counts', {}).get('deferred', 0)}`",
        f"- Pending/in-progress tasks: `{model.get('counts', {}).get('active_or_pending', 0)}`",
        "",
        "## Task outcomes",
        "",
        "| Task | Status | Commit | Verification | Validator | Domain review |",
        "|---|---|---|---|---|---|",
    ]
    for task in model.get("tasks", []):
        lines.append(
            f"| `{task['task_id']}` | `{task['status']}` | `{str(task.get('commit_sha') or 'none')[:12]}` | `{task.get('verification_status') or 'unknown'}` | `{task.get('validator') or 'unknown'}` | `{task.get('domain_review') or 'unknown'}` |"
        )
    lines += [
        "",
        "## What was achieved",
        "",
    ]
    passed = [t for t in model.get("tasks", []) if t.get("status") == "passed"]
    if passed:
        for task in passed:
            lines.append(f"- `{task['task_id']}` reached `passed` and has commit `{str(task.get('commit_sha') or 'none')[:12]}`.")
    else:
        lines.append("- No task is recorded as `passed` yet.")
    lines += [
        "",
        "## Testing hierarchy coverage",
        "",
        "| Tier | Required by tasks | Explicitly not required | Missing declaration |",
        "|---|---:|---:|---:|",
    ]
    for tier, counts in model.get("testing_coverage", {}).get("tiers", {}).items():
        lines.append(f"| `{tier}` | {counts.get('required', 0)} | {counts.get('not_required', 0)} | {counts.get('missing', 0)} |")
    missing = model.get("testing_coverage", {}).get("missing_contract_tasks", [])
    if missing:
        lines += ["", "Tasks missing machine-readable `test_expectations`: " + ", ".join(f"`{t}`" for t in missing)]
    lines += [
        "",
        "## Evidence map",
        "",
        "| Evidence type | Count |",
        "|---|---:|",
    ]
    for key in ["implementation_results", "review_results", "validation_results", "session_reports", "pull_request_packages"]:
        lines.append(f"| {key.replace('_', ' ').title()} | {len(model.get(key, []))} |")
    lines += [
        "",
        "## Teaching checklist",
        "",
        f"Checklist: `{model['paths']['checklist']}`",
        "",
        "The teacher agent should ask the human to restate understanding first, then teach and quiz by checklist stage.",
        "",
        "## Current status answer",
        "",
        current_status_answer(model),
        "",
        "## Report files",
        "",
        f"- JSON: `{model['paths']['json']}`",
        f"- Markdown: `{model['paths']['markdown']}`",
        f"- HTML: `{model['paths']['html']}`",
        f"- Checklist: `{model['paths']['checklist']}`",
    ]
    return "\n".join(lines) + "\n"


def current_status_answer(model: dict[str, Any]) -> str:
    counts = model.get("counts", {})
    status = model.get("engineering_status") or "unknown"
    parts = [f"The run is currently `{status}` at stage `{model.get('current_stage')}`."]
    parts.append(f"Tasks passed: {counts.get('passed', 0)}; blocked: {counts.get('blocked', 0)}; deferred: {counts.get('deferred', 0)}; active or pending: {counts.get('active_or_pending', 0)}.")
    if model.get("blocked_tasks"):
        parts.append("Blocked tasks: " + ", ".join(model["blocked_tasks"]) + ".")
    if model.get("deferred_tasks"):
        parts.append("Deferred tasks: " + ", ".join(model["deferred_tasks"]) + ".")
    if counts.get("active_or_pending", 0):
        parts.append("Next: continue the build loop or inspect blockers before claiming completion.")
    else:
        parts.append("Next: run `/teach-me` to close learning, or prepare delivery if engineering closure is complete.")
    return " ".join(parts)


def badge(status: str | None) -> str:
    s = (status or "unknown").lower()
    cls = "ok" if s in {"passed", "pass", "closed", "local_delivery_complete"} else "warn" if s in {"pending", "in_progress", "implemented", "deferred", "learning_pending"} else "bad" if s in {"blocked", "changes_requested", "rejected", "fail", "not_closable"} else "neutral"
    return f"<span class='badge {cls}'>{html.escape(status or 'unknown')}</span>"


def html_report(model: dict[str, Any]) -> str:
    task_cards = []
    for task in model.get("tasks", []):
        files = "".join(f"<li><code>{html.escape(str(f))}</code></li>" for f in task.get("files_changed", [])[:8]) or "<li>No changed files recorded</li>"
        task_cards.append(
            f"""
            <article class='card'>
              <div class='card-head'><h3>{html.escape(task['task_id'])}</h3>{badge(task.get('status'))}</div>
              <dl>
                <dt>Commit</dt><dd><code>{html.escape(str(task.get('commit_sha') or 'none')[:12])}</code></dd>
                <dt>Verification</dt><dd>{badge(task.get('verification_status'))}</dd>
                <dt>Validator</dt><dd>{badge(task.get('validator'))}</dd>
                <dt>Domain review</dt><dd>{badge(task.get('domain_review'))}</dd>
              </dl>
              <p><strong>Highest test tier:</strong> <code>{html.escape(str(task.get('test_expectations_summary', {}).get('highest_required_tier', 'unknown')))}</code></p>
              <details><summary>Test expectations</summary><ul>{''.join(f"<li><strong>{html.escape(tier)}</strong>: {html.escape(str(info.get('summary')))}</li>" for tier, info in task.get('test_expectations_summary', {}).get('tiers', {}).items()) or '<li>No test expectations recorded</li>'}</ul></details>
              <details><summary>Files changed</summary><ul>{files}</ul></details>
            </article>
            """
        )
    evidence_items = "".join(
        f"<li><strong>{html.escape(key.replace('_',' ').title())}</strong>: {len(model.get(key, []))}</li>"
        for key in ["implementation_results", "review_results", "validation_results", "session_reports", "pull_request_packages"]
    )
    checklist_items = "".join(f"<li>{html.escape(title)}</li>" for _, title in CHECKLIST_SECTIONS)
    goal = html.escape(model.get("goal") or "Goal not available")
    current = html.escape(current_status_answer(model))
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Teach-Me Report — {html.escape(model['run_id'])}</title>
<style>
:root {{ --bg:#f7f7f8; --panel:#ffffff; --ink:#1f2937; --muted:#667085; --line:#e5e7eb; --ok:#067647; --warn:#b54708; --bad:#b42318; --neutral:#475467; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height:1.5; }}
header {{ background:#111827; color:white; padding:2rem; }}
main {{ max-width:1180px; margin:0 auto; padding:2rem; }}
section {{ margin:1.5rem 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:1rem; box-shadow:0 1px 2px rgba(16,24,40,.04); }}
.card-head {{ display:flex; justify-content:space-between; align-items:center; gap:1rem; }}
.card h3 {{ margin:.2rem 0; }}
.kpi {{ font-size:2rem; font-weight:700; }}
.muted {{ color:var(--muted); }}
.badge {{ display:inline-block; border-radius:999px; padding:.2rem .55rem; font-size:.8rem; font-weight:650; background:#eef2f6; color:var(--neutral); }}
.badge.ok {{ background:#ecfdf3; color:var(--ok); }} .badge.warn {{ background:#fffaeb; color:var(--warn); }} .badge.bad {{ background:#fef3f2; color:var(--bad); }}
.timeline {{ border-left:3px solid var(--line); padding-left:1rem; }}
.timeline li {{ margin:.75rem 0; }}
code {{ background:#f2f4f7; padding:.12rem .3rem; border-radius:4px; }}
dl {{ display:grid; grid-template-columns:110px 1fr; gap:.25rem .6rem; }} dt {{ color:var(--muted); }} dd {{ margin:0; }}
table {{ width:100%; border-collapse:collapse; }} th, td {{ text-align:left; padding:.5rem; border-bottom:1px solid var(--line); }} th {{ color:var(--muted); }}
.print-note {{ border:1px dashed var(--line); background:white; padding:1rem; border-radius:12px; }}
@media print {{ body {{ background:white; }} header {{ background:white; color:black; border-bottom:1px solid #ddd; }} .card {{ box-shadow:none; }} }}
</style>
</head>
<body>
<header>
  <h1>Teach-Me Report — {html.escape(model['run_id'])}</h1>
  <p>Generated {html.escape(model['generated_at'])} · Branch <code>{html.escape(str(model.get('branch')))}</code> · Head <code>{html.escape(str(model.get('head') or '')[:12])}</code></p>
</header>
<main>
  <section class='grid'>
    <div class='card'><div class='muted'>Engineering status</div><div>{badge(model.get('engineering_status'))}</div></div>
    <div class='card'><div class='muted'>Learning status</div><div>{badge(model.get('learning_status'))}</div></div>
    <div class='card'><div class='muted'>Passed tasks</div><div class='kpi'>{model.get('counts',{}).get('passed',0)}</div></div>
    <div class='card'><div class='muted'>Blocked/deferred</div><div class='kpi'>{model.get('counts',{}).get('blocked',0)} / {model.get('counts',{}).get('deferred',0)}</div></div>
  </section>

  <section class='card'>
    <h2>Goal</h2>
    <p>{goal}</p>
  </section>

  <section class='card'>
    <h2>Mental model</h2>
    <ol class='timeline'>
      <li><strong>Intent</strong>: the human-owned outcome and constraints.</li>
      <li><strong>Context</strong>: repository, environment, conventions and project-pack knowledge.</li>
      <li><strong>Expectations</strong>: what counts as done and what counts as failure.</li>
      <li><strong>Task contracts</strong>: executable slices generated from the intent/context/expectations.</li>
      <li><strong>Build loop</strong>: implementation, postflight, review, validation and commit.</li>
      <li><strong>Teach-me</strong>: post-run understanding, report and mastery checklist.</li>
    </ol>
  </section>

  <section>
    <h2>Task outcomes</h2>
    <div class='grid'>{''.join(task_cards) or '<p>No tasks found.</p>'}</div>
  </section>

  <section class='card'>
    <h2>Testing hierarchy coverage</h2>
    <table>
      <thead><tr><th>Tier</th><th>Required by tasks</th><th>Explicitly not required</th><th>Missing declaration</th></tr></thead>
      <tbody>{''.join(f"<tr><td><code>{html.escape(tier)}</code></td><td>{counts.get('required',0)}</td><td>{counts.get('not_required',0)}</td><td>{counts.get('missing',0)}</td></tr>" for tier, counts in model.get('testing_coverage', {}).get('tiers', {}).items())}</tbody>
    </table>
  </section>

  <section class='grid'>
    <div class='card'><h2>Evidence map</h2><ul>{evidence_items}</ul></div>
    <div class='card'><h2>Teaching checklist</h2><ul>{checklist_items}</ul></div>
  </section>

  <section class='card'>
    <h2>Current status answer</h2>
    <p>{current}</p>
  </section>

  <section class='print-note'>
    <h2>How to use this report</h2>
    <p>Use this report to brief yourself or others. Then run <code>/teach-me</code> for an interactive mastery session. The teacher should ask for your restatement first, fill gaps, quiz you, and update the checklist.</p>
    <p>Checklist: <code>{html.escape(model['paths']['checklist'])}</code></p>
  </section>
</main>
</body>
</html>"""


def build_model(repo: Path, run_id_arg: str | None) -> dict[str, Any]:
    features = load_json(repo / "tasks/feature_list.json")
    run_id = run_id_arg or features.get("run_id")
    if not run_id:
        raise HarnessError("Cannot determine run_id from --run-id or tasks/feature_list.json")
    state = load_optional_json(repo / "tasks/run_state.json")
    manifest = load_optional_json(repo / "tasks/run_manifest.json")
    intent_path = manifest_artifact(manifest, "intent")
    context_path = manifest_artifact(manifest, "context")
    expectations_path = manifest_artifact(manifest, "expectations")
    task_contract_path = manifest_artifact(manifest, "task_contracts")
    intent_text = read_text(repo / intent_path) if intent_path else ""
    checklist_path = repo / "docs" / "learning" / f"{run_id}-teach-me-checklist.md"
    contract_map = load_task_contract_map(repo, task_contract_path)
    tasks = [task_summary(t, contract_map.get(str(t.get("task_id")))) for t in features.get("tasks", [])]
    counts = {
        "passed": sum(1 for t in tasks if t.get("status") == "passed"),
        "blocked": sum(1 for t in tasks if t.get("status") == "blocked"),
        "deferred": sum(1 for t in tasks if t.get("status") == "deferred"),
        "active_or_pending": sum(1 for t in tasks if t.get("status") not in {"passed", "blocked", "deferred"}),
    }
    outdir = repo / "docs" / "teach-me-reports" / run_id
    paths = {
        "json": str((outdir / "teach-me.json").relative_to(repo)),
        "markdown": str((outdir / "teach-me.md").relative_to(repo)),
        "html": str((outdir / "teach-me.html").relative_to(repo)),
        "checklist": str(checklist_path.relative_to(repo)),
    }
    model = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "branch": current_branch(repo),
        "head": current_head(repo),
        "goal": extract_goal(intent_text),
        "engineering_status": (state.get("closure", {}).get("engineering", {}) or {}).get("verdict") or state.get("status") or "unknown",
        "current_stage": state.get("current_stage") or "unknown",
        "learning_status": infer_learning_status(checklist_path),
        "counts": counts,
        "blocked_tasks": [t["task_id"] for t in tasks if t.get("status") == "blocked"],
        "deferred_tasks": [t["task_id"] for t in tasks if t.get("status") == "deferred"],
        "tasks": sorted(tasks, key=lambda t: (STATUS_ORDER.get(str(t.get("status")), 99), str(t.get("task_id")))),
        "testing_coverage": build_testing_coverage(tasks),
        "idsd_artifacts": {
            "intent": intent_path,
            "context": context_path,
            "expectations": expectations_path,
            "task_contracts": task_contract_path,
        },
        "implementation_results": collect_glob_json(repo, "docs/implementation-results/**/*.json") + collect_glob_json(repo, "docs/implementation-results/*.json"),
        "review_results": collect_glob_json(repo, "docs/reviews/**/*.json"),
        "validation_results": collect_glob_json(repo, "docs/validation-results/**/*.json") + collect_glob_json(repo, "docs/validation-results/*.json"),
        "session_reports": collect_glob_json(repo, f"docs/session-reports/{run_id}/*.json"),
        "pull_request_packages": collect_glob_json(repo, f"docs/pull-requests/{run_id}.json"),
        "paths": paths,
    }
    return model


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate post-run teach-me JSON, Markdown, HTML, and mastery checklist artifacts.")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--check", action="store_true", help="Check that teach-me artifacts exist for the current or provided run.")
    args = parser.parse_args()
    repo = repository_root()
    features = load_json(repo / "tasks/feature_list.json")
    run_id = args.run_id or features.get("run_id")
    if not run_id:
        raise HarnessError("Cannot determine run_id")
    outdir = repo / "docs" / "teach-me-reports" / run_id
    checklist_path = repo / "docs" / "learning" / f"{run_id}-teach-me-checklist.md"
    if args.check:
        required = [outdir / "teach-me.json", outdir / "teach-me.md", outdir / "teach-me.html", checklist_path]
        missing = [str(p.relative_to(repo)) for p in required if not p.is_file()]
        if missing:
            print(json.dumps({"verdict": "FAIL", "missing": missing}, indent=2))
            return 1
        print(json.dumps({"verdict": "PASS", "run_id": run_id}, indent=2))
        return 0
    model = build_model(repo, args.run_id)
    outdir.mkdir(parents=True, exist_ok=True)
    existing_checklist = read_text(checklist_path, limit=50000)
    write_json(outdir / "teach-me.json", model)
    (outdir / "teach-me.md").write_text(markdown_report(model), encoding="utf-8")
    (outdir / "teach-me.html").write_text(html_report(model), encoding="utf-8")
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    if not checklist_path.exists():
        checklist_path.write_text(build_checklist(model), encoding="utf-8")
    elif existing_checklist and "# Teach-Me Checklist" not in existing_checklist[:200]:
        checklist_path.write_text(build_checklist(model, existing_checklist), encoding="utf-8")
    print(json.dumps({"verdict": "PASS", "run_id": model["run_id"], "paths": model["paths"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
