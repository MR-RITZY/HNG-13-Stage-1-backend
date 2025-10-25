import re
from numerizer import numerize

def preprocess_query(query: str) -> str:
    query = query.lower().strip()
    
    try:
        query = numerize(query)
    except Exception:
        pass
    
    query = re.sub(r"\s+", " ", query)
    query = re.sub(r"[^\w\s<>=!,]", " ", query)
    query = re.sub(r"\s+", " ", query).strip()
    
    return query




from sqlalchemy import and_, or_

def build_filters(parsed, StringRecord):
    """Build SQLAlchemy filters from parsed tree"""
    
    def _parse_cond(cond):
        if not isinstance(cond, dict):
            return None
        
        cond_type = cond.get("type")
        
        if cond_type == "comparison":
            field = getattr(StringRecord, cond["field"], None)
            if not field:
                return None
            
            op_map = {
                ">": lambda f, v: f > v,
                ">=": lambda f, v: f >= v,
                "<": lambda f, v: f < v,
                "<=": lambda f, v: f <= v,
                "==": lambda f, v: f == v,
                "!=": lambda f, v: f != v,
            }
            
            return op_map.get(cond["op"], lambda f, v: f == v)(field, cond["value"])
        
        elif cond_type == "range":
            field = getattr(StringRecord, cond["field"], None)
            if not field:
                return None
            return and_(field >= cond["min"], field <= cond["max"])
        
        elif cond_type == "contains":
            subtype = cond.get("subtype")
            neg = cond.get("neg", False)
            
            if subtype == "count":
                field = getattr(StringRecord, cond["field"], None)
                if not field:
                    return None
                expr = field >= cond["value"]
            
            elif subtype == "positional":
                position = cond.get("position")
                alpha = cond.get("alpha")
                letter = cond.get("letter")
                
                if position is None:
                    return None
                
                if alpha:
                    if "vowel" in alpha:
                        chars = "aeiou"
                    elif "consonant" in alpha:
                        chars = "bcdfghjklmnpqrstvwxyz"
                    else:
                        chars = "abcdefghijklmnopqrstuvwxyz"
                    
                    # Basic SQL filter - check if chars exist
                    expr = or_(*[StringRecord.value.ilike(f"%{c}%") for c in chars])
                
                elif letter:
                    # Basic SQL filter - check if letter exists
                    expr = StringRecord.value.ilike(f"%{letter}%")
                
                else:
                    return None
            
            elif subtype == "char_class":
                char_class = cond["char_class"]
                if "vowel" in char_class:
                    chars = "aeiou"
                elif "consonant" in char_class:
                    chars = "bcdfghjklmnpqrstvwxyz"
                else:
                    chars = "abcdefghijklmnopqrstuvwxyz"
                expr = or_(*[StringRecord.value.ilike(f"%{c}%") for c in chars])
            
            elif subtype == "letter":
                letter = cond["letter"]
                expr = StringRecord.value.ilike(f"%{letter}%")
            else:
                return None
            
            return ~expr if neg else expr
        
        elif cond_type == "qualitative":
            qual = cond["qual"]
            filters = []
            
            if qual in ["palindrome", "palindromic"]:
                filters.append(StringRecord.is_palindrome == True)
            
            if "word_count" in cond:
                filters.append(StringRecord.word_count == cond["word_count"])
            if "length" in cond:
                filters.append(StringRecord.length == cond["length"])
            
            return and_(*filters) if filters else None
        
        elif cond_type == "compound":
            filters = []
            for item in cond["conditions"]:
                if isinstance(item, dict):
                    if "op" in item and "condition" in item:
                        f = _parse_cond(item["condition"])
                        if f is not None:
                            filters.append((item["op"], f))
                    else:
                        f = _parse_cond(item)
                        if f is not None:
                            filters.append(("and", f))
            
            if not filters:
                return None
            
            result = filters[0][1]
            for i in range(1, len(filters)):
                op, f = filters[i]
                result = or_(result, f) if op == "or" else and_(result, f)
            
            return result
        
        elif cond_type == "all":
            return None
        
        return None
    
    f = _parse_cond(parsed)
    return [f] if f is not None else []


# ==========================================
# PYTHON-SIDE POSITIONAL FILTERING
# ==========================================

def apply_positional_filter(results: list, parsed: dict) -> list:
    """
    Apply exact positional filtering (Python-side).
    Call this AFTER getting results from database.
    """
    
    def check_condition(cond, value):
        """Check if a single condition matches"""
        if cond.get("type") == "contains" and cond.get("subtype") == "positional":
            position = cond.get("position")
            alpha = cond.get("alpha")
            letter = cond.get("letter")
            neg = cond.get("neg", False)
            
            value_lower = value.lower()
            match = False
            
            if alpha:
                if "vowel" in alpha:
                    char_set = "aeiou"
                elif "consonant" in alpha:
                    char_set = "bcdfghjklmnpqrstvwxyz"
                else:
                    char_set = "abcdefghijklmnopqrstuvwxyz"
                
                filtered_chars = [c for c in value_lower if c in char_set]
                
                if position == -1:  # last
                    if value_lower and value_lower[-1] in char_set:
                        match = True
                else:
                    if len(filtered_chars) >= position:
                        match = True
            
            elif letter:
                letter_positions = [i + 1 for i, c in enumerate(value_lower) if c == letter]
                
                if position == -1:  # last
                    if value_lower and value_lower[-1] == letter:
                        match = True
                else:
                    if len(letter_positions) >= position:
                        match = True
            
            return match if not neg else not match
        
        return True  # Non-positional conditions already filtered by SQL
    
    def needs_positional_check(cond):
        """Check if condition needs Python-side filtering"""
        if isinstance(cond, dict):
            if cond.get("type") == "contains" and cond.get("subtype") == "positional":
                return True
            elif cond.get("type") == "compound":
                for item in cond.get("conditions", []):
                    if isinstance(item, dict):
                        if "condition" in item:
                            if needs_positional_check(item["condition"]):
                                return True
                        elif needs_positional_check(item):
                            return True
        return False
    
    def check_all_conditions(cond, value):
        """Recursively check all conditions including compounds"""
        if cond.get("type") == "compound":
            results = []
            for item in cond.get("conditions", []):
                if isinstance(item, dict):
                    if "condition" in item:
                        result = check_all_conditions(item["condition"], value)
                        op = item.get("op", "and")
                        results.append((op, result))
                    else:
                        result = check_all_conditions(item, value)
                        results.append(("and", result))
            
            if not results:
                return True
            
            final = results[0][1]
            for i in range(1, len(results)):
                op, r = results[i]
                if op == "or":
                    final = final or r
                else:
                    final = final and r
            return final
        else:
            return check_condition(cond, value)
    
    # Only filter if positional checks needed
    if not needs_positional_check(parsed):
        return results
    
    # Apply positional filtering
    filtered = []
    for record in results:
        if check_all_conditions(parsed, record.value):
            filtered.append(record)
    
    return filtered