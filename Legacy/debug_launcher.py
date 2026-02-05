import os
import sys
import subprocess
import time

print(f"DEBUG_LAUNCHER: CWD is {os.getcwd()}")
TARGET_FILE = "app.py"
if os.path.exists(TARGET_FILE):
    print(f"DEBUG_LAUNCHER: {TARGET_FILE} FOUND.")
else:
    print(f"DEBUG_LAUNCHER: {TARGET_FILE} NOT FOUND!")
    files = os.listdir(".")
    print(f"DEBUG_LAUNCHER: Files in dir: {files}")
    sys.exit(1)

print(f"DEBUG_LAUNCHER: Starting {TARGET_FILE}...")
try:
    # Run synchronously to catch output
    result = subprocess.run(
        [sys.executable, TARGET_FILE],
        capture_output=True,
        text=True,
        check=False
    )
    print("DEBUG_LAUNCHER: Process finished.")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("EXIT CODE:", result.returncode)
except Exception as e:
    print(f"DEBUG_LAUNCHER: Exception running subprocess: {e}")
