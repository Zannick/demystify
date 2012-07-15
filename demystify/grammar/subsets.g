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

subsets : subset ( ( COMMA! ( subset COMMA! )+ )? conj^ subset )?
        | properties restriction*
          -> ^( SUBSET ^( NUMBER ALL ) properties restriction* );

subset : number properties restriction*
         -> ^( SUBSET number properties restriction* )
       | AMONG properties restriction*
         -> ^( SUBSET ^( NUMBER ANY ) properties restriction* )
       | ANOTHER properties restriction*
         -> ^( SUBSET ^( NOT SELF ) properties restriction* )
       | ALL OTHER properties restriction*
         -> ^( SUBSET ^( NUMBER ALL ) ^( NOT SELF ) properties restriction* )
       | THE LAST properties restriction*
         -> ^( SUBSET ^( LAST properties restriction* ) )
       | full_zone
         -> ^( SUBSET full_zone )
       | ref_object in_zones?
         -> ^( SUBSET ref_object in_zones? )
       | player_group
         -> ^( SUBSET player_group )
       ;

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
            | THAT! share_feature
            | WITH! total_int_prop
            | other_than
            | except_for
            | attached_to
            | chosen_prop
            | not_chosen_prop
            | from_expansion
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

not_chosen_prop : THAT ( ISNT | ARENT ) 
                  ( chosen_prop -> ^( NOT chosen_prop )
                  | OF A prop_type CHOSEN THIS WAY
                    -> ^( NOT ^( CHOSEN[] prop_type ) )
                  | THE NAMED CARD -> ^( NOT ^( CHOSEN[] NAME ) )
                  );

from_expansion : FROM THE expansion EXPANSION -> ^( EXPANSION[] expansion );

expansion : ANTIQUITIES
          | ARABIAN_NIGHTS
          | HOMELANDS
          ;

/* Special properties, usually led by 'with', 'that', or 'if it has' */

// Do we need to remember ref_object?
has_counters : counter_subset ON ref_object
               -> ^( HAS_COUNTERS counter_subset );

share_feature : SHARE A prop_type -> ^( SHARE[] prop_type );

total_int_prop : TOTAL^ int_prop_with_value ;

prop_with_value : int_prop_with_value;

int_prop_with_value : CONVERTED MANA COST comparison -> ^( CMC comparison )
                    | integer LIFE^
                    | LIFE^ comparison
                    | POWER^ comparison
                    | TOUGHNESS^ comparison;
