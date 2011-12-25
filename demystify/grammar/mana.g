parser grammar mana;

/* Mana symbols and mana costs */

mc_symbols : ( BASIC_MANA_SYMBOL | NUMBER_SYM | MC_HYBRID_SYM )+ ;
