lang = r"""
start: query

?query: compound_condition
      | single_condition

compound_condition: single_condition ((conj | comma) single_condition)*

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

// Multi-word adjectives
multi_word_adj: "at" "least"             -> at_least
              | "at" "most"              -> at_most
              | "longer" "than"          -> longer_than
              | "shorter" "than"         -> shorter_than
              | "greater" "than"         -> greater_than
              | "less" "than"            -> less_than
              | "more" "than"            -> more_than
              | "fewer" "than"           -> fewer_than
              | "equal" "to"             -> equal_to
              | "not" "longer" "than"    -> not_longer_than
              | "not" "shorter" "than"   -> not_shorter_than

// Element conditions with full position support
element_condition: det? head? rel_pro? neg? verb_elem positional_alpha
                 | det? head? rel_pro? neg? verb_elem positional_letter
                 | det? head? rel_pro? neg? verb_elem number keyword
                 | det? head? rel_pro? neg? verb_elem alpha
                 | det? head? rel_pro? neg? verb_elem "letter" letter
                 | det? head? rel_pro? neg? verb_elem letter

// Positional patterns - COMPLETE
positional_alpha: "the"? ordinal alpha
                | "the"? cardinal alpha
                | alpha "at" "the"? "position"? cardinal
                | alpha "at" "the"? cardinal "position"
                | alpha "in" "the"? "position"? cardinal
                | alpha "in" "the"? cardinal "position"

positional_letter: "the"? ordinal letter
                 | "the"? cardinal letter
                 | letter "at" "the"? "position"? cardinal
                 | letter "at" "the"? cardinal "position"
                 | letter "in" "the"? "position"? cardinal
                 | letter "in" "the"? cardinal "position"

// Range
range_condition: det? head? "between" number "and" number keyword?

// Length phrases
length_phrase: det? head? prep "length" multi_word_adj number keyword?
             | det? head? prep "length" adj number keyword?
             | det? head? prep "length" operator number keyword?

// Qualitative conditions - COMPLETE
qual_with_count: det? number keyword qual_adj head?
               | det? word_number keyword qual_adj head?

qual_with_verb: det? qual_adj head? (rel_pro? verb_elem | prep) positional_alpha
              | det? qual_adj head? (rel_pro? verb_elem | prep) positional_letter
              | det? qual_adj head? (rel_pro? verb_elem | prep) number keyword
              | det? qual_adj head? (rel_pro? verb_elem | prep) word_number keyword?
              | det? qual_adj (rel_pro? verb_elem | prep) positional_alpha head?
              | det? qual_adj (rel_pro? verb_elem | prep) positional_letter head?
              | det? qual_adj (rel_pro? verb_elem | prep) number keyword head?
              | det? qual_adj (rel_pro? verb_elem | prep) word_number keyword? head?

qual_simple: det? word_number keyword? qual_adj head?
           | det? qual_adj word_number keyword? head?
           | det? number keyword? qual_adj head?
           | det? qual_adj number keyword? head?
           | det? qual_adj head?

qual_condition: qual_with_count
              | qual_with_verb
              | qual_simple

// Number patterns
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

// Ordinals for positions
ordinal: "first"         -> pos_1
       | "second"        -> pos_2
       | "third"         -> pos_3
       | "fourth"        -> pos_4
       | "fifth"         -> pos_5
       | "sixth"         -> pos_6
       | "seventh"       -> pos_7
       | "eighth"        -> pos_8
       | "ninth"         -> pos_9
       | "tenth"         -> pos_10
       | "last"          -> pos_last

// Cardinals for positions
cardinal: /\d+(st|nd|rd|th)/

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