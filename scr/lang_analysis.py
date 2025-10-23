import re
from numerizer import numerize
from sqlalchemy import and_, or_

def preprocess_query(query: str) -> str:
    """Clean and normalize the query"""
    query = query.lower().strip()
    
    # Convert spelled numbers to digits
    try:
        query = numerize(query)
    except Exception:
        pass
    
    # Normalize whitespace
    query = re.sub(r"\s+", " ", query)
    
    # Remove extra punctuation but keep operators
    query = re.sub(r"[^\w\s<>=!,]", " ", query)
    query = re.sub(r"\s+", " ", query).strip()
    
    return query


def build_filters(parsed, StringRecord):
    def _parse_cond(cond):
        if not isinstance(cond, dict): return None
        ctype = cond.get("type")
        
        # -------------------
        # Comparison
        # -------------------
        if ctype == "comparison":
            field = getattr(StringRecord, cond["field"], None)
            if field is None:
                raise ValueError(f"Unknown field: {cond['field']}")
            op_map = {
                ">": lambda f,v: f>v, ">=": lambda f,v: f>=v,
                "<": lambda f,v: f<v, "<=": lambda f,v: f<=v,
                "==": lambda f,v: f==v, "!=": lambda f,v: f!=v
            }
            return op_map[cond["op"]](field, cond["value"])
        
        # -------------------
        # Range
        # -------------------
        elif ctype == "range":
            field = getattr(StringRecord, cond["field"], None)
            if field is None: return None
            return and_(field>=cond["min"], field<=cond["max"])
        
        # -------------------
        # Contains
        # -------------------
        elif ctype == "contains":
            subtype = cond.get("subtype")
            neg = cond.get("neg", False)
            
            if subtype == "count":
                field = getattr(StringRecord, cond["field"], None)
                expr = field >= cond["value"]
            elif subtype == "char_class":
                if cond["char_class"]=="vowel": chars="aeiou"
                elif cond["char_class"]=="consonant": chars="bcdfghjklmnpqrstvwxyz"
                elif cond["char_class"]=="alphabet": chars="abcdefghijklmnopqrstuvwxyz"
                expr = or_(*[StringRecord.value.ilike(f"%{c}%") for c in chars])
            elif subtype == "letter":
                expr = StringRecord.value.ilike(f"%{cond['letter']}%")
            else: return None
            
            return ~expr if neg else expr
        
        # -------------------
        # Qualitative
        # -------------------
        elif ctype=="qualitative":
            is_pal = StringRecord.is_palindrome==True
            filters = [is_pal]
            if cond.get("word_count") is not None:
                filters.append(StringRecord.word_count==cond["word_count"])
            if cond.get("length") is not None:
                filters.append(StringRecord.length==cond["length"])
            return and_(*filters)
        
        # -------------------
        # Compound
        # -------------------
        elif ctype=="compound":
            filters = []
            for item in cond["conditions"]:
                if isinstance(item, dict) and "op" in item and "condition" in item:
                    f = _parse_cond(item["condition"])
                    if f is not None:
                        filters.append((item["op"], f))
                elif isinstance(item, dict):
                    f = _parse_cond(item)
                    if f is not None:
                        filters.append(("and", f))
            
            if not filters: return None
            result = filters[0][1]
            for i in range(1,len(filters)):
                op,f = filters[i]
                result = or_(result,f) if op=="or" else and_(result,f)
            return result
        
        # -------------------
        # All
        # -------------------
        elif ctype=="all": return None
        
        return None
    
    f = _parse_cond(parsed)
    return [f] if f is not None else []