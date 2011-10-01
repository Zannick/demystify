lexer grammar Symbols;

/* Symbols and punctuation */

options {
    language = Python;
}

// hack to allow unicode
@header {
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
}

// TODO: Need to chop off the '}' from the token values?

MANA_SYM : '{' ( WUBRG | DIGIT_SYM+ | SNOW_SYM ) '}';

// Basic lands have only one letter as their rules text
BASIC_MANA_SYM : WUBRG;

// The last of these takes precedence over the REMINDER_TEXT rule.
HYBRID_MANA_SYM
    : '{' ( WUBRG | DIGIT_SYM+ | SNOW_SYM ) '/' WUBRGP '}'
    | '{(' ( WUBRG | DIGIT_SYM+ | SNOW_SYM ) '/' WUBRGP ')}'
    | '(' ( WUBRG | DIGIT_SYM+ | 'S' ) '/' ( WUBRGP | 'S' ) ')';

// Appearance in rules text
PHYREXIA_SYM : 'P';

VAR_SYM : '{' ('X'..'Z') '}';

TAP_SYM : '{T}';

UNTAP_SYM : '{Q}';

// TODO: Cast to int
NUMBER_SYM : DIGIT_SYM+;

VAR : 'X'..'Z';

MDASH : ( '\u2014' | '--' );

SELF : 'SELF';

SELF_POSS : 'SELF\'s';

PARENT : 'PARENT';

PARENT_POSS : 'PARENT\'s';

REFBYNAME : 'NAME_' '\w'+;

NON : 'non' '-'?;

// Literals used in parsing rules don't have to be declared,
// but for reference they are:
// ,:;."'+-*/

// TODO: Determine landwalk type.
// TODO: Avoid collision with "planeswalk" keyword.
// TODO: landwalk as a parser rule instead of a token
//LANDWALK : '\w' ('\w' | ' ')* '\w' 'walk' 's'? '\b';

// TODO: Determine cycling type or make this a parser rule.
TYPECYCLING : '\w' ('\w' | ' ')* '\w' 'cycling';


WS : ( ' ' | '\t' | '\n' ) {$channel=HIDDEN;} ;

// I have no idea why the snow mana symbol appears as 'S}i' in gatherer.
fragment SNOW_SYM : 'S' '}'? 'i'?;

fragment WUBRG : ('W'|'U'|'B'|'R'|'G');

fragment WUBRGP : ( WUBRG | 'P' );

fragment DIGIT_SYM : '0'..'9';
