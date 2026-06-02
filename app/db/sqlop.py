_operators = {
    "eq": "=",
    "lt": "<",
    "gt": ">",
    "ne": "!=",
    "re": "~",
    "like": "LIKE",
    "not_like": "NOT LIKE",
}

_update_operators = {
    "": "%(field)s = %%(%(key)s)s",
    "add": "%(field)s = %(field)s + %%(%(key)s)s",
    "sub": "%(field)s = %(field)s - %%(%(key)s)s",
    "append": "%(field)s = %(field)s || %%(%(key)s)s",
    "func": "%(field)s = %(val)s",
}


def where(where, start_at=1):
    """
    Construct where clause from dict in format:

    eg. { 'key1'     : 'value1',
          'key2__op' : 'value1' }

        'key1 = %s AND key2 op %s' % (value1,value2)

    'op' is looked up in '_operators' hash table which
    maps common operators (eg '__lt' to '<'). If the
    operator is not found it is passed through directly
    allowing other operators to be specified directly.
    """
    if where:
        _where = []
        for idx, f in enumerate(where.keys()):
            field, _, op = f.partition("__")
            _where.append(f"{field} {_operators.get(op, op) or '='} ${start_at + idx}")
        return " WHERE " + " AND ".join(_where)
    else:
        return ""


def update(values):
    _update = []
    for idx, k in enumerate(values.keys(), 1):
        f, _, op = k.partition("__")
        _update.append(f"{f}=${idx}")
    return ",".join(_update)


def order(order):
    if order:
        _order = []
        for f in order:
            field, _, direction = f.partition("__")
            _order.append(field + (" DESC" if direction == "desc" else ""))
        return " ORDER BY " + ", ".join(_order)
    else:
        return ""


def columns(columns):
    if columns:
        return ", ".join(
            [(c if isinstance(c, str) else "%s AS %s" % c) for c in columns]
        )
    else:
        return "*"


def on(t, on):
    t1, t2 = t
    if on:
        return "%s = %s" % on
    else:
        return "%s.id = %s.%s_id" % (t1, t2, t1)


def limit(limit):
    if limit:
        return " LIMIT %d" % limit
    else:
        return ""


def offset(offset):
    if offset:
        return " OFFSET %d" % offset
    else:
        return ""


def for_update(update):
    if update:
        return " FOR UPDATE"
    else:
        return ""


def extract_values(values_dict):
    return [v for v in values_dict.values()]
