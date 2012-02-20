parser grammar players;

/* Players, controllers, and owners. */

player_subset : player_group
                ( conj player_group -> ^( PLAYER_SET ^( conj player_group+ ) )
                | -> ^( PLAYER_SET player_group )
                );

// TODO: other players can have opponents and teammates
// TODO: objects can have controllers and/or owners
// TODO: Factor out some subrules?
// TODO: Handle 'that player' etc refs differently?
player_group : YOU
             | number? ( OPPONENT | TEAMMATE | PLAYER )
               -> ^( PLAYER_GROUP number? OPPONENT? TEAMMATE? PLAYER? )
             | THAT ( OPPONENT | TEAMMATE | PLAYER )
               -> ^( PLAYER_GROUP THAT OPPONENT? TEAMMATE? PLAYER? );
