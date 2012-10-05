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

// Unfortunately we can't have the lexer rule match just a single quote
// in some cases but not others, so we use a parser rule to handle this.
poss : APOS_S | S_APOS | SQUOTE ;

// Similarly, APOS_S sometimes means "is".
is_ : IS | APOS_S ;
