# /rollback-task

Safely roll back an uncommitted task implementation or mark a committed task for human recovery.

Run:

```bash
python -B scripts/rollback_task.py --task-id <TASK_ID>
```

This command is deterministic and must not rewrite history without explicit human authority.
