parser grammar math;

// This file is part of Demystify.
// 
// Demystify: a Magic: The Gathering parser
// Copyright (C) 2012 Benjamin S Wolf
// 
// Demystify is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 3 of the License,
// or (at your option) any later version.
// 
// Demystify is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

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
            AMONG ( properties | ref_object | player_group )
            -> ^( MAX int_prop properties? ref_object? player_group? );

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
