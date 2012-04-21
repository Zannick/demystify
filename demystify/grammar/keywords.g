parser grammar keywords;

/* Keywords, in the official Magic parlance. */

/* For the purposes of this file, there are three types of keywords:
 *
 * Keyword actions, which are verbs used in sentences (aside from some
 *   ubiquitous keyword actions used elsewhere in this grammar).
 * Listable keywords, which are usually placed at the top of the card in a
 *   list, though they don't have to be (e.g. when reminder text is included).
 * Standalone keywords, which must go on their own line.
 *
 * These appear generally in a form containing some fixed text
 * relating to the keyword and 0-2 arguments, each of which is either
 * an integer, a cost, or a quality.
 *
 * For example:
 *   Suspend (number) -- (cost)
 *   (quality)cycling
 *   Protection from (quality)
 *   (quality)walk
 *
 * Keywords may also appear in a fixed short form for when abilities grant
 * keyword abilities, remove keyword abilities, or make reference to objects
 * having keyword abilities.
 */

keywords : keyword ( ( COMMA | SEMICOLON ) keyword )* -> ^( KEYWORDS keyword+ )
         | keyword_one_line -> ^( KEYWORDS keyword_one_line )
         ;

keyword_one_line : keyword_int_cost
                 | keyword_enchant
                 | keyword_champion
                 | keyword_splice
                 ;

keyword : keyword_int
        | keyword_cost
        | keyword_no_args
        | keyword_multiword
        | keyword_landwalk
        | keyword_protection
        | keyword_affinity
        | keyword_kicker
        | keyword_offering
        | keyword_typecycling
        ;

// core first, then expert.
keyword_no_args : DEATHTOUCH
                | DEFENDER
                | FLASH
                | FLYING
                | HASTE
                | HEXPROOF
                | INTIMIDATE
                | LIFELINK
                | REACH
                | SHROUD
                | TRAMPLE
                | VIGILANCE
                | BANDING
                | BATTLE_CRY
                | CASCADE
                | CHANGELING
                | CONSPIRE
                | CONVOKE
                | DELVE
                | EPIC
                | EXALTED
                | FEAR
                | FLANKING
                | GRAVESTORM
                | HAUNT
                | HIDEAWAY
                | HORSEMANSHIP
                | INFECT
                | LIVING_WEAPON
                | PERSIST
                | PHASING
                | PROVOKE
                | REBOUND
                | RETRACE
                | SHADOW
                | SPLIT_SECOND
                | STORM
                | SUNBURST
                | TOTEM_ARMOR
                | UNDYING
                // Vanishing can appear with or without an argument.
                | VANISHING
                | WITHER
                ;

/* Special case keywords. */

keyword_affinity : AFFINITY^ FOR! keyword_arg_quality ;

keyword_champion : CHAMPION A keyword_arg_quality
                   ( OR keyword_arg_quality
                     -> ^( CHAMPION ^( OR keyword_arg_quality+ ) )
                   | -> ^( CHAMPION keyword_arg_quality )
                   )
                 ;

keyword_enchant : ENCHANT^ ( properties | player_subset );

keyword_kicker : KICKER^ keyword_arg_cost ( AND_OR! keyword_arg_cost )? ;

keyword_landwalk : keyword_arg_quality WALK
                   -> ^( LANDWALK keyword_arg_quality )
                 | keyword_arg_quality LANDWALK
                   -> ^( LANDWALK[] keyword_arg_quality );

keyword_offering : keyword_arg_quality OFFERING^ ;

keyword_protection : PROTECTION^ FROM! keyword_arg_prot
                     ( ( COMMA! ( FROM! keyword_arg_prot COMMA! )+ )?
                       AND! FROM! keyword_arg_prot )? ;

keyword_splice : SPLICE^ ONTO! keyword_arg_quality keyword_arg_cost ;

keyword_typecycling : keyword_arg_quality CYCLING keyword_arg_cost
                      -> ^( TYPECYCLING keyword_arg_quality keyword_arg_cost );

/* Keywords with arguments in a generic form. */

keyword_int : ( ABSORB
              | AMPLIFY
              | ANNIHILATOR
              | BLOODTHIRST
              | BUSHIDO
              | DEVOUR
              | DREDGE
              | FADING
              | FRENZY
              | GRAFT
              | MODULAR
              | POISONOUS
              | RAMPAGE
              | RIPPLE
              | SOULSHIFT
              | VANISHING
              )^ keyword_arg_int ;

keyword_cost : ( EQUIP
               | BUYBACK
               | CUMULATIVE_UPKEEP
               | CYCLING
               | ECHO
               | ENTWINE
               | EVOKE
               | FLASHBACK
               | FORTIFY
               | MADNESS
               | MORPH
               | MULTIKICKER
               | NINJUTSU
               | PROWL 
               | RECOVER
               | REPLICATE
               | TRANSFIGURE
               | TRANSMUTE
               | UNEARTH
               )^ keyword_arg_cost ;

keyword_int_cost : ( REINFORCE
                   | SUSPEND
                   )^ keyword_arg_int MDASH! keyword_arg_cost ;

// Multiword keywords here, to cut down on rewrite rule spam.
keyword_multiword : FIRST STRIKE -> FIRST_STRIKE
                  | DOUBLE STRIKE -> DOUBLE_STRIKE
                  | AURA SWAP keyword_arg_cost -> AURA_SWAP keyword_arg_cost
                  | BAND WITH OTHER keyword_arg_quality
                    -> ^( BANDS_WITH_OTHER keyword_arg_quality )
                  | LEVEL UP keyword_arg_cost -> LEVEL_UP keyword_arg_cost
                  ;

/* Argument rules. */

// TODO: the values of this can be referred to as "points of keyword",
// eg. "for each point of bushido it has"
keyword_arg_int : NUMBER_SYM -> ^( INT NUMBER_SYM )
                | VAR_SYM -> ^( INT ^( VAR VAR_SYM ) )
                | MDASH SUNBURST -> ^( INT SUNBURST );

// Costs can include standard cost items, plus some new ones:
// "Gain control of a land you don't control"
// "Put [creatures] onto the battlefield under an opponent's control."
// "Add [mana] to your mana pool."
// "Flip a coin."
// "An opponent gains [life]."
// "Draw a card."
// in general many actions can be keyword costs like this. These are all
// cumulative upkeep costs; the gain life one appears in splice as well.
// The general idea is that it's a drawback, or in the case of cumulative
// upkeep, finite or dangerous.
// eg. "gain a poison counter" could work.
// TODO: Add these new cost items.
keyword_arg_cost : cost ;

// TODO: better distinguish quality args.
//       (eg. typecyclying takes only simple_properties,
//            protection takes this, and enchant takes properties)
keyword_arg_prot : keyword_arg_quality
                 | int_prop_with_value
                 | EVERYTHING -> ALL
                 | ALL COLOR -> COLORED
                 ;

// Quality can include generic properties as well as other special qualities
// as in "protection from everything" or "protection from all colors".
// More than that, it can include adjectives on their own.
keyword_arg_quality : simple_properties ;
