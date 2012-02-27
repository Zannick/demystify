parser grammar counters;

/* Rules related to counters. */

/* Counter subsets. */

counter_subset : counter_group
                 ( ( ',' ( counter_group ',' )+ )? conj counter_group
                   -> ^( COUNTER_SET ^( conj counter_group+ ) )
                 | -> ^( COUNTER_SET counter_group )
                 );
 
counter_group : number ( obj_counter | pt )? COUNTER
                -> ^( COUNTER_GROUP number obj_counter? pt? );

