parser grammar subsets;

/* Rules for describing subsets of objects. */

subsets : subset ( ( ( ','! subset )+ ','! )? conj^ subset )?
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
       ;

// A full zone, for use as a subset
full_zone : player_poss ind_zone -> ^( ZONE player_poss ind_zone )
          | THE ( TOP | BOTTOM ) number? properties
            OF player_poss ( LIBRARY | GRAVEYARD )
            -> {$number.text}? number properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? )
            -> ^( NUMBER NUMBER[$THE, "1"] ) properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? );

restriction : WITH! has_counters
            | WITH! int_prop_with_value
            | THAT! share_feature
            | WITH! total_int_prop
            | other_than
            | except_for
            | attached_to
            ;

// TODO: 'choose a creature type other than wall'. This may go elsewhere.
other_than : OTHER THAN
             ( ref_object -> ^( NOT ref_object )
             | A? properties -> ^( NOT properties )
             | zone_subset -> ^( NOT zone_subset )
             );

// TODO: "except for creatures the player hasn't controlled continuously
//        since the beginning of the turn".
// put in descriptors? putting in restriction would require
// except_for to not be in restriction
except_for : ','!? EXCEPT^ FOR! ( ref_object | properties );

attached_to : ATTACHED TO ( ref_object | properties )
              -> ^( ATTACHED_TO ref_object? properties? );

/* Special properties, usually led by 'with', 'that', or 'if it has' */

has_counters : counter_subset ON ref_object
               -> ^( HAS_COUNTERS ref_object counter_subset );

share_feature : SHARE A prop_type -> ^( SHARE[] prop_type );

total_int_prop : TOTAL^ int_prop_with_value ;

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

int_prop_with_value : CONVERTED MANA COST comparison -> ^( CMC comparison )
                    | integer LIFE^
                    | LIFE^ comparison
                    | POWER^ comparison
                    | TOUGHNESS^ comparison;
