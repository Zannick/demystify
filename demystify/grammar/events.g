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

triggers : trigger ( OR trigger )? trigger_descriptor?
           -> {$OR}? ^( TRIGGER ^( OR[] trigger+ ) trigger_descriptor? )
           -> ^( TRIGGER trigger trigger_descriptor? );

// Although it doesn't look great, it was necessary to factor 'subset' out
// of the event and condition rules. It's a bad idea to leave it unfactored
// since ANTLR will run itself out of memory (presumably trying to generate
// lookahead tables).
trigger : subset_list
          ( event ( OR event )?
            -> {$OR}? ^( EVENT subset_list ^( OR[] event+ ) )
            -> ^( EVENT subset_list event )
          | condition -> ^( CONDITION subset_list condition )
          )
        | non_subset_event -> ^( EVENT non_subset_event )
        | non_subset_condition -> ^( CONDITION non_subset_condition )
        ;

// An event is something that happens, usually an object taking an action
// or having an action done to it.

event : zone_transfer
      | cause_transfer
      | phases_in_out
      | state_change
      | cost_paid
      | attack_with_stuff
      | cast_spell
      | clash_happens
      | coin_flip
      | counter_spell
      | cycle_card
      | deal_damage
      | dealt_damage
      | discard_card
      | draw_card
      | gain_life
      | kick_stuff
      | lose_control
      | lose_life
      | lose_the_game
      | play_stuff
      | sacrifice_stuff
      | shuffle_library
      | tap_stuff
      | is_tapped
      ;

/* Events. */

zone_transfer : ( ENTER | is_ ( PUT ( INTO | ONTO ) | RETURNED TO ) )
                a=zone_subset ( FROM ( b=zone_subset | ANYWHERE ) )?
                -> ^( ENTER[] $a ^( FROM[] $b? ANYWHERE[]? )? )
              | LEAVE zone_subset
                -> ^( LEAVE[] zone_subset )
              | DIE
                -> ^( ENTER[] ^( ZONE_SET ^( NUMBER NUMBER[$DIE, "1"] ) GRAVEYARD )
                              ^( FROM[] BATTLEFIELD ) )
              ;

cause_transfer : PUT subset ( INTO | ONTO )
                 a=zone_subset ( FROM ( b=zone_subset | ANYWHERE ) )?
                 -> ^( PUT[] subset $a ^( FROM[] $b? ANYWHERE[]? )? );

phases_in_out : PHASE^ ( IN | OUT );

state_change : BECOME ( BLOCKED BY subset
                        -> ^( BECOME[] BLOCKED ^( BY[] subset ) )
                      | status -> ^( BECOME[] status )
                      | THE TARGET OF subset -> ^( TARGETED subset )
                      | UNATTACHED FROM subset
                        -> ^( BECOME UNATTACHED ^( FROM[] subset ) )
                      )
             | ATTACK ( subset_list | ALONE )?
               ( AND IS NOT BLOCKED
                 -> ^( BECOME UNBLOCKED ALONE? subset_list? )
               | -> ^( BECOME ATTACKING ALONE? subset_list? )
               )
             | BLOCK ( subset | ALONE )? -> ^( BECOME BLOCKING ALONE? subset? )
             | is_ TURNED status -> ^( BECOME[] status )
             ;

cost_paid : poss cost_prop IS NOT? PAID
            -> {$NOT}? ^( NOT[] ^( PAID[] cost_prop ) )
            -> ^( PAID[] cost_prop )
          | ( DO NOT )? PAY ( A | subset poss ) cost_prop
            -> {$NOT}? ^( NOT[] ^( PAY[] cost_prop subset? ) )
            -> ^( PAY[] cost_prop subset? )
          ;

attack_with_stuff : ATTACK^ WITH! subset ;

// TODO: Collect alike verbs together into one rule?
cast_spell : CAST^ subset ;

clash_happens : CLASH AND ( WIN | LOSE ) -> ^( CLASH[] WIN[]? LOSE[]? )
              | CLASH -> CLASH[]
              ;

