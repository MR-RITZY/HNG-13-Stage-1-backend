from sqlalchemy import and_, or_, cast, Integer, select
from scr.model import StringRecord


def filter_query_by_conditions(conditions: dict):
    filters = []

    # Boolean field
    if conditions.get("is_palindrome") is True:
        filters.append(StringRecord.is_palindrome.is_(True))

    # Length filters
    length = conditions.get("length")
    min_length = conditions.get("min_length")
    max_length = conditions.get("max_length")
    if isinstance(length, int):
        filters.append(StringRecord.length == length)
    if isinstance(min_length, int):
        filters.append(StringRecord.length >= min_length)
    if isinstance(max_length, int):
        filters.append(StringRecord.length <= max_length)

    # Word count filters
    word_count = conditions.get("word_count")
    min_word_count = conditions.get("min_word_count")
    max_word_count = conditions.get("max_word_count")
    if isinstance(word_count, int):
        filters.append(StringRecord.word_count == word_count)
    if isinstance(min_word_count, int):
        filters.append(StringRecord.word_count >= min_word_count)
    if isinstance(max_word_count, int):
        filters.append(StringRecord.word_count <= max_word_count)

    # Contains / startswith / endswith
    for key, pattern_func in [
        ("contains_character", lambda s: f"%{s}%"),
        ("startswith", lambda s: f"{s}%"),
        ("endswith", lambda s: f"%{s}")
    ]:
        
        v = conditions.get(key)
        if v:
            value = v.lower()
            segs = segregate(value)
            if segs:
                sep, items = segs
                conds = [StringRecord.value.ilike(pattern_func(item)) for item in items]
                filters.append(or_(*conds) if sep == "," else and_(*conds))
            else:
                filters.append(StringRecord.value.ilike(pattern_func(value)))

    # Character count filters (JSON field)
    for key, operator in [
        ("character_count", "exact"),
        ("min_character_count", ">="),
        ("max_character_count", "<=")
    ]:
        value = conditions.get(key)
        if value:
            segs = segregate(value)
            if segs:
                sep, items = segs
                conds = []
                for item in items:
                    char, count = count_string(item)
                    cond_expr = build_char_count_filter(char, count, operator)
                    conds.append(cond_expr)
                filters.append(or_(*conds) if sep == "," else and_(*conds))
            else:
                char, count = count_string(value)
                filters.append(build_char_count_filter(char, count, operator))

    return filters


def segregate(string: str):
    """Return (separator, items) or None if no separator."""
    striped = "".join(string.split())
    if "," in striped:
        return ",", striped.split(",")
    if "&" in striped:
        return "&", striped.split("&")
    return None


def count_string(string: str):
    """Convert 'a:3' to ('a', 3)."""
    striped = "".join(string.split())
    if len(striped) == 3 and striped[1] == ":":
        try:
            return striped[0], int(striped[2])
        except ValueError:
            pass
    raise ValueError(f"Invalid character_count format: {string}")


def build_char_count_filter(char, count, operator):
    """Return SQLAlchemy filter for JSON character_frequency_map field."""
    col = StringRecord.character_frequency_map[char].astext
    col_int = cast(col, Integer)
    if operator == "exact":
        return StringRecord.character_frequency_map.contains({char: count})
    elif operator == ">=":
        return col_int >= count
    elif operator == "<=":
        return col_int <= count
    else:
        raise ValueError(f"Unknown operator: {operator}")


# Usage in query
async def get_filtered_strings(db, conditions: dict):
    query = select(StringRecord)
    filters = filter_query_by_conditions(conditions)
    if filters:
        query = query.where(and_(*filters))
    result = await db.scalars(query)
    return result.all()


