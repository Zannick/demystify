parser grammar misc;

/* Miscellaneous rules. */

conj : AND | OR | AND_OR ;

/* Numbers and quantities. */

number : integer
         ( OR integer -> ^( OR integer+ )
         | -> integer
         )
       | ( ALL | EACH | EVERY ) -> ^( NUMBER ALL )
       | ANY ( c=number_word -> ^( NUMBER[] $c )
             | NUMBER OF -> ^( NUMBER[] ANY )
             | -> ^( NUMBER[] NUMBER[$ANY, "1"] )
             )
       | A SINGLE? -> ^( NUMBER NUMBER[$A, "1"] )
       | NO -> ^( NUMBER NUMBER[$NO, "0"] );

/* Not sure whether this should go in integer, or number, or somewhere else.
   Most references to "no more than" or "more than" are setting a maximum
   value, eg. "can't be blocked by more than one creature".
        | NO? ( MORE | GREATER ) THAN ( s=NUMBER_SYM | w=number_word )
          -> {$NO}? ^( NUMBER ^( LEQ $s? $w? ) )
          -> ^( NUMBER ^( GT $s? $w? ) )
*/
integer : ( s=NUMBER_SYM | w=number_word )
          ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ $s? $w? ) )
          | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ $s? $w? ) )
          | -> ^( NUMBER $s? $w? )
          )
        | AT LEAST ( s=NUMBER_SYM | w=number_word )
          -> ^( NUMBER ^( GEQ $s? $w? ) )
        | EXACTLY ( s=NUMBER_SYM | w=number_word )
          -> ^( NUMBER ^( EQUAL $s? $w? ) )
        | b=VAR_SYM ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ ^( VAR $b ) ) )
                    | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ ^( VAR $b ) ) )
                    | -> ^( NUMBER ^( VAR $b ) )
                    )
        | ANY AMOUNT OF -> ^( NUMBER ANY )
        ;

// TODO: more player stuff.
player_poss : YOUR ;

