parser grammar types;

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

/* Types, supertypes, subtypes, and other miscellaneous types. */

// For use parsing a full typeline.
typeline : supertypes? types ( MDASH subtypes )?
           -> ^( TYPELINE supertypes? types subtypes? );

supertypes : supertype+ -> ^( SUPERTYPES supertype+ );

supertype : ( BASIC | LEGENDARY | SNOW | WORLD );

// Card types

types : tribal_type? spell_type -> ^( TYPES tribal_type? spell_type )
      | tribal_type n=noncreature_perm_types -> ^( TYPES tribal_type $n )
      | permanent_types -> ^( TYPES permanent_types )
      | other_type -> ^( TYPES other_type );

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