coin_flip : FLIP A COIN -> COINFLIP
          | ( LOSE | WIN ) A COIN FLIP -> ^( COINFLIP LOSE[]? WIN[]? );

counter_spell : COUNTER^ subset ;

cycle_card : CYCLE^ subset
           | CYCLE OR^ DISCARD subset ;

deal_damage : DEAL integer? damage ( TO subset_list )?
              -> ^( DEAL[] integer? damage subset_list? );

dealt_damage : is_ DEALT integer? damage ( BY subset )?
               -> ^( DEALT[] integer? damage subset? );

discard_card : DISCARD^ subset ;

draw_card : DRAW^ A! CARD! ;

gain_life : GAIN^ integer? LIFE ;

kick_stuff : KICK^ subset ;

lose_control : LOSE CONTROL OF subset -> ^( LOSE[] CONTROL[] subset );

lose_life : LOSE^ integer? LIFE ;

lose_the_game : LOSE^ THE! GAME ;

play_stuff : PLAY^ subset ;

sacrifice_stuff : SACRIFICE^ subset ;

shuffle_library : SHUFFLE^ player_poss LIBRARY ;

tap_stuff : TAP subset ( FOR MANA )? -> ^( TAP[] subset MANA[]? );

is_tapped : is_ TAPPED FOR MANA -> ^( BECOME TAPPED[] MANA[] );

// A condition is a true-or-false statement about the game state. These
// types of triggered abilities (sometimes called "state triggers") will
// trigger any time that statement is true and it isn't already on the stack.
// Since otherwise this would lead to a mandatory loop, the effects of these
// triggered conditions usually serve to end the game or change the relevant
// state (e.g. 'when SELF has flying, sacrifice it').

condition : has_ability
          | has_cards
          | have_life
          | HAS! has_counters
          | int_prop_is
          | control_stuff
          | is_somewhere
          ;

/* Conditions. */

has_ability : HAS raw_keyword -> ^( HAS[] raw_keyword );

has_cards : HAS number CARD IN HAND -> ^( HAND[] number );

have_life : HAS integer LIFE -> ^( VALUE LIFE[] integer );

int_prop_is : poss int_prop IS magic_number
              -> ^( VALUE int_prop magic_number );

control_stuff : CONTROL subset -> ^( CONTROL[] subset );

is_somewhere : is_ ( IN | ON ) zone_subset -> ^( IN[] zone_subset );

// Some triggers do not start with subsets, eg. "there are",
// "a counter is" or "the chosen color is".
non_subset_event : counter_changed
                 | damage_dealt
                 ;

non_subset_condition : there_are
                     | there_counters
                     ;

/* Non-subset events. */

counter_changed : ( THE ordinal_word | number )
                  base_counter is_
                  ( REMOVED FROM subset
                    -> ^( REMOVED ordinal_word? number? base_counter subset )
                  | PUT ON subset
                    -> ^( PUT ordinal_word? number? base_counter subset )
                  );

damage_dealt : integer? damage is_ DEALT TO subset_list
               -> ^( DEAL integer? damage subset_list );

/* Non-subset conditions. */

there_are : THERE is_ number properties restriction*
            -> ^( EQUAL number ^( SIZE properties restriction* ) );

there_counters : THERE is_ counter_subset ON subset
                 -> ^( HAS_COUNTERS counter_subset subset );

// A trigger descriptor is an additional check that comes after the event
// triggers and conditions. Some of these may be (or include) conditions.
trigger_descriptor : while_condition
                   | during_turn
                   | during_step
                   | nth_time_per_turn
                   | this_turn
                   ;

while_condition : WHILE ref_object ( condition | is_ status )
                  -> ^( CONDITION ref_object condition? status? )
                | WHILE non_subset_condition
                  -> ^( CONDITION non_subset_condition )
                ;

during_turn : DURING player_poss TURN
              -> ^( DURING[] ^( TURN[] player_poss ) );

// TODO: Other steps.
during_step : DURING^ COMBAT ;

nth_time_per_turn : FOR THE ordinal_word TIME THIS TURN
                    -> ^( NTH ordinal_word ^( PER TURN[] ) );
