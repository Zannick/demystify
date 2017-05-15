parser grammar raw_keywords;

// This file is part of Demystify.
// 
// Demystify: a Magic: The Gathering parser
// Copyright (C) 2012 Benjamin S Wolf
// 
// Demystify is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 3 of the License,
// or (at your option) any later version.
// 
// Demystify is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

/* Raw keyword definitions, for references within other abilities. */

raw_keywords : raw_keyword
               ( ( COMMA! ( raw_keyword COMMA! )+ )? conj^ raw_keyword )? ;

raw_keyword : raw_keyword_no_args
            | raw_keyword_int
            | raw_keyword_cost
            | raw_keyword_int_cost
            | raw_keyword_quality
            | ENCHANT
            | PROTECTION
            | AFFINITY
            | CHAMPION
            | KICKER
            | LANDWALK
            | SPLICE
            ;

raw_keyword_with_no_args : raw_keyword_no_args
                         | VANISHING
                         ;

raw_keyword_with_cost : raw_keyword_cost
                      | raw_keyword_int_cost
                      | KICKER
                      | SPLICE
                      ;

// TODO: the values of this can be referred to as "points of keyword",
// eg. "for each point of bushido it has"
raw_keyword_with_int : raw_keyword_int
                     | raw_keyword_int_cost
                     ;

// This happens to include things that use more specialized quality args.
raw_keyword_with_quality : raw_keyword_quality
                         | ENCHANT
                         | PROTECTION
                         | AFFINITY
                         | CHAMPION
                         | LANDWALK
                         | SPLICE
                         ;

// The lists of raw_keyword_(.*) below are for the generic keyword rules
// keyword_\1 in keywords.g. Each keyword should appear in at most one of
// these lists. For keywords that have a particular type of argument, use
// the raw_keyword_with_\1 rules above.

// core first, then expert.
raw_keyword_no_args : DEATHTOUCH
                    | DEFENDER
                      // Some keywords e.g. double strike use macro rules.
                    | double_strike
                    | first_strike
                    | FLASH
                    | FLYING
                    | HASTE
                    | HEXPROOF
                    | INDESTRUCTIBLE
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
                    | CIPHER
                    | CONSPIRE
                    | CONVOKE
                    | DELVE
                    | DETHRONE
                    | DEVOID
                    | EPIC
                    | EVOLVE
                    | EXALTED
                    | EXPLOIT
                    | EXTORT
                    | FEAR
                    | FLANKING
                    | FUSE
                    | GRAVESTORM
                    | HAUNT
                    | HIDEAWAY
                    | HORSEMANSHIP
                    | IMPROVISE
                    | INFECT
                    | INGEST
                    | LIVING_WEAPON
                    | MELEE
                    | MENACE
                    | MYRIAD
                    | PARTNER
                    | PERSIST
                    | PHASING
                    | PROVOKE
                    | PROWESS
                    | REBOUND
                    | RETRACE
                    | SHADOW
                    | SKULK
                    | SOULBOND
                    | SPLIT_SECOND
                    | STORM
                    | SUNBURST
                    | TOTEM_ARMOR
                    | UNDAUNTED
                    | UNDYING
                    | UNLEASH
                    | WITHER
                    ;

raw_keyword_cost : EQUIP
                 | aura_swap
                 | BESTOW
                 | BUYBACK
                 | CUMULATIVE_UPKEEP
                 | CYCLING
                 | DASH
                 | ECHO
                 | EMBALM
                 | EMERGE
                 | ENTWINE
                 | ESCALATE
                 | EVOKE
                 | FLASHBACK
                 | FORTIFY
                 | level_up
                 | MADNESS
                 | MEGAMORPH
                 | MIRACLE
                 | MORPH
                 | MULTIKICKER
                 | NINJUTSU
                 | OUTLAST
                 | OVERLOAD
                 | PROWL 
                 | RECOVER
                 | REPLICATE
                 | SCAVENGE
                 | SURGE
                 | TRANSFIGURE
                 | TRANSMUTE
                 | UNEARTH
                 ;

raw_keyword_int : ABSORB
                | AMPLIFY
                | ANNIHILATOR
                | BLOODTHIRST
                | BUSHIDO
                | CREW
                | DEVOUR
                | DREDGE
                | FABRICATE
                | FADING
                | FRENZY
                | GRAFT
                | MODULAR
                | POISONOUS
                | RAMPAGE
                | RENOWN
                | RIPPLE
                | SOULSHIFT
                | TRIBUTE
                | VANISHING
                ;

raw_keyword_int_cost : AWAKEN
                     | REINFORCE
                     | SUSPEND
                     ;

raw_keyword_quality : bands_with_other
                    ;

/* Keyword actions. */

raw_keyword_action : raw_keyword_action_no_args
                   | raw_keyword_action_int
                   ;

raw_keyword_action_no_args : MANIFEST
                           | POPULATE
                           | PROLIFERATE
                           ;

raw_keyword_action_int : BOLSTER
                       | FATESEAL
                       | MONSTROSITY
                       | SCRY
                       ;
