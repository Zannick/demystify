parser grammar subsets;

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

/* Rules for describing subsets of objects. */

subsets : subset_list
        | mini_sub ( ( COMMA ( mini_sub COMMA )+ )? conj mini_sub )?
          -> {$conj.text}? ^( SUBSET ^( NUMBER ALL )
                                     ^( conj ^( SUBSET mini_sub)+ ) )
          -> ^( SUBSET ^( NUMBER ALL ) mini_sub )
        ;

subset_list : subset ( options {greedy=true;}:
                       ( COMMA! ( subset COMMA! )+ )? conj^ subset )? ;

subset : number mini_sub ( ( COMMA ( mini_sub COMMA )+ )? conj mini_sub )?
         -> {$conj.text}? ^( SUBSET number ^( conj ^( SUBSET mini_sub)+ ) )
         -> ^( SUBSET number mini_sub )
       | number OTHER mini_sub
         -> ^( SUBSET number ^( NOT SELF ) mini_sub )
       | AMONG mini_sub
         -> ^( SUBSET ^( NUMBER ANY ) mini_sub )
       | ANOTHER mini_sub
         -> ^( SUBSET ^( NOT SELF ) mini_sub )
       | THE LAST mini_sub
         -> ^( SUBSET ^( LAST mini_sub ) )
       | full_zone
         -> ^( SUBSET full_zone )
       | haunted_object
         -> ^( SUBSET haunted_object )
       | ref_object in_zones?
         -> ^( SUBSET ref_object in_zones? )
       | player_group
         -> ^( SUBSET player_group )
       ;

mini_sub : properties restriction* ;

// A full zone, for use as a subset
full_zone : player_poss ind_zone -> ^( ZONE player_poss ind_zone )
          | THE ( TOP | BOTTOM ) number? properties
            OF player_poss ( LIBRARY | GRAVEYARD )
            -> {$number.text}? number properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? )
            -> ^( NUMBER NUMBER[$THE, "1"] ) properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? );

// Restrictions are very similar to descriptors, but can reference properties.
restriction : WITH! has_counters
            | WITH! int_prop_with_value
            | share_feature
            | WITH! total_int_prop
            | other_than
            | except_for
            | attached_to
            | chosen_prop
            | not_chosen_prop
            | from_expansion
            | linked_ref
            ;

// TODO: 'choose a creature type other than wall'. This may go elsewhere.
other_than : OTHER THAN
             ( ref_object -> ^( NOT ref_object )
             | A? properties -> ^( NOT properties )
             | zone_subset -> ^( NOT zone_subset )
             );

// TODO: "except for creatures the player hasn't controlled continuously
//        since the beginning of the turn".
// put in descriptors? putting "...hasn't controlled" in restriction would
// require except_for to not be in restriction.
except_for : ','!? EXCEPT^ FOR! ( ref_object | properties );

attached_to : ATTACHED TO ( ref_object | properties )
              -> ^( ATTACHED_TO ref_object? properties? );

chosen_prop : ( OF | WITH ) THE CHOSEN prop_type -> ^( CHOSEN[] prop_type );

not_chosen_prop : THAT IS NOT
                  ( chosen_prop -> ^( NOT[] chosen_prop )
                  | OF A prop_type CHOSEN THIS WAY
                    -> ^( NOT[] ^( CHOSEN[] prop_type ) )
                  | THE NAMED CARD -> ^( NOT[] ^( CHOSEN[] NAME ) )
                  );

from_expansion : FROM THE expansion EXPANSION -> ^( EXPANSION[] expansion );

expansion : ANTIQUITIES
          | ARABIAN_NIGHTS
          | HOMELANDS
          ;

linked_ref : CHAMPIONED WITH SELF -> ^( LINKED CHAMPION )
           | EXILED WITH SELF -> ^( LINKED EXILE )
           | PUT ONTO THE BATTLEFIELD WITH SELF -> ^( LINKED BATTLEFIELD[] )
           ;

/* Special properties, usually led by 'with', 'that', or 'if it has' */

// Do we need to remember ref_object?
has_counters : counter_subset ON ref_object
               -> ^( HAS_COUNTERS counter_subset );

share_feature : THAT SHARE A prop_type -> ^( SHARE[] prop_type )
              | WITH THE SAME prop_type -> ^( SAME[] prop_type );

total_int_prop : TOTAL^ int_prop_with_value ;

prop_with_value : int_prop_with_value;

int_prop_with_value : CONVERTED MANA COST comparison -> ^( CMC comparison )
                    | integer LIFE^
                    | LIFE^ comparison
                    | POWER^ comparison
                    | TOUGHNESS^ comparison;
