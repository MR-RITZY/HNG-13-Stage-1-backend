from lark import Transformer

class NLTransformer(Transformer):
    
    # Numbers
    def numeric_number(self, items):
        return int(items[0])
    
    def one(self, _):
        return 1
    
    def two(self, _):
        return 2
    
    # Multi-word adjectives
    def at_least(self, _): return "at_least"
    def at_most(self, _): return "at_most"
    def longer_than(self, _): return "longer_than"
    def shorter_than(self, _): return "shorter_than"
    def greater_than(self, _): return "greater_than"
    def less_than(self, _): return "less_than"
    def more_than(self, _): return "more_than"
    def fewer_than(self, _): return "fewer_than"
    def equal_to(self, _): return "equal_to"
    
    # Helpers to extract strings
    def _extract_str(self, items):
        return str(items[0]) if items else None
    
    def head(self, items): return self._extract_str(items)
    def keyword(self, items): return self._extract_str(items)
    def adj(self, items): return self._extract_str(items)
    def multi_word_adj(self, items): return items[0] if items else None
    def verb_elem(self, items): return self._extract_str(items)
    def alpha(self, items): return self._extract_str(items)
    def letter(self, items): return self._extract_str(items).lower()
    def operator(self, items): return self._extract_str(items)
    def qual_adj(self, items): return self._extract_str(items)
    def neg(self, items): return True
    def conj(self, items): return self._extract_str(items)
    
    # -----------------------------
    # QUALITATIVE CONDITIONS
    # -----------------------------
    def qual_condition(self, items):
        qual = None
        word_count = None
        length = None
        
        for item in items:
            if isinstance(item, str):
                if item in ["palindrome", "palindromic", "mirror", "symmetric", "symmetrical"]:
                    qual = item
                elif item in ["single", "monoword", "mono"]:
                    word_count = 1
                elif item in ["double", "pair", "couple"]:
                    word_count = 2
            elif isinstance(item, int):
                # Could be length
                length = item
        
        return {"type": "qualitative", "qual": qual or "palindrome",
                "word_count": word_count, "length": length}
    
    # -----------------------------
    # COMPARISON CONDITIONS
    # -----------------------------
    def comparison_condition(self, items):
        number = None
        keyword = None
        adj = None
        operator = None
        
        for item in items:
            if isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in ["word", "words"]: keyword = item
                elif item in ["character", "characters", "char", "chars", "length"]: keyword = item
                elif item in [">", ">=", "<", "<=", "==", "=", "!="]: operator = item
                else: adj = item
        
        field = "length" if keyword not in ["word", "words"] else "word_count"
        
        if operator:
            op = operator if operator != "=" else "=="
        elif adj:
            op_map = {
                "longer": ">", "shorter": "<", "greater": ">", "less": "<",
                "more": ">", "fewer": "<", "over": ">", "under": "<",
                "exactly": "==", "just": "==", "only": "==", "precisely": "==", "about": "==",
                "long": ">=", "short": "<=",
                "at_least": ">=", "at_most": "<=",
                "longer_than": ">", "shorter_than": "<",
                "greater_than": ">", "less_than": "<",
                "more_than": ">", "fewer_than": "<",
                "equal_to": "=="
            }
            op = op_map.get(adj, "==")
        else:
            op = "=="
        
        return {"type": "comparison", "field": field, "op": op, "value": number}
    
    # -----------------------------
    # ELEMENT CONDITIONS
    # -----------------------------
    def element_condition(self, items):
        neg = False
        verb = None
        number = None
        keyword = None
        alpha = None
        letter = None
        
        for item in items:
            if item is True: neg = True
            elif isinstance(item, int): number = item
            elif isinstance(item, str):
                if item in ["have", "has", "having", "contain", "contains", "containing",
                            "include", "includes", "including", "with"]: verb = item
                elif item in ["word", "words"]: keyword = item
                elif item in ["character", "characters", "char", "chars", "length"]: keyword = item
                elif item in ["vowel", "vowels", "consonant", "consonants"]: alpha = item
                elif item in ["alphabet", "alphabets"]: alpha = "alphabet"
                elif len(item) == 1 and item.isalpha(): letter = item.lower()
        
        result = {"type": "contains", "neg": neg}
        if number and keyword:
            field = "word_count" if keyword in ["word", "words"] else "length"
            result.update({"subtype": "count", "field": field, "value": number})
        elif alpha:
            result.update({"subtype": "char_class", "char_class": alpha})
        elif letter:
            result.update({"subtype": "letter", "letter": letter})
        
        return result
    
    # -----------------------------
    # RANGE CONDITIONS
    # -----------------------------
    def range_condition(self, items):
        numbers = [item for item in items if isinstance(item, int)]
        keyword = next((item for item in items if isinstance(item, str) and item in ["word", "words", "character", "characters", "char", "chars", "length"]), None)
        field = "word_count" if keyword in ["word", "words"] else "length"
        return {"type": "range", "field": field,
                "min": numbers[0] if len(numbers) > 0 else 0,
                "max": numbers[1] if len(numbers) > 1 else 999}
    
    # -----------------------------
    # LENGTH PHRASES
    # -----------------------------
    def length_phrase(self, items):
        number = None
        adj = None
        operator = None
        for item in items:
            if isinstance(item, int): number = item
            elif isinstance(item, str):
                if item in [">", ">=", "<", "<=", "==", "=", "!="]: operator = item
                else: adj = item
        
        if operator: op = operator if operator != "=" else "=="
        elif adj:
            op_map = {
                "longer": ">", "shorter": "<", "greater": ">", "less": "<",
                "more": ">", "fewer": "<", "over": ">", "under": "<",
                "exactly": "==", "just": "==", "only": "==",
                "at_least": ">=", "at_most": "<=",
                "longer_than": ">", "shorter_than": "<",
                "greater_than": ">", "less_than": "<",
                "more_than": ">", "fewer_than": "<"
            }
            op = op_map.get(adj, "==")
        else: op = "=="
        
        return {"type": "comparison", "field": "length", "op": op, "value": number}
    
    # -----------------------------
    # DET + NUMBER + KEYWORD + HEAD
    # -----------------------------
    def det_number_keyword_head(self, items):
        number = None
        keyword = None
        adj = None
        for item in items:
            if isinstance(item, int): number = item
            elif isinstance(item, str):
                if item in ["word", "words"]: keyword = item
                elif item in ["character", "characters", "char", "chars", "length"]: keyword = item
                elif item in ["long", "short", "exactly", "just", "only"]: adj = item
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        op_map = {"long": ">=", "short": "<=", "exactly": "==", "just": "==", "only": "=="}
        op = op_map.get(adj, "==")
        
        return {"type": "comparison", "field": field, "op": op, "value": number}
    
    # -----------------------------
    # HEAD ONLY
    # -----------------------------
    def head_only(self, items):
        return {"type": "all"}
    
    # -----------------------------
    # COMPOUND CONDITIONS
    # -----------------------------
    def compound_condition(self, items):
        conditions = []
        last_op = "and"
        for item in items:
            if isinstance(item, str) and item in ["and", "or", "but"]: 
                last_op = "and" if item=="but" else item
            elif isinstance(item, dict):
                conditions.append({"op": last_op, "condition": item})
                last_op = "and"
        
        if not conditions: return {"type": "all"}
        first_cond = conditions[0]["condition"]
        rest = conditions[1:] if len(conditions)>1 else []
        if rest:
            return {"type": "compound", "conditions": [first_cond]+rest}
        return first_cond
    
    def single_condition(self, items):
        return items[0] if items else {"type": "all"}
    
    def start(self, items):
        return items[0] if items else {"type": "all"}
