parser grammar pt;

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

/* Power/toughness related rules. */

// This rule is used for printed p/t, p/t setting abilities,
// and p/t modifying abilities.

pt : ( p=pt_signed_part | p=pt_part ) DIV_SYM ( t=pt_signed_part | t=pt_part )
     -> ^( PT $p $t );

pt_signed_part : PLUS_SYM pt_part -> ^( PLUS pt_part )
               | MINUS_SYM pt_part -> ^( MINUS pt_part );

pt_part : NUMBER_SYM
        | VAR_SYM -> ^( VAR VAR_SYM )
        | STAR_SYM
        | a=NUMBER_SYM ( b=PLUS_SYM | b=MINUS_SYM ) c=STAR_SYM
          { plog.debug('Ignoring p/t value "{} {} {}" in {}; '
                       'deferring actual p/t calculation to rules text.'
                       .format($a.text, $b.text, $c.text,
                               self.getCardState())) }
          -> STAR_SYM;
