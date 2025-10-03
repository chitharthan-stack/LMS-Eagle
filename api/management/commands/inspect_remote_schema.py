# api/management/commands/inspect_remote_schema.py
"""
Inspect remote DB schema and diff with api/tmp_models.py WITHOUT importing
tmp_models as Django models (avoids app registry conflicts).
"""
from django.core.management.base import BaseCommand
from django.db import connections, DEFAULT_DB_ALIAS
from django.conf import settings
import ast
from pathlib import Path
import re

TMP_MODELS_RELPATH = Path("api") / "tmp_models.py"

# helper to extract string from ast node
def ast_str(node):
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None

class TmpModelParser(ast.NodeVisitor):
    """
    Parse top-level classes in tmp_models.py and collect:
      - class name
      - meta.db_table (if provided)
      - fields: mapping db_column -> {attr_name, field_type, null}
    We only look for simple top-level assignments like:
      field_name = models.TextField(blank=True, null=True, db_column='colname')
    and an inner Meta class with db_table = "..."
    """
    def __init__(self):
        self.models = {}  # name -> dict(db_table, fields)
        self._current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        # start a model class
        cls_name = node.name
        self._current_class = {"class_name": cls_name, "db_table": None, "fields": {}}
        # iterate body
        for elt in node.body:
            if isinstance(elt, ast.Assign):
                # class attr assignment (likely field)
                for target in elt.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        # try to analyze value: call to models.<Field>
                        val = elt.value
                        if isinstance(val, ast.Call):
                            # function or attribute call; get func name
                            func = val.func
                            field_type = None
                            if isinstance(func, ast.Attribute):
                                # e.g., models.TextField
                                if isinstance(func.value, ast.Name) and func.value.id == "models":
                                    field_type = func.attr
                            elif isinstance(func, ast.Name):
                                field_type = func.id
                            # collect kwargs (db_column, null)
                            db_column = None
                            null = False
                            for kw in val.keywords:
                                if kw.arg == "db_column":
                                    db_column = ast_str(kw.value)
                                if kw.arg == "null":
                                    if isinstance(kw.value, ast.Constant):
                                        null = bool(kw.value.value)
                                if kw.arg == "blank" and isinstance(kw.value, ast.Constant):
                                    # blank not used for null detection but noted
                                    pass
                            key = db_column if db_column else attr_name
                            self._current_class["fields"][key] = {"attr": attr_name, "type": field_type or "Unknown", "null": null}
            elif isinstance(elt, ast.ClassDef) and elt.name == "Meta":
                # inner Meta class: look for db_table
                for m_elt in elt.body:
                    if isinstance(m_elt, ast.Assign):
                        for t in m_elt.targets:
                            if isinstance(t, ast.Name) and t.id == "db_table":
                                dbt = ast_str(m_elt.value)
                                if dbt:
                                    self._current_class["db_table"] = dbt
                    # also capture unique_together for info (optional)
        # only record classes that look like models (contain fields and db_table)
        if self._current_class and self._current_class["fields"]:
            # ensure db_table fallback to lowercase class name if not set
            if not self._current_class["db_table"]:
                # default guess: class name lowercased + 's' maybe; but we'll set to None
                self._current_class["db_table"] = None
            self.models[self._current_class["class_name"]] = self._current_class
        self._current_class = None
        # continue visiting nested nodes if any
        # super().generic_visit(node)  # not required

def load_tmp_models_file():
    # attempt to find file relative to settings.BASE_DIR
    base = Path(settings.BASE_DIR) if hasattr(settings, "BASE_DIR") else Path.cwd()
    p = (base / TMP_MODELS_RELPATH).resolve()
    if not p.exists():
        # fallback: relative path
        p = Path(TMP_MODELS_RELPATH)
    if not p.exists():
        raise FileNotFoundError(f"Could not find {TMP_MODELS_RELPATH} at {p}")
    return p.read_text(encoding="utf-8")

