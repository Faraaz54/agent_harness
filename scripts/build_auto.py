#!/usr/bin/env python3
from __future__ import annotations
import sys
from build_driver import main as _driver_main

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "auto"] + sys.argv[1:]
    raise SystemExit(_driver_main())
