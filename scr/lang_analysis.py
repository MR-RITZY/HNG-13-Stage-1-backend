import re
from numerizer import numerize

def preprocess_query(query: str) -> str:
    """Clean and normalize the query - FIXED to preserve single letters"""
    query = query.lower().strip()
    
    # Convert spelled numbers to digits BEFORE removing punctuation
    try:
        query = numerize(query)
    except Exception:
        pass
    
    # Normalize whitespace
    query = re.sub(r"\s+", " ", query)
    
    # Remove punctuation but preserve:
    # - Single letters (a-z) surrounded by spaces
    # - Operators (<, >, =, !)
    # - Commas
    # DO NOT remove single letters!
    # Only remove special chars that aren't letters, numbers, spaces, or operators
    query = re.sub(r"[^\w\s<>=!,]", " ", query)
    
    # Clean up multiple spaces again
    query = re.sub(r"\s+", " ", query).strip()
    
    return query


# ==========================================
# FILTER BUILDING
# ==========================================

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
            
            op = cond["op"]
            val = cond["value"]
            
            op_map = {
                ">": lambda f, v: f > v,
                ">=": lambda f, v: f >= v,
                "<": lambda f, v: f < v,
                "<=": lambda f, v: f <= v,
                "==": lambda f, v: f == v,
                "!=": lambda f, v: f != v,
            }
            
            return op_map.get(op, lambda f, v: f == v)(field, val)
        
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
            elif subtype == "char_class":
                char_class = cond["char_class"]
                if "vowel" in char_class:
                    chars = "aeiou"
                elif "consonant" in char_class:
                    chars = "bcdfghjklmnpqrstvwxyz"
                else:  # alphabet
                    chars = "abcdefghijklmnopqrstuvwxyz"
                
                # Create OR condition for each character
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
            
            # Add word count or length filter if specified
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
                        # First item, no operator
                        f = _parse_cond(item)
                        if f is not None:
                            filters.append(("and", f))
            
            if not filters:
                return None
            
            # Build combined filter
            result = filters[0][1]
            for i in range(1, len(filters)):
                op, f = filters[i]
                if op == "or":
                    result = or_(result, f)
                else:
                    result = and_(result, f)
            
            return result
        
        elif cond_type == "all":
            return None  # No filter, return all
        
        return None
    
    f = _parse_cond(parsed)
    return [f] if f is not None else []








