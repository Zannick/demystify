lexer grammar Symbols;

/* Symbols and punctuation */

options {
    language = Python;
}

// Literals used in parsing rules don't have to be declared,
// but for reference they are:
// ,:;."'+-*/

// These six are the only things in rules text exempt from being lowercased.
SELF_POSS : 'SELF\'s';
SELF : 'SELF';

PARENT_POSS : 'PARENT\'s';
PARENT : 'PARENT';

REFBYNAME : 'NAME_' ( 'A'..'Z' | 'a'..'z' | '_' | '\u00c6' | '\u00e6' )+;

// Basic lands have only one letter as their rules text
BASIC_MANA_SYM : WUBRG_u;

// Chop off brackets for the symbols whose text we'll need later.
// Unfortunately we have to do our checking against hybrid alternatives
// elsewhere.

MANA_SYM
    : '{(' ( WUBRG | DIGIT_SYM | SNOW_SYM ) '/' WUBRGP ')}'
      { $text = $text[2:-2].upper() }
    | '{' ( WUBRG | DIGIT_SYM | SNOW_SYM ) ( '}' | '/' WUBRGP '}' )
      { $text = $text[1:-1].upper() };

// Mana cost symbols are BASIC_MANA_SYM, NUMBER_SYM,
// MC_HYBRID_SYM, and MC_VAR_SYM.
// These use all caps mana symbols and should never be seen in text.

MC_HYBRID_SYM
    : '(' ( WUBRG_u | DIGIT_SYM | SNOW_u ) '/' ( WUBRGP_u | SNOW_u ) ')'
      { $text = $text[1:-1] };

MC_VAR_SYM : 'X'..'Z' ;

// Appearance in rules text
PHYREXIA_SYM : '{p}' { $text = 'P' };

VAR_MANA_SYM : '{' ('x'..'z') '}' { $text = $text[1:-1].upper() };

TAP_SYM : '{t}' { $text = 'T' };

UNTAP_SYM : '{q}' { $text = 'Q' };

// TODO: Cast to int
NUMBER_SYM : DIGIT_SYM;

VAR_SYM : 'x'..'z' { $text = $text.upper() };

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

fragment WUBRGP : ( WUBRG | 'p' );

fragment SNOW_u : 'S';

fragment WUBRG_u : ('W'|'U'|'B'|'R'|'G');

fragment WUBRGP_u : ( WUBRG_u | 'P' );

fragment DIGIT_SYM : ('1'..'9' '0'..'9') | ('0'..'9');
