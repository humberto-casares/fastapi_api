from . import sqlop


async def db_update(table, values, where=None, returning=None, conn=None):
    _values = sqlop.extract_values(round_values(values))
    sql = f"UPDATE {table} SET {sqlop.update(values)}"
    if where:
        sql = f"{sql} {sqlop.where(where, start_at=len(values) + 1)}"
        [_values.append(v) for v in where.values()]
    if returning:
        res = await conn.fetchrow(f"{sql} RETURNING {returning}", *_values)
        if res is not None:
            return dict(res)
        else:
            return None
    else:
        updated = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *_values)
        return len(updated)


async def db_insert(table, values, returning=None, conn=None):
    _count = [f"${x}" for x, v in enumerate(round_values(values).keys(), 1)]
    sql = f"INSERT INTO {table} ({','.join(values.keys())}) VALUES ({','.join(_count)})"
    _values = sqlop.extract_values(values)
    if returning:
        res = await conn.fetchrow(f"{sql} RETURNING {returning}", *_values)
        if res is not None:
            return dict(res)
        else:
            return None
    else:
        inserted = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *_values)
        return len(inserted)


async def upsert(table, values, constraint=None, returning=None, conn=None):
    constraint = constraint or f"{table}_pk"
    _count = [f"${x}" for x, v in enumerate(values.keys(), 1)]
    _vals = sqlop.extract_values(values)
    _kvps = [f"{v}=${idx + len(values)}" for idx, v in enumerate(values.keys(), 1)]

    sql = (
        f"INSERT INTO {table} ({','.join(values.keys())}) "
        f"VALUES ({','.join(_count)}) "
        f"ON CONFLICT ({constraint}) DO UPDATE SET {','.join(_kvps)}"
    )

    if returning:
        res = await conn.fetchrow(f"{sql} RETURNING {returning}", *(_vals + _vals))
        if res is not None:
            return dict(res)
        else:
            return None
    else:
        upserted = await conn.fetch(f"{sql} RETURNING {list(values.keys())[0]}", *(_vals + _vals))
        return len(upserted)


async def upsert_many(table, rows, constraint=None, returning=None, conn=None):
    if not rows:
        return 0  # No rows to upsert

    constraint = constraint or f"{table}_pk"
    keys = [f'"{k}"' for k in rows[0].keys()]
    values_placeholder = [f"${x}" for x in range(1, len(keys) * len(rows) + 1)]
    split_points = [x for x in range(len(keys), len(values_placeholder) + 1, len(keys))]
    values_chunks = [values_placeholder[s - len(keys):s] for s in split_points]
    values_sql = ",".join([f"({','.join(chunk)})" for chunk in values_chunks])
    all_values = [value for row in rows for value in row.values()]

    _kvps = [f"{key}=excluded.{key}" for key in keys]

    sql = f'INSERT INTO {table} ({",".join(keys)}) VALUES {values_sql} ON CONFLICT ({constraint}) DO UPDATE SET {",".join(_kvps)}'

    if returning:
        result = await conn.fetch(f"{sql} RETURNING {returning}", *all_values)
        return [dict(row) for row in result] if result else []
    else:
        upserted = await conn.fetch(f"{sql} RETURNING {list(keys)[0]}", *all_values)
        return len(upserted)


def round_values(values: dict) -> dict:
    """Round all numeric values in the dictionary to 2 decimal places."""
    return {k: round(v, 2) if isinstance(v, float) else v for k, v in values.items()}
