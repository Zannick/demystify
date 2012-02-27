parser grammar math;

/* Mathematical constructs and calculations. */

comparison : ( EQUAL TO OR )? ( MORE | GREATER ) THAN magic_number
             -> {$EQUAL.text}? ^( GEQ magic_number )
             -> ^( GT magic_number )
           | ( FEWER | LESS ) THAN ( OR EQUAL TO )? magic_number
             -> {$EQUAL.text}? ^( LEQ magic_number )
             -> ^( LT magic_number )
           | EQUAL TO magic_number -> ^( EQUAL[] magic_number )
           | integer
           ;

magic_number : integer
             | object_count
             ;

object_count : THE NUMBER OF 
               ( properties -> ^( COUNT properties ) 
               | counter_subset ON properties
                 -> ^( COUNT counter_subset properties )
               );

multiplier : HALF -> ^( NUMBER NUMBER["1/2"] )
           | THIRD -> ^( NUMBER NUMBER["1/3"] )
           | TWICE -> ^( NUMBER NUMBER["2"] )
           | integer TIMES -> integer
           ;

magic_life_number : integer LIFE^
                  | multiplier player_poss LIFE
                    ( ',' ROUNDED ( u=UP | d=DOWN ) )?
                      -> ^( MULT multiplier ^( LIFE player_poss )
                                 ^( ROUND $u? $d? )? )
                  | LIFE EQUAL TO magic_number -> ^( LIFE magic_number )
                  ;
