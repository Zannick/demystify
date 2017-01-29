parser grammar misc;

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

/* Miscellaneous rules. */

/* Special references to related objects. */

haunted_object : THE ( type | obj_type ) ref_object HAUNT
                 -> ^( HAUNTED ref_object );

// TODO: target
ref_object : SELF
           | PARENT
           | IT
           | THEM
             // planeswalker pronouns
           | HIM
           | HER
             // We probably don't actually need to remember what the
             // nouns were here, but keep them in for now.
           | ( ENCHANTED | EQUIPPED | FORTIFIED ) noun+
           | this_ref
           | that_ref
           ;

ref_obj_poss : SELF APOS_S!
             | PARENT APOS_S!
             | ITS -> IT
             | THEIR -> THEM
               // planeswalker pronouns
             | HIS -> HIM
             | HER -> HER
             | ( ENCHANTED | EQUIPPED | FORTIFIED ) noun+ poss!
             | this_ref poss!
             | that_ref poss!
             ;

// eg. this creature, this permanent, this spell.
this_ref : THIS ( type | obj_type ) -> SELF;

that_ref : (THAT | THOSE) ( type | obj_type | obj_subtype )
         -> ^( THAT type? obj_type? obj_subtype? );

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
       | NO -> ^( NUMBER NUMBER[$NO, "0"] )
       ;

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

/* Others */

conj : AND | OR | AND_OR ;

damage : NON COMBAT DAMAGE -> ^( DAMAGE[] NONCOMBAT )
       | COMBAT DAMAGE -> ^( DAMAGE[] COMBAT[] )
       | DAMAGE -> DAMAGE[]
       ;

this_turn : THIS TURN -> ^( THIS[] TURN[] );

// Unfortunately we can't have the lexer rule match just a single quote
// in some cases but not others, so we use a parser rule to handle this.
// Note that the lexer will never match S_APOS since S will be part of
// the preceding token, so APOS_S | SQUOTE is all that's necessary.
poss : APOS_S | SQUOTE ;

// Similarly, APOS_S sometimes means "is".
is_ : IS | APOS_S ;
