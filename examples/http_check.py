#!/usr/bin/env python3
"""Example client for the faultydata action: stdlib urllib only.

Prints FD_OUTCOME=<outcome> for the exhibit at $FD_URL, the way fd expects.
Copy this into your repo, point it at YOUR http client code instead, and
wire it into .github/workflows/faultydata.yml.
"""
import json
import os
import sys
import urllib.request
import urllib.error

url = os.environ["FD_URL"]
outcome = "ok"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        status = r.status
        print(f"FD_STATUS={status}")
        if status >= 400:
            outcome = "status_error"
        elif status not in (204, 304):
            json.loads(r.read().decode("utf-8", "replace"))
except urllib.error.HTTPError as e:
    print(f"FD_STATUS={e.code}")
    outcome = "status_error"
except TimeoutError:
    outcome = "timeout"
except json.JSONDecodeError as e:
    print(f"FD_DETAIL={e}")
    outcome = "parse_error"
except Exception as e:
    print(f"FD_DETAIL={type(e).__name__}: {e}")
    outcome = "connection_error"
print(f"FD_OUTCOME={outcome}")
