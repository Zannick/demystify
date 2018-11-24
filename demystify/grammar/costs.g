parser grammar costs;

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

/* Costs and payments */

// TODO: "as an additional cost" items: "you may", "choose" type/number.

// The OR case here is where the player has the option to choose
// either of the methods to pay for the ability,
// eg. 3, TAP or U, TAP.

cost : cost_list ( OR^ cost_list )?
     | loyalty_cost -> ^( COST loyalty_cost );

// The AND case here is usually for costs where a latter item
// references a preceding item,
// eg. remove n quest counters from SELF and sacrifice it.
// This sometimes makes it seem like MTG doesn't use the oxford comma
// in separating cost items, but does in separating subsets as part of
// a cost item. More simply, MTG doesn't normally use 'and' in cost lists
// eg: "{2}{u}, {t}, discard a card, sacrifice a land".

cost_list : cost_item ( COMMA cost_item )* ( AND cost_item )?
            -> ^( COST cost_item+ );

cost_item : TAP_SYM
          | UNTAP_SYM
          | mana
          | repeatable_cost_item_ 
            ( for_each -> ^( PAY_PER repeatable_cost_item_ for_each )
            | -> repeatable_cost_item_
            )
          ;

repeatable_cost_item_ : PAY! mana
                      | discard
                      | exile
                      | move_cards
                      | pay_mana_cost
                      | pay_energy
                      | pay_life
                      | put_counters
                      | remove_counters
                      | reveal
                      | sacrifice
                      | tap
                      | unattach
                      | untap
                      ;

// Loyalty

loyalty_cost : PLUS_SYM? ( NUMBER_SYM | VAR_SYM )
               -> ^( LOYALTY PLUS NUMBER_SYM? ^( VAR VAR_SYM )? )
             | MINUS_SYM ( NUMBER_SYM | VAR_SYM )
               -> ^( LOYALTY MINUS NUMBER_SYM? ^( VAR VAR_SYM )? );

// Mana symbols and mana costs

mana : ( MANA_SYM | VAR_MANA_SYM )+
       -> ^( MANA MANA_SYM* ^( VAR VAR_MANA_SYM )* );

discard : DISCARD subsets ( AT RANDOM )? -> ^( DISCARD RANDOM? subsets );

exile : EXILE^ subsets ;

move_cards : ( PUT | RETURN ) subsets ( TO | ON | INTO ) zone_subset
           -> ^( MOVE_TO subsets zone_subset );

pay_energy : PAY ( ANY AMOUNT OF ENERGY_SYM -> ^( ENERGY ANY[] )
                 | A AMOUNT OF ENERGY_SYM EQUAL TO magic_number
                   -> ^( ENERGY ^( EQUAL[] magic_number ))
                 | e+=ENERGY_SYM+ -> ^( ENERGY NUMBER[str(len($e))] )
                 );

pay_life : PAY magic_life_number -> ^( PAY_LIFE magic_life_number );

pay_mana_cost : PAY ref_obj_poss MANA COST -> ^( PAY_COST ref_obj_poss );

put_counters : PUT counter_subset ON subsets
               -> ^( ADD_COUNTERS counter_subset subsets ) ;

remove_counters : REMOVE counter_subset FROM subsets
                  -> ^( REMOVE_COUNTERS counter_subset subsets ) ;

reveal : REVEAL^ subsets ;

sacrifice : SACRIFICE^ subsets ;

tap : TAP^ subsets ;

unattach : UNATTACH^ subsets ;

untap : UNTAP^ subsets ;
