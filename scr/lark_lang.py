lang = r"""
start: query

?query: compound_condition
      | single_condition

compound_condition: single_condition ((conj | comma) single_condition)+

single_condition: qual_condition
                | comparison_condition
                | element_condition  
                | range_condition
                | length_phrase
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
              | "not" "longer" "than"   -> not_longer_than
              | "not" "shorter" "than"  -> not_shorter_than

// Element conditions - FIXED to handle letters properly
element_condition: det? head? rel_pro? neg? verb_elem number keyword
                 | det? head? rel_pro? neg? verb_elem alpha
                 | det? head? rel_pro? neg? verb_elem "letter" letter
                 | det? head? rel_pro? neg? verb_elem letter

// Range: "between 3 and 10 characters"
range_condition: det? head? "between" number "and" number keyword?

// Length phrases: "of length 10", "with length under 5"  
length_phrase: det? head? prep "length" multi_word_adj number keyword?
             | det? head? prep "length" adj number keyword?
             | det? head? prep "length" operator number keyword?
             
// Qualitative: "palindromic strings", "all single palindrome", "all 2 word palindromes"
// Pattern 1: "all 2 word palindrome", "all double words palindrome"  
qual_with_count: det? number keyword qual_adj head?
               | det? word_number keyword qual_adj head?

// Pattern 2: "all palindrome with 2 words", "palindrome containing single word"
qual_with_verb: det? qual_adj head? (rel_pro? verb_elem | prep) number keyword
              | det? qual_adj head? (rel_pro? verb_elem | prep) word_number keyword?
              | det? qual_adj (rel_pro? verb_elem | prep) number keyword head?
              | det? qual_adj head? (rel_pro? verb_elem | prep) det? number? keyword?

// Pattern 3: "all palindromic single words", "all single palindrome"
qual_condition: qual_with_count
              | qual_with_verb
              | det? word_number qual_adj head?
              | det? qual_adj word_number head?
              | det? number qual_adj head?
              | det? qual_adj number head?
              | det? qual_adj head?

// Number patterns: "10 character long string", "all 5 characters strings"
det_number_keyword_head: det? number keyword adj? head?

// Just a head noun
head_only: det? head

// Terminals
number: NUMBER           -> numeric_number
      | word_number      -> word_number_val

word_number: "single"    -> one
           | "monoword"  -> one  
           | "mono"      -> one
           | "double"    -> two
           | "pair"      -> two
           | "couple"    -> two

cardinal: /d+(st|nd|rd|th)/
           
alpha: "vowel" | "vowels" | "consonant" | "consonants" 
     | "alphabet" | "alphabets" | cardinal_alpha

cardinal_alpha: cardinal alpha

keyword: "character" | "characters" | "char" | "chars"
       | "word" | "words" 
       | "length" | alpha

letter: /[a-z]/

det: "all" | "any" | "each" | "every" | "the" | "a" | "an"

head: "string" | "strings" | "text" | "texts" 
    | "phrase" | "phrases" | "entry" | "entries" | "word" | "words"

adj: "longer" | "shorter" | "greater" | "less" 
   | "more" | "fewer" | "exactly" | "just" 
   | "only" | "precisely" | "about" | "over" | "under"
   | "long" | "short"

verb_elem: "have" | "has" | "having" 
         | "contain" | "contains" | "containing"
         | "include" | "includes" | "including"

neg: "not" | "without" | "excluding" | "no"

operator: ">" | ">=" | "<" | "<=" | "==" | "=" | "!="

qual_adj: "palindromic" | "palindrome" | "mirror" 
        | "symmetric" | "symmetrical"

prep: "of" | "with" | "at" | "in"
rel_pro: "that" | "which" | "whose"
conj: "and" | "or" | "but"
comma: ","

%import common.NUMBER
%import common.WS
%ignore WS
"""