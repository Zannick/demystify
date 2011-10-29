lexer grammar Symbols;

/* Symbols and punctuation */

options {
    language = Python;
}

tokens {
    MANA_SYM;
    BASIC_MANA_SYM;
    PHYREXIA_SYM;
    VAR_SYM;
    TAP_SYM;
    UNTAP_SYM;
    NUMBER_SYM;
    VAR;
    MDASH;
    SELF;
    SELF_POSS;
    PARENT;
    PARENT_POSS;
    REFBYNAME;
    WALK;
    WS;
}

// Literals used in parsing rules don't have to be declared,
// but for reference they are:
// ,:;."'+-*/

// These six are the only things exempt from being lowercased.
SELF_POSS : 'SELF\'s';
SELF : 'SELF';

PARENT_POSS : 'PARENT\'s';
PARENT : 'PARENT';

REFBYNAME : 'NAME_' ( 'A'..'Z' | 'a'..'z' | '_' | '\u00c6' | '\u00e6' )+;

// Basic lands have only one letter as their rules text
BASIC_MANA_SYM : ('W'|'U'|'B'|'R'|'G');

// TODO: Need to chop off the '}' from the token values?

MANA_SYM
    : '{(' ( WUBRG | DIGIT_SYM | SNOW_SYM ) '/' WUBRGP ')}'
      { $text = $text[2:-2].split('/') }
    | '{' ( WUBRG | DIGIT_SYM | SNOW_SYM ) ( '}' | '/' WUBRGP '}' )
      { $text = $text[1:-1].split('/') }
    | '(' ( WUBRG | DIGIT_SYM | SNOW_SYM ) '/' ( WUBRGP | SNOW_SYM ) ')'
      { $text = $text[1:-1].split('/') };

// Appearance in rules text
PHYREXIA_SYM : '{p}';

VAR_SYM : '{' ('x'..'z') '}';

TAP_SYM : '{t}';

UNTAP_SYM : '{q}';

// TODO: Cast to int
NUMBER_SYM : DIGIT_SYM;

VAR : 'x'..'z';

MDASH : ( '\u2014' | '--' );

// TODO: Determine landwalk type.
// TODO: Avoid collision with "planeswalk" keyword.
// TODO: landwalk as a parser rule instead of a token
//LANDWALK : '\w' ('\w' | ' ')* '\w' 'walk' 's'? '\b';
WALK : 'walk';

// TODO: Determine cycling type or make this a parser rule.
//TYPECYCLING : '\w' ('\w' | ' ')* '\w' 'cycling';


WS : ( ' ' | '\t' | '\n' ) {$channel=HIDDEN;} ;

fragment SNOW_SYM : 's';

fragment WUBRG : ('w'|'u'|'b'|'r'|'g');

fragment WUBRGP : ( WUBRG | 'p');

fragment DIGIT_SYM : ('1'..'9' '0'..'9') | ('0'..'9');
