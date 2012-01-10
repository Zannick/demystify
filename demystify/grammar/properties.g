parser grammar properties;

/* Properties of objects for describing subsets of objects. */

tokens {
    PROPERTIES;
}

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
             | noun_list descriptor*
               -> ^( PROPERTIES adjective* noun_list descriptor* )
             | b+=noun+ 
               ( j=conj c+=adjective+ d+=noun+ e+=descriptor*
                 { plog.debug('properties case 3: {}'.format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [$j.text]
                    + [t.text for t in ($c or []) + ($d or [])]
                    + [t.toStringTree() for t in ($e or [])]))) }
                 -> ^( PROPERTIES ^( $j ^( PROPERTIES $a* $b+ )
                                        ^( PROPERTIES $c+ $d+ ) )
                                     descriptor* )
               | f+=descriptor+ k=conj c+=adjective+ d+=noun+ e+=descriptor*
                 { plog.debug('properties case 4: {}'.format(' '.join(
                    [t.text for t in ($a or []) + ($b or [])]
                    + [t.toStringTree() for t in ($f or [])]
                    + [$k.text]
                    + [t.text for t in ($c or []) + ($d or [])]
                    + [t.toStringTree() for t in ($e or [])]))) }
                 -> ^( PROPERTIES ^( $k ^( PROPERTIES $a* $b+ $f+ )
                                        ^( PROPERTIES $c+ $d+ $e* ) ) )
               )
             );

// Lists

adj_list : adjective ( ','! ( ( adjective | noun ) ','! )+ )?
           conj^ ( adjective | noun );

noun_list : noun+ ( ','! ( noun+ ','! )+ )? conj^ noun+;

// Adjectives

adjective : NON^? ( supertype | color | color_spec | status );

color : WHITE | BLUE | BLACK | RED | GREEN;
color_spec : COLORED | COLORLESS | MONOCOLORED | MULTICOLORED;
status : TAPPED
       | UNTAPPED
       | ENCHANTED
       | EQUIPPED
       | FORTIFIED
       | HAUNTED
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
           | own;
           //| other_than
           //| in_zones;

named : NAMED^ REFBYNAME;

// TODO: expand
control : YOU CONTROL;
own : YOU OWN;
