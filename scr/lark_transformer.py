from lark import Transformer

class NLTransformer(Transformer):
    
    # Numbers
    def numeric_number(self, items):
        return int(items[0])
    
    def word_number_val(self, items):
        return items[0]
    
    def one(self, _):
        return 1
    
    def two(self, _):
        return 2
    
    # Multi-word adjectives
    def at_least(self, _):
        return "at_least"
    
    def at_most(self, _):
        return "at_most"
    
    def longer_than(self, _):
        return "longer_than"
    
    def shorter_than(self, _):
        return "shorter_than"
    
    def greater_than(self, _):
        return "greater_than"
    
    def less_than(self, _):
        return "less_than"
    
    def more_than(self, _):
        return "more_than"
    
    def fewer_than(self, _):
        return "fewer_than"
    
    def equal_to(self, _):
        return "equal_to"
    
    def not_longer_than(self, _):
        return "not_longer_than"
    
    def not_shorter_than(self, _):
        return "not_shorter_than"
    
    # Helpers to extract strings
    def _extract_str(self, items):
        return str(items[0]) if items else None
    
    def head(self, items):
        return self._extract_str(items)
    
    def keyword(self, items):
        return self._extract_str(items)
    
    def adj(self, items):
        return self._extract_str(items)
    
    def multi_word_adj(self, items):
        return items[0] if items else None
    
    def verb_elem(self, items):
        return self._extract_str(items)
    
    def alpha(self, items):
        return self._extract_str(items)
    
    def letter(self, items):
        return self._extract_str(items)
    
    def operator(self, items):
        return self._extract_str(items)
    
    def qual_adj(self, items):
        return self._extract_str(items)
    
    def word_number(self, items):
        return items[0]
    
    def neg(self, items):
        return True
    
    def conj(self, items):
        return self._extract_str(items)
    
    def qual_with_count(self, items):
        """Qualitative with explicit word/character count: '2 word palindrome'"""
        qual_word = None
        count_value = None
        count_field = "word_count"  # default
        
        for item in items:
            if isinstance(item, str):
                if item in ["palindromic", "palindrome", "mirror", "symmetric", "symmetrical"]:
                    qual_word = item
                elif item in ["word", "words"]:
                    count_field = "word_count"
                elif item in ["character", "characters", "char", "chars", "length"]:
                    count_field = "length"
                elif item in ["double", "pair", "couple"]:
                    count_value = 2
                    print(item)
                elif item in ["single", "monoword", "mono"]:
                    count_value = 1
                    print(item)
                print(count_value)
            elif isinstance(item, int):
                count_value = item
        print("count is none")
        result = {"type": "qualitative", "qual": qual_word or "palindrome"}
        if count_value is not None:
            result[count_field] = count_value
        
        return result
    
    def qual_with_verb(self, items):
        """Qualitative with verb: 'palindrome containing 2 words'"""
        qual_word = None
        count_value = None
        count_field = "word_count"  # default
        
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
    
    def qual_condition(self, items):
        """Qualitative conditions: 'palindromic', 'single palindrome'"""
        qual_word = None
        count_value = None
        
        for item in items:
            if isinstance(item, str) and item in [
                "palindromic", "palindrome", "mirror", "symmetric", "symmetrical"
            ]:
                qual_word = item
            elif isinstance(item, int):
                count_value = item
        
        result = {"type": "qualitative", "qual": qual_word or "palindrome"}
        if count_value is not None:
            result["word_count"] = count_value
        
        return result
    
    
    
    def comparison_condition(self, items):
        """Parse comparison conditions"""
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
                elif item in ["longer", "shorter", "greater", "less", "more", "fewer", 
                             "exactly", "just", "only", "precisely", "about", "over", "under", "long", "short",
                             "at_least", "at_most", "longer_than", "shorter_than", "greater_than", 
                             "less_than", "more_than", "fewer_than", "equal_to",
                             "not_longer_than", "not_shorter_than"]:
                    adj = item
        
        # Determine field
        field = "length"
        if keyword in ["word", "words"]:
            field = "word_count"
        
        # Determine operator - expanded map
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
        
        return {
            "type": "comparison",
            "field": field,
            "op": op,
            "value": number
        }
    
    def element_condition(self, items):
        """Parse element/containment conditions"""
        neg = False
        number = None
        keyword = None
        alpha = None
        letter = None
        
        for item in items:
            if item is True:
                neg = True
            elif isinstance(item, int):
                number = item
            elif isinstance(item, str):
                if item in ["have", "has", "having", "contain", "contains", 
                           "containing", "include", "includes", "including"]:
                    pass  # verb, just skip
                elif item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                    keyword = item
                elif item in ["vowel", "vowels", "consonant", "consonants", "alphabet", "alphabets"]:
                    alpha = item
                elif len(item) == 1 and item.isalpha():
                    letter = item
        
        result = {"type": "contains", "neg": neg}
        
        if number and keyword:
            # "contain 3 words"
            field = "word_count" if keyword in ["word", "words"] else "length"
            result["subtype"] = "count"
            result["field"] = field
            result["value"] = number
        elif alpha:
            # "contain vowels"
            result["subtype"] = "char_class"
            result["char_class"] = alpha
        elif letter:
            # "contain letter a"
            result["subtype"] = "letter"
            result["letter"] = letter
        
        return result
    
    def range_condition(self, items):
        """Parse range conditions: between X and Y"""
        numbers = [item for item in items if isinstance(item, int)]
        keyword = None
        for item in items:
            if isinstance(item, str) and item in ["word", "words", "character", "characters", "char", "chars", "length"]:
                keyword = item
                break
        
        field = "word_count" if keyword in ["word", "words"] else "length"
        return {
            "type": "range",
            "field": field,
            "min": numbers[0] if len(numbers) > 0 else 0,
            "max": numbers[1] if len(numbers) > 1 else 999
        }
    
    def length_phrase(self, items):
        """Parse length phrases: 'of length 10', 'with length longer than 2 words'"""
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
                elif item in ["longer", "shorter", "greater", "less", "more", "fewer", 
                             "exactly", "just", "only", "over", "under",
                             "at_least", "at_most", "longer_than", "shorter_than", 
                             "greater_than", "less_than", "more_than", "fewer_than",
                             "not_longer_than", "not_shorter_than"]:
                    adj = item
        
        # Determine field based on keyword if present
        if keyword in ["word", "words"]:
            field = "word_count"
        else:
            field = "length"
        
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
        
        return {
            "type": "comparison",
            "field": field,
            "op": op,
            "value": number
        }
    
    def det_number_keyword_head(self, items):
        """Parse 'det? number keyword adj? head?' patterns like 'all 5 characters strings'"""
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
        
        return {
            "type": "comparison",
            "field": field,
            "op": op,
            "value": number
        }
    
    def head_only(self, items):
        """Just return all strings (no filter)"""
        return {"type": "all"}
    
    def compound_condition(self, items):
        """Handle multiple conditions with and/or"""
        conditions = []
        last_op = "and"  # default
        
        for item in items:
            if isinstance(item, str) and item in ["and", "or", "but"]:
                last_op = "and" if item == "but" else item
            elif isinstance(item, dict):
                conditions.append({"op": last_op, "condition": item})
                last_op = "and"
        
        # First condition has no operator prefix
        if conditions and len(conditions) > 0:
            first_cond = conditions[0]["condition"]
            rest = conditions[1:] if len(conditions) > 1 else []
            
            if rest:
                return {"type": "compound", "conditions": [first_cond] + rest}
            else:
                return first_cond
        
        return {"type": "all"}
    
    def single_condition(self, items):
        """Pass through single conditions"""
        return items[0] if items else {"type": "all"}
    
    def start(self, items):
        """Top level"""
        return items[0] if items else {"type": "all"}



