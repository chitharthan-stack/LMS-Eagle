

import os
import sys
import re
import importlib
from pathlib import Path
from collections import defaultdict

# Ensure manage.py / Django settings are on the path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Boot Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_backend.settings")
import django
django.setup()

from django.db import connection
from django.apps import apps
from django.conf import settings
import api.models as existing_models_module

# Basic PG -> Django field mapping
PG_TO_DJANGO = [
    (re.compile(r"^integer", re.I), "models.IntegerField(blank=True, null=True)"),
    (re.compile(r"^bigint", re.I), "models.BigIntegerField(blank=True, null=True)"),
    (re.compile(r"^smallint", re.I), "models.SmallIntegerField(blank=True, null=True)"),
    (re.compile(r"^numeric|^decimal", re.I), "models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)"),
    (re.compile(r"^double precision|^real", re.I), "models.FloatField(blank=True, null=True)"),
    (re.compile(r"^boolean", re.I), "models.BooleanField(blank=True, null=True)"),
    (re.compile(r"^text", re.I), "models.TextField(blank=True, null=True)"),
    (re.compile(r"^character varying|^varchar|^character", re.I), "models.TextField(blank=True, null=True)"),
    (re.compile(r"^timestamp", re.I), "models.DateTimeField(blank=True, null=True)"),
    (re.compile(r"^date$", re.I), "models.DateField(blank=True, null=True)"),
    (re.compile(r"^jsonb?$", re.I), "models.JSONField(blank=True, null=True)"),
    (re.compile(r"^uuid", re.I), "models.UUIDField(blank=True, null=True)"),
    (re.compile(r"^inet|^cidr", re.I), "models.TextField(blank=True, null=True)"),
    # arrays (very common): we'll attempt ArrayField with base type numeric/text
    (re.compile(r".*\[\]$"), "ARRAY"),
]

OUTPUT_FILE = Path(PROJECT_ROOT) / "api" / "tmp_models_autogen.py"

def pg_type_to_django(pg_type):
    pg_type = pg_type.strip()
    # arrays
    if pg_type.endswith("[]"):
        base = pg_type[:-2]
        # map base
        base_field = "models.TextField(blank=True, null=True)"
        for pattern, dj in PG_TO_DJANGO:
            if pattern.pattern == r".*\[\]$":
                continue
            if pattern.match(base):
                base_field = dj
                break
        # choose ArrayField format
        return f"models.ArrayField(base_field={base_field}, blank=True, null=True)"
    for pattern, dj in PG_TO_DJANGO:
        if pattern.match(pg_type):
            return dj
    # default fallback
    return "models.TextField(blank=True, null=True)"

def get_db_tables():
    with connection.cursor() as cur:
        # list only public schema tables (adjust if you use different schema)
        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog','information_schema')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """)
        return cur.fetchall()

def get_table_columns(schema, table):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        return cur.fetchall()

def load_existing_fields():
    """
    Read django model class attributes from api.models (best-effort).
    Returns mapping: { 'table_name' : set(field_names) }
    """
    mapping = defaultdict(set)
    # iterate through attributes in existing_models_module
    for name in dir(existing_models_module):
        cls = getattr(existing_models_module, name)
        if not isinstance(cls, type):
            continue
        # only classes with Meta.db_table in that module
        meta = getattr(cls, "Meta", None)
        if not meta:
            continue
        db_table = getattr(meta, "db_table", None)
        if not db_table:
            continue
        # collect declared field names
        declared = set()
        for k, v in vars(cls).items():
            # Django model fields are instances of Field (deferred import), but easiest is to ignore callables/private names
            if k.startswith("_"):
                continue
            if isinstance(v, (str, int, float, type(None))):
                continue
            # pick typical field objects by attribute names: we'll treat anything not a function/class as a field candidate
            if not callable(v) and not isinstance(v, type):
                declared.add(k)
        # fallback: read _meta if present
        try:
            _meta = getattr(cls, "_meta", None)
            if _meta:
                for f in _meta.fields:
                    declared.add(f.name)
        except Exception:
            pass
        mapping[db_table].update(declared)
    return mapping

def normalize_table_name(table):
    # some DB tables may be schema-qualified; use plain table name
    return table

def main():
    print("Running DB schema detection...")
    tables = get_db_tables()
    existing_fields = load_existing_fields()
    report = []
    snippets = []
    for schema, table in tables:
        table_key = f"{schema}.{table}" if schema else table
        plain_table = table
        cols = get_table_columns(schema, table)
        if not cols:
            continue
        db_col_names = [c[0] for c in cols]
        existing = existing_fields.get(plain_table, existing_fields.get(f"{schema}.{table}", set()))
        added = [c for c in cols if c[0] not in existing]
        removed = [f for f in existing if f not in db_col_names]
        report.append((schema, table, len(cols), len(existing), len(added), len(removed)))

        if added:
            # Build model snippet
            snippet_lines = []
            class_name = "".join(x.capitalize() for x in plain_table.split("_"))
            snippet_lines.append(f"class {class_name}(models.Model):")
            for col_name, data_type, udt_name in cols:
                if col_name in existing:
                    # include existing fields too so model looks complete
                    snippet_lines.append(f"    {col_name} = models.Field()  # keep existing or refine manually")
                else:
                    # decide pg type token (use udt_name for arrays etc.)
                    pg_type = udt_name if udt_name else data_type
                    django_field = pg_type_to_django(pg_type)
                    # skip id auto field (if id is missing DB uses composite PK)
                    if col_name == "id":
                        snippet_lines.append(f"    # NOTE: table has an 'id' column.")
                        snippet_lines.append(f"    id = models.AutoField(primary_key=True)")
                    else:
                        snippet_lines.append(f"    {col_name} = {django_field}")
            snippet_lines.append("")
            snippet_lines.append("    class Meta:")
            snippet_lines.append("        managed = False")
            snippet_lines.append(f"        db_table = \"{plain_table}\"")
            snippet_lines.append("")
            snippets.append("\n".join(snippet_lines))

    # Print summary
    print("\nSummary (schema, table, db_cols, model_fields_declared, new_columns, missing_in_db):")
    for r in report:
        print(f" - {r[0]}.{r[1]}: cols={r[2]} declared={r[3]} new_cols={r[4]} missing={r[5]}")

    if snippets:
        print("\nWriting suggested model snippets to:", OUTPUT_FILE)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
            fh.write("# Auto-generated model suggestions. Review & merge into api/models.py\n")
            fh.write("from django.db import models\n\n")
            for s in snippets:
                fh.write(s)
                fh.write("\n\n")
        print("Done. Please open", OUTPUT_FILE)
    else:
        print("No new columns detected vs current `api.models` declarations. Nothing to write.")

if __name__ == "__main__":
    main()
