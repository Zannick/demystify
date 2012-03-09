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
             | max_among
             ;

object_count : THE NUMBER OF 
               ( properties -> ^( COUNT properties ) 
               | base_counter_set ON ( properties | ref_object )
                 -> ^( COUNT base_counter_set properties? ref_object? )
               );

// ref_object is usually plural in this case
max_among : THE ( HIGHEST | GREATEST ) int_prop
            AMONG ( properties | ref_object | player_subset )
            -> ^( MAX int_prop properties? ref_object? player_subset? );

// TODO: for each basic land type among lands you control. (Draco)
for_each : FOR EACH
           ( properties -> ^( PER properties ) 
           | base_counter_set ON ( properties | ref_object )
             -> ^( PER base_counter_set properties? ref_object? )
           );

multiplier : HALF -> ^( NUMBER NUMBER["1/2"] )
           | THIRD -> ^( NUMBER NUMBER["1/3"] )
           | TWICE -> ^( NUMBER NUMBER["2"] )
           | integer TIMES -> integer
           ;

// Specifically for talking about amounts of life.
magic_life_number : integer LIFE -> ^( LIFE[] integer )
                  | multiplier player_poss LIFE
                    ( ',' ROUNDED ( u=UP | d=DOWN ) )?
                      -> ^( MULT multiplier ^( LIFE[] player_poss )
                                 ^( ROUND $u? $d? )? )
                  | LIFE EQUAL TO magic_number -> ^( LIFE[] magic_number )
                  ;
