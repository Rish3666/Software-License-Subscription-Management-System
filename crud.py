"""Reusable CRUD helpers used by the Streamlit UI.

Generic, engine-agnostic (works on the MySQL schema and the SQLite mirror):
- insert       : add one row to any table
- apply_edits  : diff an edited DataFrame against the original and UPDATE rows
- delete_rows  : delete selected PK values (FK RESTRICT errors surface to UI)

Business rules (BR-01..BR-04, CHECK, UNIQUE, FK) are enforced by the database
itself, so any violation raises and is shown as an error toast by the caller.
"""
import pandas as pd

import db


def get_table(table: str) -> pd.DataFrame:
    return db.q(f"SELECT * FROM {table}")


def insert(table: str, values: dict) -> None:
    cols = ", ".join(values)
    ph = ", ".join(["?"] * len(values))
    db.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})",
               tuple(values.values()))


def delete_rows(table: str, pk_col: str, pk_values) -> int:
    if not pk_values:
        return 0
    ph = ", ".join(["?"] * len(pk_values))
    with db.get_conn() as conn:
        cur = conn.execute(f"DELETE FROM {table} WHERE {pk_col} IN ({ph})",
                           tuple(pk_values))
        conn.commit()
        return cur.rowcount


def apply_edits(table: str, pk_col: str,
                original: pd.DataFrame, edited: pd.DataFrame) -> int:
    """UPDATE only the cells that actually changed, row by row."""

    def norm(v):
        # treat pandas NaN as SQL NULL so empty cells never look "changed"
        try:
            if pd.isna(v):
                return None
        except (TypeError, ValueError):
            pass
        return v

    changed = 0
    pk_vals = edited[pk_col].tolist()
    orig = original.set_index(pk_col)
    for _, row in edited.iterrows():
        key = row[pk_col]
        before = orig.loc[key]
        diffs = {c: norm(row[c]) for c in edited.columns
                 if c != pk_col and norm(row[c]) != norm(before[c])}
        if not diffs:
            continue
        if isinstance(diffs.get("auto_renew"), bool):
            diffs["auto_renew"] = int(diffs["auto_renew"])
        if isinstance(diffs.get("is_active"), bool):
            diffs["is_active"] = int(diffs["is_active"])
        set_sql = ", ".join(f"{c} = ?" for c in diffs)
        db.execute(f"UPDATE {table} SET {set_sql} WHERE {pk_col} = ?",
                   (*diffs.values(), key))
        changed += 1
    assert len(pk_vals) >= 0
    return changed
