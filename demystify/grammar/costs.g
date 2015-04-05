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
                      | pay_life
                      | put_cards
                      | put_counters
                      | remove_counters
                      | reveal
                      | sacrifice
                      | tap
                      | unattach
                      | untap
                      ;

// Loyalty

loyalty_cost : LBRACKET PLUS_SYM? ( NUMBER_SYM | VAR_SYM ) RBRACKET
               -> ^( LOYALTY PLUS NUMBER_SYM? ^( VAR VAR_SYM )? )
             | LBRACKET MINUS_SYM ( NUMBER_SYM | VAR_SYM ) RBRACKET
               -> ^( LOYALTY MINUS NUMBER_SYM? ^( VAR VAR_SYM )? );

// Mana symbols and mana costs

mc_symbols
    : ( BASIC_MANA_SYM | MC_HYBRID_SYM | MC_VAR_SYM | NUMBER_SYM )*
      -> ^( MANA BASIC_MANA_SYM* MC_HYBRID_SYM*
            ^( VAR MC_VAR_SYM )* NUMBER_SYM* );

// The only place an empty mana cost is valid is the mana cost field on a card,
// which is covered by mc_symbols above.

mana : ( MANA_SYM | VAR_MANA_SYM )+
       -> ^( MANA MANA_SYM* ^( VAR VAR_MANA_SYM )* );

discard : DISCARD subsets ( AT RANDOM )? -> ^( DISCARD RANDOM? subsets );

exile : EXILE^ subsets ;

pay_life : PAY magic_life_number -> ^( PAY_LIFE magic_life_number );

put_cards : PUT^ subsets ( ON! | INTO! ) zone_subset;

put_counters : PUT counter_subset ON subsets
               -> ^( ADD_COUNTERS counter_subset subsets ) ;

remove_counters : REMOVE counter_subset FROM subsets
                  -> ^( REMOVE_COUNTERS counter_subset subsets ) ;

reveal : REVEAL^ subsets ;

sacrifice : SACRIFICE^ subsets ;

tap : TAP^ subsets ;

unattach : UNATTACH^ subsets ;

untap : UNTAP^ subsets ;
