parser grammar subsets;

/* Rules for describing subsets of objects. */

subsets : subset ( ( ( ','! subset )+ ','! )? conj^ subset )?;

subset : number properties -> ^( SUBSET number properties )
       | AMONG properties -> ^( SUBSET ^( NUMBER ANY ) properties )
       | ANOTHER properties -> ^( SUBSET ^( NOT SELF ) properties )
       //| spec-zone -> ^( SUBSET spec-zone )
       | ref_object descriptor* -> ^( SUBSET ref_object descriptor* );

/* Numbers and quantities. */

number : ( s=NUMBER_SYM | w=number_word )
         ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ $s? $w? ) )
         | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ $s? $w? ) )
         | -> ^( NUMBER $s? $w? )
         )
       | b=VAR_SYM ( OR ( MORE | GREATER ) -> ^( NUMBER ^( GEQ ^( VAR $b ) ) )
                   | OR ( FEWER | LESS ) -> ^( NUMBER ^( LEQ ^( VAR $b ) ) )
                   | -> ^( NUMBER ^( VAR $b ) )
                   )
       | ALL -> ^( NUMBER ALL )
       | ANY ( c=number_word -> ^( NUMBER $c )
             | NUMBER OF -> ^( NUMBER ANY )
             | -> ^( NUMBER NUMBER[$ANY, 1] )
             )
       | A SINGLE? -> ^( NUMBER NUMBER[$A, "1"] );

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
       //| ENCHANTED
       //| EQUIPPED
       //| FORTIFIED
       //| HAUNTED
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
           | other_than;
           //| in_zones;

named : NAMED^ REFBYNAME;

// TODO: expand
control : YOU CONTROL;
own : YOU OWN;

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
             // We probably don't actually need to remember what the
             // nouns were here, but keep them in for now.
           | ( ENCHANTED | EQUIPPED | FORTIFIED | HAUNTED ) noun+
           | this_guy;

// eg. this creature, this permanent, this spell.
this_guy : THIS ( type | obj_type ) -> SELF;

/* Counter subsets. */

counter_subset : counter_group
                 ( ( ',' ( counter_group ',' )+ )? conj counter_group
                   -> ^( COUNTER_SET ^( conj counter_group+) )
                 | -> ^( COUNTER_SET counter_group )
                 );
 
counter_group : number ( obj_counter | pt )? COUNTER
                -> ^( COUNTER_GROUP number obj_counter? pt? );
