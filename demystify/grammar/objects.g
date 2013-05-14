parser grammar objects;

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

/* Common object properties, such as types, colors, and statuses. */

adj_list : a=adjective ( COMMA! ( ( b+=adjective | c+=noun ) COMMA! )+ )?
           conj^ ( d=adjective | e=noun )
           // Currently only Soldevi Adnate?
           { if $e.text or $c:
                self.emitDebugMessage('Mixed list: {}'.format(
                    ', '.join([$a.text]
                              + [adj.text for adj in ($b or []) + ($c or [])]
                              + [$d.text or $e.text])))
           };

noun_list : noun ( COMMA! ( noun COMMA! )+ )? conj^ noun ;

// Adjectives

adjective : NON? ( supertype | color | color_spec | status )
            -> {$NON}? ^( NON[] supertype? color? color_spec? status? )
            -> supertype? color? color_spec? status? ;

color : WHITE | BLUE | BLACK | RED | GREEN ;
color_spec : COLORED | COLORLESS | MONOCOLORED | MULTICOLORED ;
status : TAPPED
       | UNTAPPED
       | EXILED
       | KICKED
       | SUSPENDED
       | ATTACKING
       | BLOCKING
       | BLOCKED
       | UNBLOCKED
       | FACE_UP
       | FACE_DOWN
       | FLIPPED
       | REVEALED
       ;

// Nouns

noun : NON? ( type | obj_subtype | obj_type )
       -> {$NON}? ^( NON[] type? obj_subtype? obj_type? )
       -> type? obj_subtype? obj_type? ;

/* Types, supertypes, subtypes, and other miscellaneous types. */

// For use parsing a full typeline.
typeline : supertypes? types ( MDASH subtypes )?
           -> ^( TYPELINE supertypes? types subtypes? );

supertypes : supertype+ -> ^( SUPERTYPES supertype+ );

supertype : BASIC | LEGENDARY | SNOW | WORLD | ONGOING ;

// Card types

types : tribal_type? spell_type -> ^( TYPES tribal_type? spell_type )
      | tribal_type n=noncreature_perm_types -> ^( TYPES tribal_type $n )
      | permanent_types -> ^( TYPES permanent_types )
      | other_type -> ^( TYPES other_type )
      ;

type : permanent_type | spell_type | other_type | tribal_type ;

permanent_types : permanent_type+ ;
permanent_type : noncreature_perm_type | creature_type ;

creature_type : CREATURE ;

noncreature_perm_types : noncreature_perm_type+ ;
noncreature_perm_type : ARTIFACT | ENCHANTMENT | LAND | PLANESWALKER ;

spell_type : INSTANT | SORCERY ;

other_type : PLANE | SCHEME | VANGUARD ;

tribal_type : TRIBAL ;

// subtypes
subtypes : obj_subtype+ -> ^( SUBTYPES obj_subtype+ );

// Object types

obj_type : OBJECT | ABILITY | CARD | PERMANENT | SOURCE | SPELL | TOKEN ;

// Player types

player_type : PLAYER | TEAMMATE | OPPONENT | CONTROLLER | OWNER | BIDDER ;

/* Power/toughness */

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
