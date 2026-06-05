#!/usr/bin/env python3
"""
Wathiq — Apply Supabase migrations.
Run this after cloning on Render or local.
Uses the Supabase service_role key to execute SQL.

Usage:
  SUPABASE_SERVICE_ROLE_KEY=your_key python3 scripts/apply_migrations.py
"""
import os
import sys
import httpx

SUPABASE_URL = "https://yywowhdgwcxulgnglcck.supabase.co"
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "supabase", "migrations")


def apply_migration(filepath: str) -> dict:
    """Execute a migration SQL file via Supabase's REST API."""
    with open(filepath) as f:
        sql = f.read()

    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }

    response = httpx.post(
        f"{SUPABASE_URL}/rest/v1/rpc/pg_query",
        headers=headers,
        json={"query": sql},
        timeout=60,
    )
    return {"file": os.path.basename(filepath), "status": response.status_code, "response": response.text[:200]}


def main():
    if not SERVICE_KEY:
        print("ERROR: Set SUPABASE_SERVICE_ROLE_KEY environment variable")
        sys.exit(1)

    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"ERROR: Migrations directory not found: {MIGRATIONS_DIR}")
        sys.exit(1)

    migrations = sorted(os.listdir(MIGRATIONS_DIR))
    print(f"Found {len(migrations)} migrations:")
    for m in migrations:
        print(f"  {m}")

    print("\nApplying migrations...")
    for m in migrations:
        filepath = os.path.join(MIGRATIONS_DIR, m)
        result = apply_migration(filepath)
        status = "✅" if result["status"] in (200, 201, 204) else "❌"
        print(f"  {status} {result['file']} — {result['status']}")

    print("\nDone.")


if __name__ == "__main__":
    main()