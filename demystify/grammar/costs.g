parser grammar costs;

/* Costs and payments */

// The OR case here is where the player has the option to choose
// either of the methods to pay for the ability,
// eg. 3, TAP or U, TAP.

cost : cost_list OR cost_list -> ^( OR cost_list+ )
     | cost_list 
     | loyalty_cost -> ^( COST loyalty_cost );


// The AND case here is usually for costs where a latter item
// references a preceding item,
// eg. remove n quest counters from SELF and sacrifice it.

cost_list : cost_item ( COMMA cost_item )* ( AND cost_item )?
            -> ^( COST cost_item+ );

cost_item : mana
          | tap
          | untap
          ;

// Loyalty

loyalty_cost : PLUS_SYM? ( NUMBER_SYM | VAR_SYM)
               -> ^( LOYALTY PLUS NUMBER_SYM? ^( VAR VAR_SYM )? )
             | MINUS_SYM ( NUMBER_SYM | VAR_SYM)
               -> ^( LOYALTY MINUS NUMBER_SYM? ^( VAR VAR_SYM )? );

// Mana symbols and mana costs

mc_symbols
    : ( BASIC_MANA_SYM | MC_HYBRID_SYM | MC_VAR_SYM | NUMBER_SYM )*
      -> ^( MANA BASIC_MANA_SYM* MC_HYBRID_SYM*
            ^( VAR MC_VAR_SYM )* NUMBER_SYM* );

// The only place an empty mana cost is valid is the mana cost field on a card,
// which is covered by mc_symbols above.

mana : (MANA_SYM | VAR_MANA_SYM)+
       -> ^( MANA MANA_SYM* ^( VAR VAR_MANA_SYM )* );

tap : TAP_SYM ;

untap : UNTAP_SYM ;
