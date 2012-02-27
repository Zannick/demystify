parser grammar misc;

/* Miscellaneous rules. */

conj : AND | OR | AND_OR ;

/* Numbers and quantities. */

number : integer
       | ( ALL | EACH | EVERY ) -> ^( NUMBER ALL )
       | ANY ( c=number_word -> ^( NUMBER[] $c )
             | NUMBER OF -> ^( NUMBER[] ANY )
             | -> ^( NUMBER[] NUMBER[$ANY, "1"] )
             )
       | A SINGLE? -> ^( NUMBER NUMBER[$A, "1"] )
       | NO -> ^( NUMBER NUMBER[$NO, "0"] );

integer : ( s=NUMBER_SYM | w=number_word )
          ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ $s? $w? ) )
          | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ $s? $w? ) )
          | -> ^( NUMBER $s? $w? )
          )
        | b=VAR_SYM ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ ^( VAR $b ) ) )
                    | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ ^( VAR $b ) ) )
                    | -> ^( NUMBER ^( VAR $b ) )
                    )
        | ANY AMOUNT OF -> ^( NUMBER ANY )
        ;

// TODO: more player stuff.
player_poss : YOUR ;

