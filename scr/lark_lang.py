lang = r"""
start: query

?query: compound_condition
      | single_condition

compound_condition: single_condition ((conj | comma) single_condition)+

single_condition: comparison_condition
                | element_condition  
                | range_condition
                | length_phrase
                | qual_condition
                | det_number_keyword_head
                | head_only

// Comparisons with multi-word operators
comparison_condition: det? head? multi_word_adj number keyword
                    | det? head? adj number keyword
                    | det? head? operator number keyword?
                    | number keyword adj
                    | multi_word_adj number keyword
                    | adj number keyword

// Multi-word adjectives like "at least", "longer than"
multi_word_adj: "at" "least"        -> at_least
              | "at" "most"         -> at_most
              | "longer" "than"     -> longer_than
              | "shorter" "than"    -> shorter_than
              | "greater" "than"    -> greater_than
              | "less" "than"       -> less_than
              | "more" "than"       -> more_than
              | "fewer" "than"      -> fewer_than
              | "equal" "to"        -> equal_to

// Element conditions with better letter handling
element_condition: det? head? neg? verb_elem number keyword
                 | det? head? neg? verb_elem alpha
                 | det? head? neg? verb_elem det? "letter" letter
                 | det? head? neg? verb_elem letter

// Range: "between 3 and 10 characters"
range_condition: det? head? "between" number "and" number keyword?

// Length phrases: "of length 10", "with length under 5"  
length_phrase: det? head? prep "length" multi_word_adj number keyword?
             | det? head? prep "length" adj number keyword?
             | det? head? prep "length" operator number keyword?

// Qualitative: "palindromic strings", "palindrome"
qual_condition: det? special_number? qual_adj head?
              | det? number? qual_adj head?
              | det? qual_adj head?

// Number patterns: "10 character long string", "all 5 characters strings"
det_number_keyword_head: det? number keyword adj? head?

// Just a head noun
head_only: det? head

// Terminals
number: NUMBER | special_number -> numeric_number
special_number: one | two     
one: "single"         -> one
   | "monoword"       -> one  
   | "mono"           -> one
two: "double"         -> two
   | "pair"           -> two
   | "couple"         -> two

keyword: "character" | "characters" | "char" | "chars"
       | "word" | "words" 
       | "length"

alpha: "vowel" | "vowels" | "consonant" | "consonants" 
     | "alphabet" | "alphabets"

letter: /[a-z]/

det: "all" | "any" | "each" | "every" | "the" | "a" | "an"

head: "string" | "strings" | "text" | "texts" 
    | "phrase" | "phrases" | "entry" | "entries"

adj: "longer" | "shorter" | "greater" | "less" 
   | "more" | "fewer" | "exactly" | "just" 
   | "only" | "precisely" | "about" | "over" | "under"
   | "long" | "short"

verb_elem: "have" | "has" | "having" 
         | "contain" | "contains" | "containing"
         | "include" | "includes" | "including"
         | "with"

neg: "not" | "without" | "excluding" | "no"

operator: ">" | ">=" | "<" | "<=" | "==" | "=" | "!="

qual_adj: "palindromic" | "palindrome" | "mirror" 
        | "symmetric" | "symmetrical"

prep: "of" | "with" | "at" | "in"
conj: "and" | "or" | "but"
comma: ","

%import common.NUMBER
%import common.WS
%ignore WS
"""