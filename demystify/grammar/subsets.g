parser grammar subsets;

/* Rules for describing subsets of objects. */

subsets : subset ( ( ( ','! subset )+ ','! )? conj^ subset )?;

subset : number properties -> ^( SUBSET number properties )
       | AMONG properties -> ^( SUBSET ^( NUMBER ANY ) properties )
       | ANOTHER properties -> ^( SUBSET ^( NOT SELF ) properties )
       | THE LAST properties -> ^( SUBSET ^( LAST properties ) )
       | full_zone -> ^( SUBSET full_zone )
       | ref_object -> ^( SUBSET ref_object );

// A full zone, for use as a subset
full_zone : player_poss ind_zone -> ^( ZONE player_poss ind_zone )
          | THE ( TOP | BOTTOM ) number? properties
            OF player_poss ( LIBRARY | GRAVEYARD )
            -> {$number.text}? number properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? )
            -> ^( NUMBER NUMBER[$THE, "1"] ) properties
               ^( ZONE player_poss LIBRARY? GRAVEYARD? TOP? BOTTOM? );

/*
 * We divide properties into three categories:
 * - adjectives
 * - nouns
 * - descriptors
 *
 * Nouns are the only required part of a set of subset properties
 * (except for the cases where an ability talks about having or being a
 *  property).
 * An adjective is any property that can't be used alone in a subset that
 * precede any nouns. For example, colors and tap status.
 * Descriptors are properties that can't be used alone in a subset that follow
 * any nouns. For example, "under your control" and "named X".
 *
 * Some of these items can be written as lists of two or more items joined
 * with a conjunction. However, the top level properties cannot have a list
 * of more than two; this kind of list will be accomplished by subset lists.
 * Furthermore, only one list can exist per properties set: either the
 * adjective list, the noun list, or the properties pair.
 *
 * When a list occurs in either adjectives or nouns, the list is treated
 * as its own set of properties, joined with the other two categories.
 * The object must match each category for the object to match the whole set
 * of properties. For example, in "white or blue creature", "white or blue"
 * is an adjective list, and creature is a noun. An object must match "white
 * or blue" and "creature" to match this properties set.
 */

properties : a+=adjective*
             ( adj_list? noun+ descriptor*
               -> ^( PROPERTIES adjective* adj_list? noun* descriptor* )
             | noun_list noun* descriptor*
               -> ^( PROPERTIES adjective* noun_list noun* descriptor* )
             | b+=noun+ 
               ( ( ',' ( c+=properties_case3_ ',' )+ )?
                 j=conj g=properties_case3_ e+=descriptor*
                 { self.emitDebugMessage('properties case 3: {}'
                                         .format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [', ' + t.toStringTree() for t in ($c or [])]
                    + ($c and [','] or [])
                    + [$j.text]
                    + [$g.text]
                    + [t.toStringTree() for t in ($e or [])]))) }
                 -> ^( PROPERTIES ^( $j ^( AND $a* $b+ )
                                        ^( AND properties_case3_)+ )
                                     descriptor* )
                 // TODO: expand case 4 if necessary?
               | f+=descriptor+ k=conj c+=adjective* d+=noun+ e+=descriptor*
                 { self.emitDebugMessage('properties case 4: {}'
                                         .format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [t.toStringTree() for t in ($f or [])]
                    + [$k.text]
                    + [t.text for t in ($c or []) + ($d or [])]
                    + [t.toStringTree() for t in ($e or [])]))) }
                 -> ^( PROPERTIES ^( $k ^( AND $a* $b+ $f+ )
                                        ^( AND $c* $d+ $e* ) ) )
               )
             );

properties_case3_ : adjective+ noun+ ;

// Lists

adj_list : adjective ( ','! ( ( adjective | noun ) ','! )+ )?
           conj^ ( adjective | noun );

noun_list : noun ( ','! ( noun ','! )+ )? conj^ noun ;

// Adjectives

adjective : NON^? ( supertype | color | color_spec | status );

color : WHITE | BLUE | BLACK | RED | GREEN;
color_spec : COLORED | COLORLESS | MONOCOLORED | MULTICOLORED;
status : TAPPED
       | UNTAPPED
       | SUSPENDED
       | ATTACKING
       | BLOCKING
       | BLOCKED
       | UNBLOCKED
       | FACE_UP
       | FACE_DOWN
       | FLIPPED
       | REVEALED
       | ACTIVE;

// Nouns

noun : NON^? ( type | obj_subtype | obj_type | player_type );

// Descriptors

descriptor : named
           | control
           | own
           | other_than
           | in_zones
           | WITH! has_counters
           | WITH! int_prop_with_value
           | THAT! share_feature
           | WITH! total_int_prop ;

named : NAMED^ REFBYNAME;

control : player_subset CONTROL^;
own : player_subset OWN^;

// TODO: 'other than a basic land card' ie. other than subset_no_descriptors
// TODO: 'other than a player's hand or library' ie. other than ref_zone
// TODO: 'choose a creature type other than wall'. This may go elsewhere.
other_than : OTHER THAN ref_object -> ^( NOT ref_object );

/* Special references to related objects. */

// TODO: target
// TODO: ref_player
ref_object : SELF
           | PARENT
           | IT
           | THEM
             // planeswalker pronouns
           | HIM
           | HER
             // We probably don't actually need to remember what the
             // nouns were here, but keep them in for now.
           | ( ENCHANTED | EQUIPPED | FORTIFIED | HAUNTED ) noun+
           | this_guy
           ;

// eg. this creature, this permanent, this spell.
this_guy : THIS ( type | obj_type ) -> SELF;

in_zones : IN zone_subset -> ^( IN[] zone_subset )
         | FROM zone_subset -> ^( IN zone_subset );

/* Counter subsets. */

counter_subset : counter_group
                 ( ( ',' ( counter_group ',' )+ )? conj counter_group
                   -> ^( COUNTER_SET ^( conj counter_group+ ) )
                 | -> ^( COUNTER_SET counter_group )
                 );
 
counter_group : number ( obj_counter | pt )? COUNTER
                -> ^( COUNTER_GROUP number obj_counter? pt? );

/* Special properties, usually led by 'with', 'that', or 'if it has' */

has_counters : counter_subset ON ref_object
               -> ^( HAS_COUNTERS ref_object counter_subset );

share_feature : SHARE A prop_type -> ^( SHARE[] prop_type );

total_int_prop : TOTAL^ int_prop_with_value ;
