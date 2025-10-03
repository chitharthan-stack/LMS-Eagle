# scripts/list_tables.py
import os
import sys

# ensure script can find your project package (adjust path if needed)
ROOT = os.path.dirname(os.path.abspath(__file__))  # scripts folder
PROJECT_ROOT = os.path.normpath(os.path.join(ROOT, ".."))  # project root
sys.path.insert(0, PROJECT_ROOT)

# point to your Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")

# now bootstrap Django
from django import setup
setup()

from django.db import connection

with connection.cursor() as cur:
    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type='BASE TABLE'
          AND table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY table_schema, table_name;
    """)
    rows = cur.fetchall()

print("Found", len(rows), "tables")
for schema, name in rows:
    print(f"{schema}.{name}")
