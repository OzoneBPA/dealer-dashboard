#!/usr/bin/env python3
"""
Ozone Overseas — Direct Dealer Dashboard Data Updater
======================================================
HOW TO USE:
  1. Open config.py and paste your GitHub token
  2. Double-click update_data.bat to push latest data
  3. Done — dashboard updates live!
"""

import json, base64, subprocess, sys, os
from datetime import datetime

# ── Load config ───────────────────────────────────────────────
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import GITHUB_TOKEN, EXCEL_PATH
except ImportError:
    print("\n  ERROR: config.py not found!")
    print("  Please create config.py next to this file.")
    print("  See config.py.example for the template.")
    input("\nPress Enter to exit..."); sys.exit(1)

if GITHUB_TOKEN == "PASTE_YOUR_TOKEN_HERE":
    print("\n  ERROR: Please open config.py and paste your GitHub token!")
    input("\nPress Enter to exit..."); sys.exit(1)

# ── Settings (don't change these) ────────────────────────────
GITHUB_USER   = "AbhishekTaneja229"
GITHUB_REPO   = "dealer-dashboard"
GITHUB_FILE   = "data.json"
GITHUB_BRANCH = "main"

# ── Install missing packages ──────────────────────────────────
def install_if_missing(pkg):
    try: __import__(pkg)
    except ImportError:
        print(f"  Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

# ── Main ──────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Ozone DD Dashboard — Data Updater")
    print("=" * 55)

    print("\n[1/4] Checking dependencies...")
    install_if_missing("openpyxl")
    install_if_missing("pandas")
    install_if_missing("requests")
    import pandas as pd, requests

    print(f"\n[2/4] Reading Excel...")
    if not os.path.exists(EXCEL_PATH):
        print(f"\n  ERROR: File not found:\n  {EXCEL_PATH}")
        print("\n  Update EXCEL_PATH in config.py if path changed.")
        input("\nPress Enter to exit..."); sys.exit(1)

    try:
        df = pd.read_excel(EXCEL_PATH)
        print(f"  OK — {len(df):,} rows  |  {len(df.columns)} columns")
    except Exception as e:
        print(f"\n  ERROR: {e}")
        input("\nPress Enter to exit..."); sys.exit(1)

    print("\n[3/4] Converting to JSON...")
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        dtype = str(df[col].dtype)
        if 'datetime' in dtype:
            df[col] = df[col].dt.strftime('%Y-%m-%d').fillna('')
        elif dtype == 'object':
            df[col] = df[col].fillna('').astype(str)
        else:
            df[col] = df[col].fillna(0)

    payload = {
        "updated_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "updated_by": os.environ.get("USERNAME", "user"),
        "row_count":  len(df),
        "columns":    list(df.columns),
        "data":       df.to_dict(orient="records")
    }
    json_str = json.dumps(payload, ensure_ascii=False, separators=(',',':'))
    print(f"  OK — {len(json_str)/1024:.1f} KB")

    print(f"\n[4/4] Pushing to GitHub...")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github.v3+json"
    }
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE}"

    sha = None
    check = requests.get(api_url, headers=headers)
    if check.status_code == 200:
        sha = check.json().get("sha")

    body = {
        "message": f"data: {datetime.now().strftime('%d-%b-%Y %H:%M')} ({len(df):,} rows)",
        "content": base64.b64encode(json_str.encode()).decode(),
        "branch":  GITHUB_BRANCH
    }
    if sha: body["sha"] = sha

    resp = requests.put(api_url, headers=headers, json=body)

    if resp.status_code in (200, 201):
        print(f"\n{'='*55}")
        print(f"  SUCCESS! Dashboard updated.")
        print(f"  URL: https://{GITHUB_USER.lower()}.github.io/{GITHUB_REPO}/")
        print(f"  Rows: {len(df):,}  |  {payload['updated_at']}")
        print(f"{'='*55}")
    else:
        print(f"\n  ERROR {resp.status_code}: {resp.text[:400]}")
        input("\nPress Enter to exit..."); sys.exit(1)

    import time; time.sleep(4)

if __name__ == "__main__":
    main()
