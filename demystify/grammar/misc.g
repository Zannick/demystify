parser grammar misc;

/* Miscellaneous rules. */

conj : AND | OR | AND_OR ;

// TODO: more player stuff.
player_poss : YOUR ;

// TODO: Move into subsets.
// Property names.
prop_type : COLOR
          | MANA! COST
          | type TYPE -> ^( SUBTYPE type )
          | CARD! TYPE
          | int_prop;

prop_with_value : int_prop_with_value;

int_prop : CONVERTED MANA COST -> CMC
         | LIFE TOTAL!?
         | POWER
         | TOUGHNESS;

int_prop_with_value : CONVERTED MANA COST integer -> ^( CMC integer )
                    | integer LIFE^
                    | POWER^ integer
                    | TOUGHNESS^ integer;
