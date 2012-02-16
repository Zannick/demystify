parser grammar zones;

/* Zones. */

zone_subset : player_poss zone_list -> ^( ZONE_SET player_poss zone_list )
            | number zone_list -> ^( ZONE_SET number zone_list )
            | zone_list -> ^( ZONE_SET ALL zone_list )
            | spec_zone ;

// This currently allows for only 1-3 zones, since there are at most
// three possible zones in such a list.
zone_list : ind_zone ( ( ','! ind_zone ','! )? conj^ ind_zone )? ;

// These zones are player-specific so must be generally prefaced with
// player_poss or number. If not, it is usually for constructs such as
// "graveyards" where there is an implicit "all".
ind_zone : GRAVEYARD -> GRAVEYARD[]
         | HAND -> HAND[]
         | LIBRARY -> LIBRARY[] ;

// specific zones
spec_zone : THE! ( BATTLEFIELD | STACK ) 
            // we pretend the tops and bottoms of libraries are zones
          | THE? ( TOP | BOTTOM ) OF player_poss LIBRARY
            -> ^( ZONE player_poss LIBRARY TOP? BOTTOM? );

// A full zone, for use as a subset
full_zone : player_poss ind_zone -> ^( ZONE player_poss ind_zone )
          | THE ( TOP | BOTTOM ) number? properties
            OF player_poss ( LIBRARY | GRAVEYARD )
            -> {$number.text}? number properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? )
            -> ^( NUMBER NUMBER[$THE, "1"] ) properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? );

// While exile is a zone, cards in it are referred to as exiled cards,
// and not cards in exile, hence no zone rules are necessary for it.

// TODO: Command zone?
