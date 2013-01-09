parser grammar properties;

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

/* Rules for describing object properties. */

/*
 * We divide properties into three categories:
 * - adjectives
 * - nouns
 * - descriptors
 *
 * Nouns are the only required part of a set of subset properties
 * (except for the cases where an ability talks about having or being a
 *  property).
 * An adjective is any property that can't be used alone in a subset that
 * precede any nouns. For example, colors and tap status.
 * Descriptors are properties that can't be used alone in a subset that follow
 * any nouns. For example, "under your control" and "named X".
 *
 * Some of these items can be written as lists of two or more items joined
 * with a conjunction. However, only one "level" of a subset can be a list:
 * either adjectives (which can include nouns), nouns, a combination of
 * both adjectives and nouns, or all three together; the type of list is
 * generally determinable from the first item in the list.
 *
 * When a list occurs in either adjectives or nouns, the list is treated
 * as its own set of properties, joined with the other two categories.
 * The object must match each category for the object to match the whole set
 * of properties. For example, in "white or blue creature", "white or blue"
 * is an adjective list, and creature is a noun. An object must match "white
 * or blue" and "creature" to match this properties set.
 *
 * Note that the conjunction is likely to be misleading based on usage here.
 * Both "sacrifice a white or blue creature" and "white and blue creatures
 * have flying" reference a set of creatures with color(s) white and/or blue.
 * To be granted flying from the latter ability, a creature must be at least
 * one of white and blue; it does not have to be both. In other words, an
 * "and" in such a situation can be considered equivalent to "union". However,
 * "sacrifice a white and blue creature" uses it as "intersection"; here the
 * creature sacrificed must be both white and blue. Context is important.
 * In some cases, the text may instead read "a creature that's both white and
 * blue".
 */

properties : a+=adjective*
             ( adj_list? noun+ descriptor*
               -> ^( PROPERTIES adjective* adj_list? noun* descriptor* )
             | nl=noun_list n+=noun* nd+=descriptor*
               {
                if $n:
                    self.emitDebugMessage('properties case 2a: {}'.format(
                        ' '.join([t.text for t in ($a or [])]
                                 + [$nl.tree.toStringTree()]
                                 + [t.text for t in ($n or [])]
                                 + [t.toStringTree() for t in ($nd or [])])))
                elif $a:
                    self.emitDebugMessage('properties case 2b: {}'.format(
                        ' '.join([t.text for t in ($a or [])]
                                 + [$nl.tree.toStringTree()]
                                 + [t.toStringTree() for t in ($nd or [])])))
               }
               -> ^( PROPERTIES adjective* noun_list noun* descriptor* )
             | b+=noun+ 
               ( ( COMMA ( c+=properties_case3_ COMMA )+ )?
                 j=conj g=properties_case3_ e+=descriptor*
                 // Currently only Purge?
                 { self.emitDebugMessage('properties case 3: {}'
                                         .format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [', ' + t.toStringTree() for t in ($c or [])]
                    + ($c and [','] or [])
                    + [$j.text]
                    + [$g.text]
                    + [t.toStringTree() for t in ($e or [])]))) }
                 -> ^( PROPERTIES ^( $j ^( AND $a* $b+ )
                                        ^( AND properties_case3_)+ )
                                  descriptor* )
               | f+=descriptor+ ( COMMA ( c+=basic_properties COMMA )+ )?
                 k=conj d=basic_properties
                 { self.emitDebugMessage('properties case 4: {}'
                                         .format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [t.toStringTree() for t in ($f or [])]
                    + [', ' + t.toStringTree() for t in ($c or [])]
                    + ($c and [','] or [])
                    + [$k.text]
                    + [$d.tree.toStringTree()]))) }
                 -> ^( PROPERTIES ^( $k ^( AND $a* $b+ $f+ )
                                        ^( AND basic_properties )+ ) )
               )
             );

properties_case3_ : adjective+ noun+ ;

basic_properties : adjective* noun+ descriptor* ;

// TODO: with descriptors? subsets would like a list of properties
// that don't have adj_list or noun_list.
simple_properties : basic_properties -> ^( PROPERTIES basic_properties )
                  | adjective+ -> ^( PROPERTIES adjective+ );

// Lists

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

// status that can't be used as an adjective but can be used in descriptors
desc_status : status
            | ENCHANTED
            | EQUIPPED
            | FORTIFIED
            | HAUNTED
            ;

// Nouns

noun : NON? ( type | obj_subtype | obj_type )
       -> {$NON}? ^( NON[] type? obj_subtype? obj_type? )
       -> type? obj_subtype? obj_type? ;

// Descriptors

descriptor : named
           | control
           | own
           | cast
           | in_zones
           | with_keywords
           | THAT is_
             ( desc_status -> desc_status
             | BOTH adjective AND adjective -> adjective+
             | NOT ( desc_status | in_zones | ON spec_zone )
               -> ^( NOT[] desc_status? in_zones? spec_zone? )
             )
           ;

named : NOT? NAMED REFBYNAME
        -> {$NOT}? ^( NOT[] ^( NAMED[] REFBYNAME ) )
        -> ^( NAMED[] REFBYNAME );

control : player_subset ( DO NOT )? CONTROL
          -> {$NOT}? ^( NOT[] ^( CONTROL[] player_subset ) )
          -> ^( CONTROL[] player_subset );
own : player_subset ( DO NOT )? OWN
      -> {$NOT}? ^( NOT[] ^( OWN[] player_subset ) )
      -> ^( OWN[] player_subset );
cast : player_subset ( DO NOT )? CAST
       -> {$NOT}? ^( NOT[] ^( CAST[] player_subset ) )
       -> ^( CAST[] player_subset );

in_zones : ( IN | FROM ) zone_subset -> ^( IN[] zone_subset );

with_keywords : WITH raw_keywords -> ^( KEYWORDS raw_keywords )
              | WITHOUT raw_keywords -> ^( NOT ^( KEYWORDS raw_keywords ) )
              ;

/* Special references to related objects. */

haunted_object : THE ( type | obj_type ) ref_object HAUNT
                 -> ^( HAUNTED ref_object );

// TODO: target
// TODO: ref_player
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
           | this_guy
           | that_guy
           ;

// eg. this creature, this permanent, this spell.
this_guy : THIS ( type | obj_type ) -> SELF;

that_guy : THAT^ ( type | obj_type );

/* Property names. */

prop_types : prop_type ( ( COMMA! ( prop_type COMMA! )+ )? conj^ prop_type )? ;

prop_type : COLOR -> COLOR[]
          | type TYPE -> ^( SUBTYPE type )
          | CARD? TYPE -> TYPE[]
          | int_prop
          | cost_prop
          ;

int_prop : CONVERTED MANA COST -> CMC
         | LIFE TOTAL? -> LIFE[]
         | POWER -> POWER[]
         | TOUGHNESS -> TOUGHNESS[]
         ;

cost_prop : MANA COST -> COST[]
          | raw_keyword_with_cost COST? -> ^( COST[] raw_keyword_with_cost )
          ;
