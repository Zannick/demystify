parser grammar events;

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

/* Events and conditions. */

triggers : trigger ( OR^ trigger )? ;

// Although it doesn't look great, it was necessary to factor 'subset' out
// of the event and condition rules. It's a bad idea to leave it unfactored
// since ANTLR will run itself out of memory (presumably trying to generate
// lookahead tables).
// TODO: event descriptors (eg. "during combat")
trigger : subset_list
          ( event ( OR event )?
            -> {$OR}? ^( EVENT subset_list ^( OR[] event+ ) )
            -> ^( EVENT subset_list event )
          | condition -> ^( CONDITION subset_list condition )
          );

// An event is something that happens, usually an object taking an action
// or having an action done to it.

event : zone_transfer
      | phases_in_out
      | state_change
      | cost_paid
      | cast_spell
      | cycle_card
      | deal_damage
      | dealt_damage
      | discard_card
      | draw_card
      | gain_life
      | lose_life
      | tap_stuff
      | is_tapped
      | sacrifice_stuff
      ;

/* Events. */

zone_transfer : ( ENTER | ( IS | ARE ) PUT ( INTO | ONTO ) ) a=zone_subset
                ( FROM ( b=zone_subset | ANYWHERE ) )?
                -> ^( ENTER[] $a ^( FROM[] $b? ANYWHERE[]? )? )
              | LEAVE zone_subset
                -> ^( LEAVE[] zone_subset )
              | DIE
                -> ^( ENTER[] ^( ZONE_SET ^( NUMBER NUMBER[$DIE, "1"] ) GRAVEYARD )
                              ^( FROM[] BATTLEFIELD ) )
              ;

phases_in_out : PHASE^ ( IN | OUT );

state_change : BECOME ( BLOCKED BY subset
                        -> ^( BECOME[] BLOCKED ^( BY[] subset ) )
                      | status -> ^( BECOME[] status )
                      | THE TARGET OF subset -> ^( TARGETED subset )
                      | UNATTACHED FROM subset
                        -> ^( BECOME UNATTACHED ^( FROM[] subset ) )
                      )
             | ATTACK ( (pl_subset)=> pl_subset | ALONE )?
               ( AND ( ISNT | ARENT ) BLOCKED
                 -> ^( BECOME UNBLOCKED ALONE? pl_subset? )
               | -> ^( BECOME ATTACKING ALONE? pl_subset? )
               )
             | BLOCK ( subset | ALONE )? -> ^( BECOME BLOCKING ALONE? subset? )
             | IS TURNED status -> ^( BECOME[] status )
             ;

cost_paid : POSS cost_prop IS NOT? PAID
            -> {$NOT}? ^( NOT ^( PAID[] cost_prop ) )
            -> ^( PAID[] cost_prop )
          | DONT? PAY ( A | subset POSS ) cost_prop
            -> {$DONT}? ^( NOT ^( PAY[] cost_prop subset? ) )
            -> ^( PAY[] cost_prop subset? )
          ;

// TODO: Collect alike verbs together into one rule?
cast_spell : CAST^ subset ;

cycle_card : CYCLE^ subset ;

deal_damage : DEAL COMBAT? DAMAGE ( TO subset )?
              -> ^( DAMAGE[] COMBAT[]? subset? );

dealt_damage : ( POSS | IS | ARE ) DEALT integer? COMBAT? DAMAGE ( BY subset )?
               -> ^( DEALT[] integer? COMBAT? DAMAGE[] subset? );

discard_card : DISCARD^ subset ;

draw_card : DRAW^ A! CARD! ;

gain_life : GAIN^ integer? LIFE ;

lose_life : LOSE^ integer? LIFE ;

tap_stuff : TAP subset ( FOR MANA )? -> ^( TAP[] subset MANA[]? );

is_tapped : ( IS | ARE ) TAPPED FOR MANA -> ^( BECOME TAPPED[] MANA[] );

sacrifice_stuff : SACRIFICE^ subset ;

// A condition is a true-or-false statement about the game state. These
// types of triggered abilities (sometimes called "state triggers") will
// trigger any time that statement is true and it isn't already on the stack.
// Since otherwise this would lead to a mandatory loop, the effects of these
// triggered conditions usually serve to end the game or change the relevant
// state (e.g. 'when SELF has flying, sacrifice it').

condition : has_ability
          | have_life
          | HAS! has_counters
          | int_prop_is
          | control_stuff
          | is_somewhere
          ;

/* Conditions. */

has_ability : ( HAS | HAVE ) raw_keyword -> ^( HAS[] raw_keyword );

have_life : ( HAS | HAVE ) integer LIFE -> ^( VALUE LIFE[] integer );

int_prop_is : POSS int_prop IS magic_number
              -> ^( VALUE int_prop magic_number );

control_stuff : CONTROL subset -> ^( CONTROL[] subset );

is_somewhere : ( IS | ARE ) ( IN | ON ) zone_subset -> ^( IN[] zone_subset );
