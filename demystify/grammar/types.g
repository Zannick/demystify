parser grammar types;

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

type : permanent_type | spell_type | other_type ;

// TODO: Are all these *_type rules necessary or can I condense them into
// their respective *_types rules?

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

obj_type : OBJECT | CARD | PERMANENT | SOURCE | SPELL | TOKEN ;

// Player types

player_type : PLAYER | TEAMMATE | OPPONENT | CONTROLLER | OWNER | BIDDER ;
