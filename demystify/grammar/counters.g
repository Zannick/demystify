parser grammar counters;

/* Rules related to counters. */

/* Counter subsets. */

counter_subset : counter_group
                 ( ( COMMA ( counter_group COMMA )+ )? conj counter_group
                   -> ^( COUNTER_SET ^( conj counter_group+ ) )
                 | -> ^( COUNTER_SET counter_group )
                 );
 
counter_group : number ( obj_counter | pt )? COUNTER
                -> ^( COUNTER_GROUP number obj_counter? pt? );

base_counter_set : base_counter
                   ( ( COMMA ( base_counter COMMA )+ )? conj base_counter
                     -> ^( COUNTER_SET ^( conj base_counter+ ) )
                   | -> ^( COUNTER_SET base_counter )
                   );

base_counter : ( obj_counter | pt ) COUNTER
               -> ^( COUNTER[] obj_counter? pt? )
             | COUNTER -> ^( COUNTER[] COUNTER['*'] )
             ;
