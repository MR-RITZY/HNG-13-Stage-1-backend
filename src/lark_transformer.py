from lark import Transformer
import re

class NLTransformer(Transformer):
    
    # Numbers
    def numeric_number(self, items):
        return int(items[0])
    
    def word_number_val(self, items):
        return items[0]
    
    def one(self, _): return 1
    def two(self, _): return 2
    
    # Ordinals
    def pos_1(self, _): return 1
    def pos_2(self, _): return 2
    def pos_3(self, _): return 3
    def pos_4(self, _): return 4
    def pos_5(self, _): return 5
    def pos_6(self, _): return 6
    def pos_7(self, _): return 7
    def pos_8(self, _): return 8
    def pos_9(self, _): return 9
    def pos_10(self, _): return 10
    def pos_last(self, _): return -1
    
    def cardinal(self, items):
        """Parse 1st, 2nd, 3rd, etc."""
        text = str(items[0])
        match = re.match(r'(\d+)', text)
        return int(match.group(1)) if match else 1
    
    def ordinal(self, items):
        return items[0]
    
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
    def not_longer_than(self, _): return "not_longer_than"
    def not_shorter_than(self, _): return "not_shorter_than"
    
    # Helpers
    def _extract_str(self, items):
        return str(items[0]) if items else None
    
    def head(self, items): return self._extract_str(items)
    def keyword(self, items): return self._extract_str(items)
    def adj(self, items): return self._extract_str(items)
    def multi_word_adj(self, items): return items[0] if items else None
    def verb_elem(self, items): return self._extract_str(items)
    def alpha(self, items): return self._extract_str(items)
    def letter(self, items): return self._extract_str(items)
    def operator(self, items): return self._extract_str(items)
    def qual_adj(self, items): return self._extract_str(items)
    def word_number(self, items): return items[0]
    def neg(self, items): return True
    def conj(self, items): return self._extract_str(items)
    
    # Positional
    def positional_alpha(self, items):
        """Parse positional alpha patterns"""
        position = None
        alpha_type = None
        
        for item in items:
            if isinstance(item, int):
                position = item
            elif isinstance(item, str) and item in ["vowel", "vowels", "consonant", "consonants", "alphabet", "alphabets"]:
                alpha_type = item
        
        return {"type": "positional", "alpha": alpha_type, "position": position}
    
    def positional_letter(self, items):
        """Parse positional letter patterns"""
        position = None
        letter = None
        
        for item in items:
            if isinstance(item, int):
                position = item
            elif isinstance(item, str) and len(item) == 1 and item.isalpha():
                letter = item
        
        return {"type": "positional", "letter": letter, "position": position}
    
    # Qualitative
    def qual_with_count(self, items):
        qual_word = None
        count_value = None
        count_field = "word_count"
        
        for item in items:
            if isinstance(item, str):
                if item in ["palindromic", "palindrome", "mirror", "symmetric", "symmetrical"]:
                    qual_word = item
                elif item in ["word", "words"]:
                    count_field = "word_count"
                elif item in ["character", "characters", "char", "chars", "length"]:
                    count_field = "length"
            elif isinstance(item, int):
                count_value = item
        
        result = {"type": "qualitative", "qual": qual_word or "palindrome"}
        if count_value is not None:
            result[count_field] = count_value
        
        return result
    
    def qual_with_verb(self, items):
        qual_word = None
        count_value = None
        count_field = "word_count"
        positional_data = None
        
        for item in items:
            if isinstance(item, dict) and item.get("type") == "positional":
                positional_data = item
            elif isinstance(item, str):
                if item in ["palindromic", "palindrome", "mirror", "symmetric", "symmetrical"]:
                    qual_word = item
                elif item in ["word", "words"]:
                    count_field = "word_count"
                elif item in ["character", "characters", "char", "chars", "length"]:
                    count_field = "length"
            elif isinstance(item, int):
                count_value = item
        
        result = {"type": "qualitative", "qual": qual_word or "palindrome"}
        
        # If positional data exists, return compound condition
        if positional_data:
            return {
                "type": "compound",
                "conditions": [
                    result,
                    {"op": "and", "condition": {"type": "contains", "neg": False, "subtype": "positional", **positional_data}}
                ]
            }
        elif count_value is not None:
            result[count_field] = count_value
        
        return result
    
    def qual_simple(self, items):
        qual_word = None
        count_value = None
        
        for item in items:
            if isinstance(item, str):
                if item in ["palindromic", "palindrome", "mirror", "symmetric", "symmetrical"]:
                    qual_word = item
            elif isinstance(item, int):
                count_value = item
        
        result = {"type": "qualitative", "qual": qual_word or "palindrome"}
        if count_value is not None:
            result["word_count"] = count_value
        
        return result
    
    def qual_condition(self, items):
        return items[0] if items else {"type": "qualitative", "qual": "palindrome"}
    
    # Other conditions
    def comparison_condition(self, items):
        number = None
        keyword = None
        adj = None
        operator = None
        
        for item in items:
            if isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                    keyword = item
                elif item in [">", ">=", "<", "<=", "==", "=", "!="]:
                    operator = item
                else:
                    adj = item
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        
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
                "equal_to": "==",
                "not_longer_than": "<=",
                "not_shorter_than": ">="
            }
            op = op_map.get(adj, "==")
        else:
            op = "=="
        
        return {"type": "comparison", "field": field, "op": op, "value": number}
    
    def element_condition(self, items):
        neg = False
        number = None
        keyword = None
        alpha = None
        letter = None
        positional_data = None
        
        for item in items:
            if item is True:
                neg = True
            elif isinstance(item, dict) and item.get("type") == "positional":
                positional_data = item
            elif isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in ["have", "has", "having", "contain", "contains", 
                           "containing", "include", "includes", "including"]:
                    pass
                elif item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                    keyword = item
                elif item in ["vowel", "vowels", "consonant", "consonants", "alphabet", "alphabets"]:
                    alpha = item
                elif len(item) == 1 and item.isalpha():
                    letter = item
        
        result = {"type": "contains", "neg": neg}
        
        if positional_data:
            result["subtype"] = "positional"
            result.update(positional_data)
        elif number and keyword:
            field = "word_count" if keyword in ["word", "words"] else "length"
            result["subtype"] = "count"
            result["field"] = field
            result["value"] = number
        elif alpha:
            result["subtype"] = "char_class"
            result["char_class"] = alpha
        elif letter:
            result["subtype"] = "letter"
            result["letter"] = letter
        
        return result
    
    def range_condition(self, items):
        numbers = [item for item in items if isinstance(item, int)]
        keyword = next((item for item in items if isinstance(item, str) and 
                       item in ["word", "words", "character", "characters", "char", "chars", "length"]), None)
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        return {
            "type": "range",
            "field": field,
            "min": numbers[0] if len(numbers) > 0 else 0,
            "max": numbers[1] if len(numbers) > 1 else 999
        }
    
    def length_phrase(self, items):
        number = None
        adj = None
        operator = None
        keyword = None
        
        for item in items:
            if isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in [">", ">=", "<", "<=", "==", "=", "!="]:
                    operator = item
                elif item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                    keyword = item
                else:
                    adj = item
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        
        if operator:
            op = operator if operator != "=" else "=="
        elif adj:
            op_map = {
                "longer": ">", "shorter": "<", "greater": ">", "less": "<",
                "more": ">", "fewer": "<", "over": ">", "under": "<",
                "exactly": "==", "just": "==", "only": "==",
                "at_least": ">=", "at_most": "<=",
                "longer_than": ">", "shorter_than": "<",
                "greater_than": ">", "less_than": "<",
                "more_than": ">", "fewer_than": "<",
                "not_longer_than": "<=", "not_shorter_than": ">="
            }
            op = op_map.get(adj, "==")
        else:
            op = "=="
        
        return {"type": "comparison", "field": field, "op": op, "value": number}
    
    def det_number_keyword_head(self, items):
        number = None
        keyword = None
        adj = None
        
        for item in items:
            if isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                    keyword = item
                elif item in ["long", "short", "exactly", "just", "only"]:
                    adj = item
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        op_map = {"long": ">=", "short": "<=", "exactly": "==", "just": "==", "only": "=="}
        op = op_map.get(adj, "==")
        
        return {"type": "comparison", "field": field, "op": op, "value": number}
    
    def head_only(self, items):
        return {"type": "all"}
    
    def compound_condition(self, items):
        conditions = []
        last_op = "and"
        
        for item in items:
            if isinstance(item, str) and item in ["and", "or", "but"]:
                last_op = "and" if item == "but" else item
            elif isinstance(item, dict):
                conditions.append({"op": last_op, "condition": item})
                last_op = "and"
        
        if conditions:
            first_cond = conditions[0]["condition"]
            rest = conditions[1:]
            
            if rest:
                return {"type": "compound", "conditions": [first_cond] + rest}
            else:
                return first_cond
        
        return {"type": "all"}
    
    def single_condition(self, items):
        return items[0] if items else {"type": "all"}
    
    def start(self, items):
        return items[0] if items else {"type": "all"}