#!/usr/bin/env python3
from __future__ import annotations
import sys, subprocess
cmd = {'abort_run':'abort','resume_run':'resume','defer_task':'defer','unblock_task':'unblock','rollback_task':'rollback'}['abort_run']
raise SystemExit(subprocess.call([sys.executable, '-B', 'scripts/run_state_ops.py', cmd, *sys.argv[1:]]))
