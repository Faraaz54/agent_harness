---
description: Generate or refresh the post-run teach-me Markdown and HTML reports without running an interactive teaching session.
---

# /teach-report

Run:

```bash
python -B scripts/teach_me_report.py
```

Use this when the human wants the visual post-run report but does not want the interactive mastery session yet.

After the command finishes, report the generated paths:

- `docs/teach-me-reports/<run-id>/teach-me.json`
- `docs/teach-me-reports/<run-id>/teach-me.md`
- `docs/teach-me-reports/<run-id>/teach-me.html`
- `docs/learning/<run-id>-teach-me-checklist.md`