class Command(BaseCommand):
    help = "Compare tmp_models.py surface against DB schema without importing tmp_models"

    def add_arguments(self, parser):
        parser.add_argument("--db-alias", default=DEFAULT_DB_ALIAS, help="DB alias to use (default: default)")

    def handle(self, *args, **options):
        db_alias = options["db_alias"]
        self.stdout.write(self.style.MIGRATE_LABEL(f"Using DB alias: {db_alias}"))
        # parse tmp_models.py
        try:
            src = load_tmp_models_file()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Could not load tmp_models.py: {e}"))
            return

        try:
            tree = ast.parse(src)
            parser = TmpModelParser()
            parser.visit(tree)
            tmp_models = parser.models  # dict of parsed models
            if not tmp_models:
                self.stdout.write(self.style.WARNING("No model-like classes parsed from tmp_models.py"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to parse tmp_models.py: {e}"))
            return

        conn = connections[db_alias]
        cur = conn.cursor()

        # For each parsed model, find matching table in DB (db_table in Meta preferred,
        # otherwise try class name lowercased)
        for cls_name, info in tmp_models.items():
            db_table = info.get("db_table")
            if not db_table:
                # try guesses: class name lowercased and plural
                guesses = [cls_name.lower(), cls_name.lower() + "s"]
            else:
                guesses = [db_table]

            found = None
            for g in guesses:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position;
                """, [g])
                rows = cur.fetchall()
                if rows:
                    found = g
                    break

            if not found:
                self.stdout.write(self.style.ERROR(f"Table for model {cls_name} not found (guesses: {guesses})"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"\n=== Model {cls_name} -> Table '{found}' ==="))
            remote_cols = {r[0]: {"data_type": r[1], "is_nullable": r[2]} for r in rows}
            model_fields = info["fields"]

            only_in_model = set(model_fields.keys()) - set(remote_cols.keys())
            only_in_remote = set(remote_cols.keys()) - set(model_fields.keys())
            in_both = set(model_fields.keys()).intersection(remote_cols.keys())

            if only_in_model:
                self.stdout.write(self.style.WARNING("Fields declared in tmp_models.py but missing in DB:"))
                for c in sorted(only_in_model):
                    f = model_fields[c]
                    self.stdout.write(f"  - model attr '{f['attr']}' (db_column='{c}', type={f['type']})")
            else:
                self.stdout.write(self.style.SUCCESS("No model-only fields."))

            if only_in_remote:
                self.stdout.write(self.style.ERROR("Columns present in DB but not declared in tmp_models.py:"))
                for c in sorted(only_in_remote):
                    rc = remote_cols[c]
                    self.stdout.write(f"  - remote column '{c}' (type={rc['data_type']}, nullable={rc['is_nullable']})")
            else:
                self.stdout.write(self.style.SUCCESS("No remote-only columns."))

            for c in sorted(in_both):
                mf = model_fields[c]
                rc = remote_cols[c]
                # rough type check
                if mf['type'] and mf['type'].lower() not in rc['data_type'].lower():
                    self.stdout.write(self.style.NOTICE(f"  * Type hint mismatch for '{c}': model={mf['type']} vs db={rc['data_type']}"))
                if (mf['null'] and rc['is_nullable'] == 'NO') or (not mf['null'] and rc['is_nullable'] == 'YES'):
                    self.stdout.write(self.style.NOTICE(f"  * Nullability mismatch for '{c}': model.null={mf['null']} vs db.is_nullable={rc['is_nullable']}"))

        # global search for 'url' columns
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Global search: columns named 'url' ==="))
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND column_name = 'url'
            ORDER BY table_name;
        """)
        rows = cur.fetchall()
        if rows:
            for tname, col, dtype in rows:
                self.stdout.write(self.style.NOTICE(f"Found 'url' in table '{tname}' (type={dtype})"))
        else:
            self.stdout.write(self.style.SUCCESS("No columns named 'url' found."))

        cur.close()
