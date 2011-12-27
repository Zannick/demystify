parser grammar mana;

/* Mana symbols and mana costs */

mc_symbols
    : (BASIC_MANA_SYM | MC_HYBRID_SYM | MC_VAR_SYM | NUMBER_SYM)*
      -> ^( MANA BASIC_MANA_SYM* MC_HYBRID_SYM* MC_VAR_SYM* NUMBER_SYM* );
