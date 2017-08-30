# This file is part of Demystify.
# 
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2012 Benjamin S Wolf
# 
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

"""keywords -- Library of Magic: The Gathering terms.

If run as a script, automatically outputs an ANTLR v3 lexer grammar, Words.g,
which forms the vast majority of Demystify's language, and an ANTLR v3 parser
grammar, macro.g, which combines similar tokens into parser rules. """

# Because Magic is essentially a subset of English language, we need to
# include multiple parts of speech for every word. For verbs, we need
# present and past tenses, sometimes progressive tense, and occasionally
# a noun form. For nouns, we need singular and plural.

# Because most verbs have multiple present tenses depending on the subject,
# and because some nouns are also verbs, we choose to represent the present
# tense as any of them (eg. both "discard" and "discards" map to the DISCARD
# token). Similarly, the noun tokens represent both singular and plural noun
# forms.

# Note that the way this is done will make the language much wider than
# necessary, allowing strange constructions like "you discards" or
# "its controllers' untap step". This is okay since we don't need to be strict
# given that we have a finite (albeit regularly increasing) card pool, and
# our objective is not to disallow poorly worded Magic cards but to interpret
# all existing Magic cards.

# Some keywords are technically multiple words, such as "first strike" and
# "cumulative upkeep". For lexing clarity, these are tokenized separately
# if the first word appears elsewhere in Magic's vocabulary. Hence "first
# strike" will be split into "first" and "strike" while "cumulative upkeep"
# will not be split at all.

class Keyword(object):
    """ Common superclass for the types of words that are used here.
        Allows export of a mini-dictionary that contains words and tokens. """
    def __init__(self, *tokenlists):
        """ Each element of tokenlists should be a list of strings
            (token, *ids) where token is a string, eg. "ACTION",
            and the rest of the list are ids, eg. ("action", "actions"). """
        self.dict = {w: ts[0] for ts in tokenlists if ts for w in ts[1:]}

class Verb(Keyword):
    """ All verbs must have present and past tenses.
        Others are optional. Each tense is a list, with the first
        value being the token used to represent the other words
        in the list.
        
        The noun, if provided, should be the word meaning the act of
        (this verb), and not meaning one that is the subject or predicate
        of the action. For example, "ACTIVATION" would be appropriate for
        "ACTIVATE", but "ATTACKER" would not be for "ATTACK". """
    def __init__(self, present, past, progressive=(), noun=()):
        self.type = present[0]
        self.present = present
        self.past = past
        self.progressive = progressive
        self.noun = noun
        super(Verb, self).__init__(present, past, progressive, noun)

class Noun(Keyword):
    """ Nouns are different from verbs in that only one form of a token
        is provided, and the rest are generated.
        A noun must have both forms given as strings:
            singular, plural.
        Since we no longer generate possessive tokens based on nouns,
        Nouns are now simply Keywords that take exactly two words. """
    def __init__(self, token, singular, plural):
        self.type = token
        self.singular = singular
        self.plural = plural
        super(Noun, self).__init__((token, singular, plural))

actions = {}
_actions = [
    # Player actions
    # These are actions that one can say "I <perform action>"
    # or "Whenever a player <performs action>".

    # Basic actions (mostly straightforward English meanings)
    Verb(   ("ACCEPT", "accept", "accepts"),
            ("ACCEPTED", "accepted")),
    Verb(   ("ADD", "add", "adds"),
            ("ADDED", "added"),
            ("ADDING", "adding")),
    Verb(   ("ANTE", "ante", "antes"),
            ("ANTED", "anted")),
    Verb(   ("ATTACK", "attack", "attacks"),
            ("ATTACKED", "attacked"),
            ("ATTACKING", "attacking")),
    Verb(   ("BEGIN", "begin", "begins"),
            ("BEGAN", "began")),
    Verb(   ("BID", "bid", "bids"),
            ("BID", "bid"),
            ("BIDDING", "bidding"),
            ("BIDDING", "bidding")),
    Verb(   ("BLOCK", "block", "blocks"),
            ("BLOCKED", "blocked"),
            ("BLOCKING", "blocking")),
    Verb(   ("CHANGE", "change", "changes"),
            ("CHANGED", "changed"),
            ("CHANGING", "changing")),
    Verb(   ("CHOOSE", "choose", "chooses"),
            ("CHOSE", "chose"),
            ("CHOOSING", "choosing"),
            ("CHOICE", "choice", "choices")),
    Verb(   ("CONTROL", "control", "controls"),
            ("CONTROLLED", "controlled"),
            ("CONTROLLING", "controlling")),
    Verb(   ("COUNT", "count", "counts"),
            ("COUNTED", "counted")),
    Verb(   ("DECIDE", "decide", "decides"),
            ("DECIDED", "decided"),
            ("DECIDING", "deciding"),
            ("DECISION", "decision")),
    Verb(   ("DECLARE", "declare", "declares"),
            ("DECLARED", "declared"),
            ("DECLARING", "declaring"),
            ("DECLARATION", "declaration")),
    Verb(   ("DISTRIBUTE", "distribute", "distributes"),
            ("DISTRIBUTED", "distributed"),
            ("DISTRIBUTING", "distributing"),
            ("DISTRIBUTION", "distribution")),
    Verb(   ("DIVIDE", "divide", "divides"),
            ("DIVIDED", "divided"),
            ("DIVIDING", "dividing"),
            ("DIVISION", "division")),
    Verb(   ("DO", "do", "does"),
            ("DID", "did"),
            ("DOING", "doing")),
    Verb(   ("DOUBLE", "double", "doubles"),
            ("DOUBLED", "doubled")),
    Verb(   ("DRAW", "draw", "draws"),
            ("DREW", "drew")),
    Verb(   ("EMPTY", "empty", "empties"),
            ("EMPTIED", "emptied")),
    Verb(   ("FINISH", "finish", "finishes"),
            ("FINISHED", "finished")),
    Verb(   ("FLIP", "flip", "flips"),
            ("FLIPPED", "flipped"),
            ("FLIPPING", "flipping")),
    Verb(   ("GAIN", "gain", "gains"),
            ("GAINED", "gained")),
    Verb(   ("GET", "get", "gets"),
            ("GOT", "got")),
    Verb(   ("GIVE", "give", "gives"),
            ("GAVE", "gave"),
            ("GIVING", "giving")),
    Verb(   ("GUESS", "guess", "guesses"),
            ("GUESSED", "guessed"),
            ("GUESSING", "guessing")),
    Verb(   ("HIDE", "hide", "hides"),
            ("HID", "hid")),
    Verb(   ("IGNORE", "ignore", "ignores"),
            ("IGNORED", "ignored")),
    Verb(   ("LOOK", "look", "looks"),
            ("LOOKED", "looked")),
    Verb(   ("LOSE", "lose", "loses"),
            ("LOST", "lost"),
            ("LOSING", "losing"),
            ("LOSS", "loss")),
    Verb(   ("MOVE", "move", "moves"),
            ("MOVED", "moved"),
            ("MOVING", "moving")),
    Verb(   ("NAME", "name", "names"),
            ("NAMED", "named")),
    Verb(   ("NOTE", "note", "notes"),
            ("NOTED", "noted")),
    Verb(   ("OFFER", "offer", "offers"),
            ("OFFERED", "offered")),
    Verb(   ("ORDER", "order", "orders"),
            ("ORDERED", "ordered")),
    Verb(   ("OWN", "own", "owns"),
            ("OWNED", "owned"),
            ("OWNING", "owning"),
            ("OWNERSHIP", "ownership")),
    Verb(   ("PASS", "pass", "passes"),
            ("PASSED", "passed")),
    Verb(   ("PAY", "pay", "pays"),
            ("PAID", "paid"),
            ("PAYING", "paying"),
            ("PAYMENT", "payment")),
    Verb(   ("PREVENT", "prevent", "prevents"),
            ("PREVENTED", "prevented")),
    Verb(   ("PUT", "put", "puts"),
            ("PUT", "put"),
            ("PUTTING", "putting")),
    Verb(   ("REDISTRIBUTE", "redistribute", "redistributes"),
            ("REDISTRIBUTED", "redistributed"),
            ("REDISTRIBUTING", "redistributing"),
            ("REDISTRIBUTION", "redistribution")),
    Verb(   ("REMOVE", "remove", "removes"),
            ("REMOVED", "removed"),
            ("REMOVING", "removing"),
            ("REMOVAL", "removal")),
    Verb(   ("REORDER", "reorder", "reorders"),
            ("REORDERED", "reordered")),
    Verb(   ("REPEAT", "repeat", "repeats"),
            ("REPEATED", "repeated")),
    Verb(   ("REPLACE", "replace", "replaces"),
            ("REPLACED", "replaced"),
            ("REPLACING", "replacing")),
    Verb(   ("RESELECT", "reselect", "reselects"),
            ("RESELECTED", "reselected")),
    Verb(   ("RESTART", "restart", "restarts"),
            ("RESTARTED", "restarted"),
            ("RESTARTING", "restarting")),
    Verb(   ("RETURN", "return", "returns"),
            ("RETURNED", "returned")),
    Verb(   ("ROLL", "roll", "rolls"),
            ("ROLLED", "rolled"),
            ("ROLLING", "rolling")),
    Verb(   ("SELECT", "select", "selects"),
            ("SELECTED", "selected")),
    Verb(   ("SEPARATE", "separate", "separates"),
            ("SEPARATED", "separated")),
    Verb(   ("SKIP", "skip", "skips"),
            ("SKIPPED", "skipped")),
    Verb(   ("SPEND", "spend", "spends"),
            ("SPENT", "spent")),
    Verb(   ("START", "start", "starts"),
            ("STARTED", "started"),
            ("STARTING", "starting")),
    Verb(   ("STOP", "stop", "stops"),
            ("STOPPED", "stopped")),
    Verb(   ("SWITCH", "switch", "switches"),
            ("SWITCHED", "switched")),
    Verb(   ("TAKE", "take", "takes"),
            ("TOOK", "took")),
    Verb(   ("TIE", "tie", "ties"),
            ("TIED", "tied"),
            ("TYING", "tying")),
    Verb(   ("VOTE", "vote", "votes"),
            ("VOTED", "voted"),
            ("VOTING", "voting")),
    Verb(   ("WIN", "win", "wins"),
            ("WON", "won"),
            ("WINNING", "winning")),

    # Keyword actions
    Verb(   ("ACTIVATE", "activate", "activates"),
            ("ACTIVATED", "activated"),
            ("ACTIVATING", "activating"),
            ("ACTIVATION", "activation", "activations")),
    Verb(   ("ATTACH", "attach", "attaches"),
            ("ATTACHED", "attached"),
            ("ATTACHING", "attaching")),
    Verb(   ("CAST", "cast", "casts"),
            ("CAST", "cast"),
            ("CASTING", "casting")),
    Verb(   ("COUNTER", "counter", "counters"),
            ("COUNTERED", "countered"),
            ("COUNTERING", "countering")),
    Verb(   ("CREATE", "create", "creates"),
            ("CREATED", "created")),
    Verb(   ("DESTROY", "destroy", "destroys"),
            ("DESTROYED", "destroyed"),
            ("DESTROYING", "destroying")),
    Verb(   ("DISCARD", "discard", "discards"),
            ("DISCARDED", "discarded"),
            ("DISCARDING", "discarding")),
    Verb(   ("EXCHANGE", "exchange", "exchanges"),
            ("EXCHANGED", "exchanged"),
            ("EXCHANGING", "exchanging"),
            ("EXCHANGE", "exchange")),
    Verb(   ("EXILE", "exile", "exiles"),
            ("EXILED", "exiled"),
            ("EXILING", "exiling")),
    Verb(   ("FIGHT", "fight", "fights"),
            ("FOUGHT", "fought")),
    Verb(   ("PAIR", "pair", "pairs"),
            ("PAIRED", "paired")),
    Verb(   ("PLAY", "play", "plays"),
            ("PLAYED", "played"),
            ("PLAYING", "playing")),
    Verb(   ("REGENERATE", "regenerate", "regenerates"),
            ("REGENERATED", "regenerated"),
            ("REGENERATING", "regenerating"),
            ("REGENERATION", "regeneration")),
    Verb(   ("REVEAL", "reveal", "reveals"),
            ("REVEALED", "revealed"),
            ("REVEALING", "revealing")),
    Verb(   ("SACRIFICE", "sacrifice", "sacrifices"),
            ("SACRIFICED", "sacrificed"),
            ("SACRIFICING", "sacrificing")),
    Verb(   ("SEARCH", "search", "searches"),
            ("SEARCHED", "searched"),
            ("SEARCHING", "searching")),
    Verb(   ("SHUFFLE", "shuffle", "shuffles"),
            ("SHUFFLED", "shuffled"),
            ("SHUFFLING", "shuffling")),
    Verb(   ("TAP", "tap", "taps"),
            ("TAPPED", "tapped"),
            ("TAPPING", "tapping")),
    Verb(   ("UNATTACH", "unattach", "unattaches"),
            ("UNATTACHED", "unattached"),
            ("UNATTACHING", "unattaching")),
    Verb(   ("UNTAP", "untap", "untaps"),
            ("UNTAPPED", "untapped"),
            ("UNTAPPING", "untapping")),
         
    # non-core keyword actions
    Verb(   ("BOLSTER", "bolster", "bolsters"),
            ("BOLSTERED", "bolstered")),
    Verb(   ("CLASH", "clash", "clashes"),
            ("CLASHED", "clashed"),
            ("CLASHING", "clashing"),
            ("CLASH", "clash")),
    Verb(   ("DETAIN", "detain", "detains"),
            ("DETAINED", "detained")),
    Verb(   ("EXERT", "exert", "exerts"),
            ("EXERTED", "exerted")),
    Verb(   ("FATESEAL", "fateseal", "fateseals"),
            ("FATESEALED", "fatesealed"),
            ("FATESEALING", "fatesealing")),
    Verb(   ("GOAD", "goad", "goads"),
            ("GOADED", "goaded"),
            ("GOADING", "goading")),
    Verb(   ("INVESTIGATE", "investigate", "investigates"),
            ("INVESTIGATED", "investigated")),
    Verb(   ("MANIFEST", "manifest", "manifests"),
            ("MANIFESTED", "manifested")),
    Verb(   ("MELD", "meld", "melds"),
            ("MELDED", "melded")),
    Verb(   ("POPULATE", "populate", "populates"),
            ("POPULATED", "populated"),
            ("POPULATING", "populating")),
    Verb(   ("PROLIFERATE", "proliferate", "proliferates"),
            ("PROLIFERATED", "proliferated"),
            ("PROLIFERATING", "proliferating"),
            ("PROLIFERATION", "proliferation")),
    Verb(   ("SCRY", "scry", "scries"),
            ("SCRIED", "scried"),
            ("SCRYING", "scrying")),
    Verb(   ("TRANSFORM", "transform", "transforms"),
            ("TRANSFORMED", "transformed")),

    # special
    Verb(   ("ABANDON", "abandon", "abandons"),
            ("ABANDONED", "abandoned"),
            ("ABANDONING", "abandoning"),
            ("ABANDONMENT", "abandonment")),
    Verb(   ("PLANESWALK", "planeswalk", "planeswalks"),
            ("PLANESWALKED", "planeswalked"),
            ("PLANESWALKING", "planeswalking")),
    Verb(   ("SET_IN_MOTION", "set in motion", "sets in motion"),
            ("SET_IN_MOTION", "set in motion"),
            ("SETTING_IN_MOTION", "setting in motion")),

    # Other (non-player) actions
    Verb(   ("AFFECT", "affect", "affects"),
            ("AFFECTED", "affected")),
    Verb(   ("APPLY", "apply", "applies"),
            ("APPLIED", "applied")),
    Verb(   ("ASSEMBLE", "assemble", "assembles"),
            ("ASSEMBLED", "assembled")),
    Verb(   ("ASSIGN", "assign", "assigns"),
            ("ASSIGNED", "assigned"),
            ("ASSIGNING", "assigning"),
            ("ASSIGNMENT", "assignment")),
    Verb(   ("BECOME", "become", "becomes"),
            ("BECAME", "became")),
    Verb(   ("CAUSE", "cause", "causes"),
            ("CAUSED", "caused")),
    Verb(   ("COME", "come", "comes"),
            ("CAME", "came")),
    Verb(   ("CONTAIN", "contain", "contains"),
            ("CONTAINED", "contained")),
    Verb(   ("CONTINUE", "continue", "continues"),
            ("CONTINUED", "continued")),
    Verb(   ("DEAL", "deal", "deals"),
            ("DEALT", "dealt"),
            ("DEALING", "dealing")),
    Verb(   ("DIE", "die", "dies"),
            ("DIED", "died")),
    Verb(   ("DRAFT", "draft", "drafts"),
            ("DRAFTED", "drafted"),
            ("DRAFTING", "drafting")),
    Verb(   ("END", "end", "ends"),
            ("ENDED", "ended")),
    Verb(   ("ENTER", "enter", "enters"),
            ("ENTERED", "entered"),
            ("ENTERING", "entering")),
    Verb(   ("INCREASE", "increase", "increases"),
            ("INCREASED", "increased")),
    Verb(   ("LEAVE", "leave", "leaves"),
            ("LEFT", "left"),
            ("LEAVING", "leaving")),
    Verb(   ("PLACE", "place", "places"),
            ("PLACED", "placed")),
    Verb(   ("PRODUCE", "produce", "produces"),
            ("PRODUCED", "produced")),
    Verb(   ("REDUCE", "reduce", "reduces"),
            ("REDUCED", "reduced")),
    Verb(   ("REMAIN", "remain", "remains"),
            ("REMAINED", "remained")),
    Verb(   ("RESOLVE", "resolve", "resolves"),
            ("RESOLVED", "resolved"),
            ("RESOLVING", "resolving"),
            ("RESOLUTION", "resolution")),
    Verb(   ("SHARE", "share", "shares"),
            ("SHARED", "shared")),
    Verb(   ("STAND", "stand", "stands"),
            ("STOOD", "stood")),
    Verb(   ("TRIGGER", "trigger", "triggers"),
            ("TRIGGERED", "triggered")),
    Verb(   ("TURN", "turn", "turns"),
            ("TURNED", "turned")),
    Verb(   ("USE", "use", "uses"),
            ("USED", "used"),
            ("USING", "using")),

    # Connective verbs
    Keyword(("ABLE", "able")),
    Verb(   ("BE", "be"),
            ("BEEN", "been"),
            ("BEING", "being")),
    Verb(   ("CAN", "can"),
            ("COULD", "could")),
    Verb(   ("IS", "is", "are", "'re"),
            ("WAS", "was", "were")),
    Verb(   ("HAS", "has", "have", "'ve"),
            ("HAD", "had"),
            ("HAVING", "having")),
    Keyword(("MAY", "may")),
]
for action in _actions:
    actions.update(action.dict)

abilities = {}
_abilities = [
    # core
    Keyword(("DEATHTOUCH", "deathtouch")),
    Keyword(("DEFENDER", "defender")),
    Keyword(("DOUBLE_STRIKE", "double strike")),
    # We use Verbs to describe keywords that can be used like actions
    # though they aren't officially keyword actions.
    # This allows us to define words like "kicked" here with the
    # relevant keyword.
    Verb(   ("ENCHANT", "enchant", "enchants"),
            ("ENCHANTED", "enchanted"),
            ("ENCHANTING", "enchanting")),
    Verb(   ("EQUIP", "equip", "equips"),
            ("EQUIPPED", "equipped"),
            ("EQUIPPING", "equipping")),
    Keyword(("FIRST_STRIKE", "first strike")),
    Keyword(("FLASH", "flash")),
    Keyword(("FLYING", "flying")),
    Keyword(("HASTE", "haste")),
    Keyword(("HEXPROOF", "hexproof")),
    Keyword(("INTIMIDATE", "intimidate")),
    Keyword(("LANDWALK", "landwalk")),
    Keyword(("WALK", "walk")),
    Keyword(("LIFELINK", "lifelink")),
    Keyword(("PROTECTION", "protection")),
    Keyword(("REACH", "reach")),
    Keyword(("SHROUD", "shroud")),
    Verb(   ("TRAMPLE", "trample", "tramples"),
            ("TRAMPLED", "trampled"),
            ("TRAMPLING", "trampling")),
    Keyword(("VIGILANCE", "vigilance")),

    # set/block-specific "expert level expansions"
    Verb(   ("ABSORB", "absorb", "absorbs"),
            ("ABSORBED", "absorbed"),
            ("ABSORBING", "absorbing")),
    Keyword(("AFFINITY", "affinity")),
    Verb(   ("AFFLICT", "afflict", "afflicts"),
            ("AFFLICTED", "afflicted")),
    Keyword(("AFTERMATH", "aftermath")),
    Verb(   ("AMPLIFY", "amplify", "amplifies"),
            ("AMPLIFIED", "amplified")),
    Keyword(("ANNIHILATOR", "annihilator")),
    Keyword(("AURA_SWAP", "aura swap")),
    Verb(   ("SWAP", "swap", "swaps"),
            ("SWAPPED", "swapped")),
    Verb(   ("AWAKEN", "awaken", "awakens"),
            ("AWAKENED", "awakened")),
    Keyword(("BATTLE_CRY", "battle cry")),
    Verb(   ("BESTOW", "bestow"),
            ("BESTOWED", "bestowed")),
    Keyword(("BLOODTHIRST", "bloodthirst")),
    Keyword(("BUSHIDO", "bushido")),
    Keyword(("BUYBACK", "buyback")),
    Keyword(("CASCADE", "cascade")),
    Verb(   ("CHAMPION", "champion", "champions"),
            ("CHAMPIONED", "championed")),
    Keyword(("CHANGELING", "changeling")),
    Keyword(("CIPHER", "cipher")),
    Verb(   ("EMBALM", "embalm", "embalms"),
            ("EMBALMED", "embalmed")),
    Verb(   ("ENCODE", "encode", "encodes"),
            ("ENCODED", "encoded")),
    Verb(   ("CONSPIRE", "conspire", "conspires"),
            ("CONSPIRED", "conspired")),
    Keyword(("CONVOKE", "convoke")),
    Verb(   ("CREW", "crew", "crews"),
            ("CREWED", "crewed")),
    Keyword(("CUMULATIVE_UPKEEP", "cumulative upkeep")),
    Verb(   ("CYCLE", "cycle", "cycles"),
            ("CYCLED", "cycled"),
            ("CYCLING", "cycling")),
    Keyword(("DASH", "dash")),
    Keyword(("DELVE", "delve")),
    Keyword(("DETHRONE", "dethrone")),
    Keyword(("DEVOID", "devoid")),
    Verb(   ("DEVOUR", "devour", "devours"),
            ("DEVOURED", "devoured")),
    Keyword(("DREDGE", "dredge")),
    Keyword(("ECHO", "echo")),
    Verb(   ("EMERGE", "emerge", "emerges"),
            ("EMERGED", "emerged")),
    Keyword(("ENTWINE", "entwine")),
    Keyword(("EPIC", "epic")),
    Verb(   ("ESCALATE", "escalate", "escalates"),
            ("ESCALATED", "escalated")),
    Verb(   ("ETERNALIZE", "eternalize", "eternalizes"),
            ("ETERNALIZED", "eternalized")),
    Verb(   ("EVOKE", "evoke", "evokes"),
            ("EVOKED", "evoked")),
    Verb(   ("EVOLVE", "evolve", "evolves"),
            ("EVOLVED", "evolved")),
    Keyword(("EXALTED", "exalted")),
    Verb(   ("EXPLOIT", "exploit", "exploits"),
            ("EXPLOITED", "exploited")),
    Verb(   ("EXTORT", "extort", "extorts"),
            ("EXTORTED", "extorted")),
    Verb(   ("FABRICATE", "fabricate", "fabricates"),
            ("FABRICATED", "fabricated")),
    Keyword(("FADING", "fading")),
    Keyword(("FLANKING", "flanking")),
    Keyword(("FLASHBACK", "flashback")),
    Keyword(("FORECAST", "forecast")),
    Verb(   ("FORTIFY", "fortify", "fortifies"),
            ("FORTIFIED", "fortified")),
    Keyword(("FRENZY", "frenzy")),
    Verb(   ("FUSE", "fuse", "fuses"),
            ("FUSED", "fused")),
    Verb(   ("GRAFT", "graft", "grafts"),
            ("GRAFTED", "grafted")),
    Keyword(("GRAVESTORM", "gravestorm")),
    Verb(   ("HAUNT", "haunt", "haunts"),
            ("HAUNTED", "haunted"),
            ("HAUNTING", "haunting")),
    Keyword(("HIDEAWAY", "hideaway")),
    Keyword(("HORSEMANSHIP", "horsemanship")),
    Verb(   ("IMPROVISE", "improvise", "improvises"),
            ("IMPROVISED", "improvised")),
    Keyword(("INDESTRUCTIBLE", "indestructible")),
    Keyword(("INFECT", "infect")),
    Keyword(("INGEST", "ingest")),
    Keyword(("KICKER", "kicker")),
    Verb(   ("KICK", "kick", "kicks"),
            ("KICKED", "kicked")),
    Keyword(("LEVEL_UP", "level up")),
    Keyword(("LIVING_WEAPON", "living weapon")),
    Keyword(("MADNESS", "madness")),
    Keyword(("MEGAMORPH", "megamorph")),
    Keyword(("MELEE", "melee")),
    Keyword(("MENACE", "menace")),
    Keyword(("MIRACLE", "miracle")),
    Keyword(("MODULAR", "modular")),
    Keyword(("MONSTROSITY", "monstrosity")),
    Keyword(("MORPH", "morph")),
    Keyword(("MYRIAD", "myriad")),
    Keyword(("MULTIKICKER", "multikicker")),
    Keyword(("NINJUTSU", "ninjutsu")),
    Keyword(("OFFERING", "offering")),
    Keyword(("OUTLAST", "outlast")),
    Verb(   ("OVERLOAD", "overload", "overloads"),
            ("OVERLOADED", "overloaded")),
    Noun("PARTNER", "partner", "partners"),
    Keyword(("PERSIST", "persist")),
    # Phasing
    Verb(   ("PHASE", "phase", "phases"),
            ("PHASED", "phased"),
            ("PHASING", "phasing")),
    Keyword(("POISONOUS", "poisonous")),
    Verb(   ("PROVOKE", "provoke", "provokes"),
            ("PROVOKED", "provoked")),
    Keyword(("PROWESS", "prowess")),
    Keyword(("PROWL", "prowl")),
    Keyword(("RAMPAGE", "rampage")),
    Keyword(("REBOUND", "rebound")),
    Verb(   ("RECOVER", "recover", "recovers"),
            ("RECOVERED", "recovered")),
    Verb(   ("REINFORCE", "reinforce", "reinforces"),
            ("REINFORCED", "reinforced")),
    Keyword(("RENOWN", "renown"),
            ("RENOWNED", "renowned")),
    Verb(   ("REPLICATE", "replicate", "replicates"),
            ("REPLICATED", "replicated")),
    Keyword(("RETRACE", "retrace")),
    Keyword(("RIPPLE", "ripple")),
    Verb(   ("SCAVENGE", "scavenge", "scavenges"),
            ("SCAVENGED", "scavenged")),
    Keyword(("SHADOW", "shadow")),
    Keyword(("SKULK", "skulk")),
    Keyword(("SOULBOND", "soulbond")),
    Keyword(("SOULSHIFT", "soulshift")),
    Verb(   ("SPLICE", "splice", "splices"),
            ("SPLICED", "spliced")),
    Keyword(("SPLIT_SECOND", "split second")),
    Keyword(("STORM", "storm")),
    Keyword(("SUNBURST", "sunburst")),
    Verb(   ("SUPPORT", "support", "supports"),
            ("SUPPORTED", "supported")),
    Verb(   ("SURGE", "surge", "surges"),
            ("SURGED", "surged")),
    Verb(   ("SUSPEND", "suspend", "suspends"),
            ("SUSPENDED", "suspended")),
    Keyword(("TOTEM_ARMOR", "totem armor")),
    Keyword(("TRANSFIGURE", "transfigure")),
    Verb(   ("TRANSMUTE", "transmute", "transmutes"),
            ("TRANSMUTED", "transmuted")),
    Keyword(("TRIBUTE", "tribute")),
    Keyword(("TYPECYCLING", "typecycling")),
    Keyword(("UNDAUNTED", "undaunted")),
    Keyword(("UNDYING", "undying")),
    Verb(   ("UNEARTH", "unearth", "unearths"),
            ("UNEARTHED", "unearthed")),
    Verb(   ("UNLEASH", "unleash", "unleashes"),
            ("UNLEASHED", "unleashed")),
    Keyword(("VANISHING", "vanishing")),
    Keyword(("WITHER", "wither")),
    # Dead
    # Banding and Bands with other
    Verb(   ("BAND", "band", "bands"),
            ("BANDED", "banded"),
            ("BANDING", "banding")),
    Keyword(("BANDS_WITH_OTHER", "bands with other")),
    Keyword(("FEAR", "fear")),
]
for ability in _abilities:
    abilities.update(ability.dict)

# These have no rules meaning but may show up in text.
ability_words = {}
_ability_words = [
    Keyword(("BATTALION", "battalion")),
    Keyword(("BLOODRUSH", "bloodrush")),
    Keyword(("CHANNEL", "channel")),
    Keyword(("CHROMA", "chroma")),
    Keyword(("COHORT", "cohort")),
    Keyword(("CONSTELLATION", "constellation")),
    Keyword(("CONVERGE", "converge")),
    Keyword(("COUNCILS_DILEMMA", "council's dilemma")),
    Keyword(("DELIRIUM", "delirium")),
    Keyword(("DOMAIN", "domain")),
    Keyword(("EMINENCE", "eminence")),
    Keyword(("FATEFUL_HOUR", "fateful hour")),
    Keyword(("FEROCIOUS", "ferocious")),
    Keyword(("FORMIDABLE", "formidable")),
    Keyword(("GRANDEUR", "grandeur")),
    Keyword(("HELLBENT", "hellbent")),
    Keyword(("HEROIC", "heroic")),
    Keyword(("IMPRINT", "imprint")),
    Keyword(("INSPIRED", "inspired")),
    Keyword(("JOIN_FORCES", "join forces")),
    Keyword(("KINSHIP", "kinship")),
    Keyword(("LANDFALL", "landfall")),
    Keyword(("LIEUTENANT", "lieutenant")),
    Keyword(("METALCRAFT", "metalcraft")),
    Keyword(("MORBID", "morbid")),
    Keyword(("PARLEY", "parley")),
    Keyword(("RADIANCE", "radiance")),
    Keyword(("RAID", "raid")),
    Keyword(("RALLY", "rally")),
    Keyword(("REVOLT", "revolt")),
    Keyword(("SPELL_MASTERY", "spell mastery")),
    Keyword(("STRIVE", "strive")),
    Keyword(("SWEEP", "sweep")),
    Keyword(("TEMPTING_OFFER", "tempting offer")),
    Keyword(("THRESHOLD", "threshold")),
    Keyword(("WILL_OF_THE_COUNCIL", "will of the council")),
]
for aword in _ability_words:
    ability_words.update(aword.dict)

# Object, player, and card types
types = {}
_types = [
    Noun("TYPE", "type", "types"),
    Noun("SUPERTYPE", "supertype", "supertypes"),
    Noun("SUBTYPE", "subtype", "subtypes"),
    Noun("OBJECT", "object", "objects"),
    Noun("ABILITY", "ability", "abilities"),
    Noun("CARD", "card", "cards"),
    Noun("COPY", "copy", "copies"),
    Noun("COUNTER", "counter", "counters"),
    Noun("EFFECT", "effect", "effects"),
    Noun("PERMANENT", "permanent", "permanents"),
    Noun("SOURCE", "source", "sources"),
    Noun("SPELL", "spell", "spells"),
    Noun("TOKEN", "token", "tokens"),

    # Card Types
    Noun("ARTIFACT", "artifact", "artifacts"),
    Noun("CREATURE", "creature", "creatures"),
    Noun("ENCHANTMENT", "enchantment", "enchantments"),
    Noun("INSTANT", "instant", "instants"),
    Noun("LAND", "land", "lands"),
    Noun("PLANESWALKER", "planeswalker", "planeswalkers"),
    Noun("SORCERY", "sorcery", "sorceries"),
    Noun("TRIBAL", "tribal", "tribals"),

    # Player types
    Noun("PLAYER", "player", "players"),
    Noun("TEAMMATE", "teammate", "teammates"),
    Noun("OPPONENT", "opponent", "opponents"),
    Noun("CONTROLLER", "controller", "controllers"),
    Noun("OWNER", "owner", "owners"),
    Noun("BIDDER", "bidder", "bidders"),
    Noun("MONARCH", "monarch", "monarchs"),
    Keyword(("ACTIVE", "active")),
    Keyword(("ATTACKING", "attacking")),
    Keyword(("DEFENDING", "defending")),

    # Mana and Color Types
    Noun("MANA", "mana", "mana"),
    Noun("COLOR", "color", "colors"),
    Keyword(("WHITE", "white")),
    Keyword(("BLUE", "blue")),
    Keyword(("BLACK", "black")),
    Keyword(("RED", "red")),
    Keyword(("GREEN", "green")),
    Keyword(("COLORLESS", "colorless")),
    Keyword(("COLORED", "colored")),
    Keyword(("MONOCOLORED", "monocolored")),
    Keyword(("MULTICOLORED", "multicolored")),

    # Other Types
    Noun("COMMANDER", "commander", "commanders"),
    Noun("EMBLEM", "emblem", "emblems"),
    Noun("PHENOMENON", "phenomenon", "phenomena"),
    Noun("PLANE", "plane", "planes"),
    Noun("SCHEME", "scheme", "schemes"),
    Noun("VANGUARD", "vanguard", "vanguards"),

    # Supertypes
    Keyword(("BASIC", "basic")),
    Keyword(("LEGENDARY", "legendary")),
    Keyword(("SNOW", "snow")),
    Keyword(("WORLD", "world")),
    Keyword(("ONGOING", "ongoing")),
]
for t in _types:
    types.update(t.dict)

# Subtypes (generally nouns)
_artifact_types = [
    Noun("CLUE", "clue", "clues"),
    Noun("CONTRAPTION", "contraption", "contraptions"),
    Noun("EQUIPMENT", "equipment", "equipment"),
    Noun("FORTIFICATION", "fortification", "fortifications"),
    Noun("VEHICLE", "vehicle", "vehicles"),
]

_enchantment_types = [
    Noun("AURA", "aura", "auras"),
    Noun("CARTOUCHE", "cartouche", "cartouche"),
    Noun("CURSE", "curse", "curses"),
    Noun("SHRINE", "shrine", "shrines"),
]

_land_types = [
    Noun("DESERT", "desert", "deserts"),
    Noun("FOREST", "forest", "forests"),
    Noun("GATE", "gate", "gates"),
    Noun("ISLAND", "island", "islands"),
    Noun("LAIR", "lair", "lairs"),
    Noun("LOCUS", "locus", "loci"),
    Noun("MINE", "mine", "mines"),
    Noun("MOUNTAIN", "mountain", "mountains"),
    Noun("PLAINS", "plains", "plains"),
    Noun("POWER_PLANT", "power-plant", "power-plants"),
    Noun("SWAMP", "swamp", "swamps"),
    Noun("TOWER", "tower", "towers"),
    Keyword(("URZAS", "urza's")),
]

_planeswalker_types = [
    Keyword(("AJANI", "ajani")),
    Keyword(("ARLINN", "arlinn")),
    Keyword(("ASHIOK", "ashiok")),
    Keyword(("BOLAS", "bolas")),
    Keyword(("CHANDRA", "chandra")),
    Keyword(("DACK", "dack")),
    Keyword(("DARETTI", "daretti")),
    Keyword(("DOMRI", "domri")),
    Keyword(("DOVIN", "dovin")),
    Keyword(("ELSPETH", "elspeth")),
    Keyword(("FREYALISE", "freyalise")),
    Keyword(("GARRUK", "garruk")),
    Keyword(("GIDEON", "gideon")),
    Keyword(("JACE", "jace")),
    Keyword(("KARN", "karn")),
    Keyword(("KAYA", "kaya")),
    Keyword(("KIORA", "kiora")),
    Keyword(("KOTH", "koth")),
    Keyword(("LILIANA", "liliana")),
    Keyword(("NAHIRI", "nahiri")),
    Keyword(("NARSET", "narset")),
    Keyword(("NISSA", "nissa")),
    Keyword(("NIXILIS", "nixilis")),
    Keyword(("RAL", "ral")),
    Keyword(("SAHEELI", "saheeli")),
    Keyword(("SAMUT", "samut")),
    Keyword(("SARKHAN", "sarkhan")),
    Keyword(("SORIN", "sorin")),
    Keyword(("TAMIYO", "tamiyo")),
    Keyword(("TEFERI", "teferi")),
    Keyword(("TEZZERET", "tezzeret")),
    Keyword(("TIBALT", "tibalt")),
    Keyword(("UGIN", "ugin")),
    Keyword(("VENSER", "venser")),
    Keyword(("VRASKA", "vraska")),
    Keyword(("XENAGOS", "xenagos")),
]

_spell_types = [
    Keyword(("ARCANE", "arcane")),
    Noun("TRAP", "trap", "traps"),
]

_creature_types = [
    Noun("ADVISOR", "advisor", "advisors"),
    Noun("AETHERBORN", "aetherborn", "aetherborn"),
    Noun("ALLY", "ally", "allies"),
    Noun("ANGEL", "angel", "angels"),
    Noun("ANTEATER", "anteater", "anteaters"),
    Noun("ANTELOPE", "antelope", "antelopes"),
    Noun("APE", "ape", "apes"),
    Noun("ARCHER", "archer", "archers"),
    Noun("ARCHON", "archon", "archons"),
    Noun("ARTIFICER", "artificer", "artificers"),
    Noun("ASSASSIN", "assassin", "assassins"),
    Noun("ASSEMBLY_WORKER", "assembly-worker", "assembly-workers"),
    Noun("ATOG", "atog", "atogs"),
    Noun("AUROCHS", "aurochs", "aurochs"),
    Noun("AVATAR", "avatar", "avatars"),
    Noun("BADGER", "badger", "badgers"),
    Noun("BARBARIAN", "barbarian", "barbarians"),
    Noun("BASILISK", "basilisk", "basilisks"),
    Noun("BAT", "bat", "bats"),
    Noun("BEAR", "bear", "bears"),
    Noun("BEAST", "beast", "beasts"),
    Noun("BEEBLE", "beeble", "beebles"),
    Noun("BERSERKER", "berserker", "berserkers"),
    Noun("BIRD", "bird", "birds"),
    Noun("BLINKMOTH", "blinkmoth", "blinkmoths"),
    Noun("BOAR", "boar", "boars"),
    Noun("BRINGER", "bringer", "bringers"),
    Noun("BRUSHWAGG", "brushwagg", "brushwaggs"),
    Noun("CAMARID", "camarid", "camarids"),
    Noun("CAMEL", "camel", "camels"),
    Noun("CARIBOU", "caribou", "caribou"),
    Noun("CARRIER", "carrier", "carriers"),
    Noun("CAT", "cat", "cats"),
    Noun("CENTAUR", "centaur", "centaurs"),
    Noun("CEPHALID", "cephalid", "cephalids"),
    Noun("CHIMERA", "chimera", "chimeras"),
    Noun("CITIZEN", "citizen", "citizens"),
    Noun("CLERIC", "cleric", "clerics"),
    Noun("COCKATRICE", "cockatrice", "cockatrices"),
    Noun("CONSTRUCT", "construct", "constructs"),
    Noun("COWARD", "coward", "cowards"),
    Noun("CRAB", "crab", "crabs"),
    Noun("CROCODILE", "crocodile", "crocodiles"),
    Noun("CYCLOPS", "cyclops", "cyclops"),
    Noun("DAUTHI", "dauthi", "dauthis"),
    Noun("DEMON", "demon", "demons"),
    Noun("DESERTER", "deserter", "deserters"),
    Noun("DEVIL", "devil", "devils"),
    Noun("DJINN", "djinn", "djinns"),
    Noun("DRAGON", "dragon", "dragons"),
    Noun("DRAKE", "drake", "drakes"),
    Noun("DREADNOUGHT", "dreadnought", "dreadnoughts"),
    Noun("DRONE", "drone", "drones"),
    Noun("DRUID", "druid", "druids"),
    Noun("DRYAD", "dryad", "dryads"),
    Noun("DWARF", "dwarf", "dwarves"),
    Noun("EFREET", "efreet", "efreets"),
    Noun("ELDER", "elder", "elders"),
    Noun("ELDRAZI", "eldrazi", "eldrazis"),
    Noun("ELEMENTAL", "elemental", "elementals"),
    Noun("ELEPHANT", "elephant", "elephants"),
    Noun("ELF", "elf", "elves"),
    Noun("ELK", "elk", "elks"),
    Noun("EYE", "eye", "eyes"),
    Noun("FAERIE", "faerie", "faeries"),
    Noun("FERRET", "ferret", "ferrets"),
    Noun("FISH", "fish", "fish"),
    Noun("FLAGBEARER", "flagbearer", "flagbearers"),
    Noun("FOX", "fox", "foxes"),
    Noun("FROG", "frog", "frogs"),
    Noun("FUNGUS", "fungus", "fungi"),
    Noun("GARGOYLE", "gargoyle", "gargoyles"),
    Noun("GERM", "germ", "germs"),
    Noun("GIANT", "giant", "giants"),
    Noun("GNOME", "gnome", "gnomes"),
    Noun("GOAT", "goat", "goats"),
    Noun("GOBLIN", "goblin", "goblins"),
    Noun("GOD", "god", "gods"),
    Noun("GOLEM", "golem", "golems"),
    Noun("GORGON", "gorgon", "gorgons"),
    Noun("GRAVEBORN", "graveborn", "graveborns"),
    Noun("GREMLIN", "gremlin", "gremlins"),
    Noun("GRIFFIN", "griffin", "griffins"),
    Noun("HAG", "hag", "hags"),
    Noun("HARPY", "harpy", "harpies"),
    Noun("HELLION", "hellion", "hellions"),
    Noun("HIPPO", "hippo", "hippos"),
    Noun("HIPPOGRIFF", "hippogriff", "hippogriffs"),
    Noun("HOMARID", "homarid", "homarids"),
    Noun("HOMUNCULUS", "homunculus", "homunculi"),
    Noun("HORROR", "horror", "horrors"),
    Noun("HORSE", "horse", "horses"),
    Noun("HOUND", "hound", "hounds"),
    Noun("HUMAN", "human", "humans"),
    Noun("HYDRA", "hydra", "hydras"),
    Noun("HYENA", "hyena", "hyenas"),
    Noun("ILLUSION", "illusion", "illusions"),
    Noun("IMP", "imp", "imps"),
    Noun("INCARNATION", "incarnation", "incarnations"),
    Noun("INSECT", "insect", "insects"),
    Noun("JACKAL", "jackal", "jackals"),
    Noun("JELLYFISH", "jellyfish", "jellyfish"),
    Noun("JUGGERNAUT", "juggernaut", "juggernauts"),
    Noun("KAVU", "kavu", "kavus"),
    Noun("KIRIN", "kirin", "kirins"),
    Noun("KITHKIN", "kithkin", "kithkins"),
    Noun("KNIGHT", "knight", "knights"),
    Noun("KOBOLD", "kobold", "kobolds"),
    Noun("KOR", "kor", "kors"),
    Noun("KRAKEN", "kraken", "krakens"),
    Noun("LAMIA", "lamia", "lamias"),
    Noun("LAMMASU", "lammasu", "lammasu"),
    Noun("LEECH", "leech", "leeches"),
    Noun("LEVIATHAN", "leviathan", "leviathans"),
    # See Anthony Alongi, Serious Fun, July 08, 2003, mtgcom/daily/aa79
    Noun("LHURGOYF", "lhurgoyf", "lhurgoyfu"),
    Noun("LICID", "licid", "licids"),
    Noun("LIZARD", "lizard", "lizards"),
    Noun("MANTICORE", "manticore", "manticores"),
    Noun("MASTICORE", "masticore", "masticores"),
    Noun("MERCENARY", "mercenary", "mercenaries"),
    Noun("MERFOLK", "merfolk", "merfolk"),
    Noun("METATHRAN", "metathran", "metathrans"),
    Noun("MINION", "minion", "minions"),
    Noun("MINOTAUR", "minotaur", "minotaurs"),
    Noun("MOLE", "mole", "moles"),
    Noun("MONGER", "monger", "mongers"),
    Noun("MONGOOSE", "mongoose", "mongooses"),
    Noun("MONK", "monk", "monks"),
    Noun("MONKEY", "monkey", "monkeys"),
    Noun("MOONFOLK", "moonfolk", "moonfolk"),
    Noun("MUTANT", "mutant", "mutants"),
    Noun("MYR", "myr", "myrs"),
    Noun("MYSTIC", "mystic", "mystics"),
    Noun("NAGA", "naga", "nagas"),
    Noun("NAUTILUS", "nautilus", "nautiluses"),
    Noun("NEPHILIM", "nephilim", "nephilims"),
    Noun("NIGHTMARE", "nightmare", "nightmares"),
    Noun("NIGHTSTALKER", "nightstalker", "nightstalkers"),
    Noun("NINJA", "ninja", "ninjas"),
    Noun("NOGGLE", "noggle", "noggles"),
    Noun("NOMAD", "nomad", "nomads"),
    Noun("NYMPH", "nymph", "nymphs"),
    Noun("OCTOPUS", "octopus", "octopuses"),
    Noun("OGRE", "ogre", "ogres"),
    Noun("OOZE", "ooze", "oozes"),
    Noun("ORB", "orb", "orbs"),
    Noun("ORC", "orc", "orcs"),
    Noun("ORGG", "orgg", "orggs"),
    Noun("OUPHE", "ouphe", "ouphes"),
    Noun("OX", "ox", "oxen"),
    Noun("OYSTER", "oyster", "oysters"),
    Noun("PEGASUS", "pegasus", "pegasus"),
    Noun("PENTAVITE", "pentavite", "pentavites"),
    Noun("PEST", "pest", "pests"),
    Noun("PHELDDAGRIF", "phelddagrif", "phelddagrifs"),
    Noun("PHOENIX", "phoenix", "phoenix"),
    Noun("PILOT", "pilot", "pilots"),
    Noun("PINCHER", "pincher", "pinchers"),
    Noun("PIRATE", "pirate", "pirates"),
    Noun("PLANT", "plant", "plants"),
    Noun("PRAETOR", "praetor", "praetors"),
    Noun("PRISM", "prism", "prisms"),
    Noun("PROCESSOR", "processor", "processors"),
    Noun("RABBIT", "rabbit", "rabbits"),
    Noun("RAT", "rat", "rats"),
    Noun("REBEL", "rebel", "rebels"),
    Noun("REFLECTION", "reflection", "reflections"),
    Noun("RHINO", "rhino", "rhinos"),
    Noun("RIGGER", "rigger", "riggers"),
    Noun("ROGUE", "rogue", "rogues"),
    Noun("SABLE", "sable", "sables"),
    Noun("SALAMANDER", "salamander", "salamanders"),
    Noun("SAMURAI", "samurai", "samurai"),
    Noun("SAND", "sand", "sand"),
    Noun("SAPROLING", "saproling", "saprolings"),
    Noun("SATYR", "satyr", "satyrs"),
    Noun("SCARECROW", "scarecrow", "scarecrows"),
    Noun("SCION", "scion", "scions"),
    Noun("SCORPION", "scorpion", "scorpions"),
    Noun("SCOUT", "scout", "scouts"),
    Noun("SERF", "serf", "serfs"),
    Noun("SERPENT", "serpent", "serpents"),
    Noun("SERVO", "servo", "servos"),
    Noun("SHADE", "shade", "shades"),
    Noun("SHAMAN", "shaman", "shamans"),
    Noun("SHAPESHIFTER", "shapeshifter", "shapeshifters"),
    Noun("SHEEP", "sheep", "sheep"),
    Noun("SIREN", "siren", "sirens"),
    Noun("SKELETON", "skeleton", "skeletons"),
    Noun("SLITH", "slith", "sliths"),
    Noun("SLIVER", "sliver", "slivers"),
    Noun("SLUG", "slug", "slugs"),
    Noun("SNAKE", "snake", "snakes"),
    Noun("SOLDIER", "soldier", "soldiers"),
    Noun("SOLTARI", "soltari", "soltari"),
    Noun("SPAWN", "spawn", "spawn"),
    Noun("SPECTER", "specter", "specters"),
    Noun("SPELLSHAPER", "spellshaper", "spellshapers"),
    Noun("SPHINX", "sphinx", "sphinx"),
    Noun("SPIDER", "spider", "spiders"),
    Noun("SPIKE", "spike", "spikes"),
    Noun("SPIRIT", "spirit", "spirits"),
    Noun("SPLINTER", "splinter", "splinters"),
    Noun("SPONGE", "sponge", "sponges"),
    Noun("SQUID", "squid", "squids"),
    Noun("SQUIRREL", "squirrel", "squirrels"),
    Noun("STARFISH", "starfish", "starfish"),
    Noun("SURRAKAR", "surrakar", "surrakars"),
    Noun("SURVIVOR", "survivor", "survivors"),
    Noun("TETRAVITE", "tetravite", "tetravites"),
    Noun("THALAKOS", "thalakos", "thalakos"),
    Noun("THOPTER", "thopter", "thopters"),
    Noun("THRULL", "thrull", "thrulls"),
    Noun("TREEFOLK", "treefolk", "treefolk"),
    Noun("TRISKELAVITE", "triskelavite", "triskelavites"),
    Noun("TROLL", "troll", "trolls"),
    Noun("TURTLE", "turtle", "turtles"),
    Noun("UNICORN", "unicorn", "unicorns"),
    Noun("VAMPIRE", "vampire", "vampires"),
    Noun("VEDALKEN", "vedalken", "vedalkens"),
    Noun("VIASHINO", "viashino", "viashinos"),
    Noun("VOLVER", "volver", "volvers"),
    Noun("WALL", "wall", "walls"),
    Noun("WARRIOR", "warrior", "warriors"),
    Noun("WEIRD", "weird", "weirds"),
    Noun("WEREWOLF", "werewolf", "werewolves"),
    Noun("WHALE", "whale", "whales"),
    Noun("WIZARD", "wizard", "wizards"),
    Noun("WOLF", "wolf", "wolves"),
    Noun("WOLVERINE", "wolverine", "wolverines"),
    Noun("WOMBAT", "wombat", "wombats"),
    Noun("WORM", "worm", "worms"),
    Noun("WRAITH", "wraith", "wraiths"),
    Noun("WURM", "wurm", "wurms"),
    Noun("YETI", "yeti", "yeti"),
    Noun("ZOMBIE", "zombie", "zombies"),
    Noun("ZUBERA", "zubera", "zubera"),
]

_plane_types = [
    Keyword(("ALARA", "alara")),
    Keyword(("ARKHOS", "arkhos")),
    Keyword(("AZGOL", "azgol")),
    Keyword(("BELENON", "belenon")),
    Keyword(("BOLASS_MEDITATION_REALM", "bolas's meditation realm")),
    Keyword(("DOMINARIA", "dominaria")),
    Keyword(("EQUILOR", "equilor")),
    Keyword(("ERGAMON", "ergamon")),
    Keyword(("FABACIN", "fabacin")),
    Keyword(("INNISTRAD", "innistrad")),
    Keyword(("IQUATANA", "iquatana")),
    Keyword(("IR", "ir")),
    Keyword(("KALDHEIM", "kaldheim")),
    Keyword(("KAMIGAWA", "kamigawa")),
    Keyword(("KARSUS", "karsus")),
    Keyword(("KEPHALAI", "kephalai")),
    Keyword(("KINSHALA", "kinshala")),
    Keyword(("KOLBAHAN", "kolbahan")),
    Keyword(("KYNETH", "kyneth")),
    Keyword(("LORWYN", "lorwyn")),
    Keyword(("LUVION", "luvion")),
    Keyword(("MERCADIA", "mercadia")),
    Keyword(("MIRRODIN", "mirrodin")),
    Keyword(("MOAG", "moag")),
    Keyword(("MONGSENG", "mongseng")),
    Keyword(("MURAGANDA", "muraganda")),
    # New Phyrexia
    Keyword(("NEW_PHYREXIA", "new phyrexia")),
    Keyword(("PHYREXIA", "phyrexia")),
    Keyword(("PYRULEA", "pyrulea")),
    Keyword(("RABIAH", "rabiah")),
    Keyword(("RATH", "rath")),
    Keyword(("RAVNICA", "ravnica")),
    Keyword(("REGATHA", "regatha")),
    Keyword(("SEGOVIA", "segovia")),
    Keyword(("SERRAS_REALM", "serra's realm")),
    Keyword(("SHADOWMOOR", "shadowmoor")),
    Keyword(("SHANDALAR", "shandalar")),
    Keyword(("ULGROTHA", "ulgrotha")),
    Keyword(("VALLA", "valla")),
    Keyword(("VRYN", "vryn")),
    Keyword(("WILDFIRE", "wildfire")),
    Keyword(("XEREX", "xerex")),
    Keyword(("ZENDIKAR", "zendikar")),
]

counter_types = [
    "age",
    "aim",
    "arrow",
    "arrowhead",
    "awakening",
    "blaze",
    "blood",
    "bounty",
    "bribery",
    "brick",
    "cage",
    "carrion",
    "charge",
    "corpse",
    "credit",
    "crystal",
    "cube",
    "currency",
    "death",
    "delay",
    "depletion",
    "despair",
    "devotion",
    "divinity",
    "doom",
    "dream",
    "echo",
    "elixir",
    "energy",
    "eon",
    "experience",
    "eyeball",
    "fade",
    "fate",
    "feather",
    "filibuster",
    "flood",
    "fungus",
    "fury",
    "fuse",
    "gem",
    "glyph",
    "gold",
    "growth",
    "hatchling",
    "healing",
    "hoofprint",
    "hour",
    "hourglass",
    "hunger",
    "ice",
    "infection",
    "intervention",
    "isolation",
    "javelin",
    "ki",
    "level",
    "lore",
    "loyalty",
    "luck",
    "magnet",
    "manifestation",
    "mannequin",
    "matrix",
    "mine",
    "mining",
    "mire",
    "music",
    "muster",
    "net",
    "omen",
    "ore",
    "page",
    "pain",
    "paralyzation",
    "petal",
    "petrification",
    "phylactery",
    "pin",
    "plague",
    "plot",
    "poison",
    "polyp",
    "pressure",
    "pupa",
    "quest",
    "rust",
    "scream",
    "shell",
    "shield",
    "shred",
    "sleep",
    "sleight",
    "slime",
    "soot",
    "spite",
    "spore",
    "storage",
    "strife",
    "study",
    "theft",
    "tide",
    "time",
    "tower",
    "training",
    "trap",
    "treasure",
    "unity",
    "velocity",
    "verse",
    "vitality",
    "vortex",
    "wage",
    "winch",
    "wind",
    "wish",
]

choices = [
    "carnage",
    "condemnation",
    "death",
    "denial",
    "dragons",
    "duplication",
    "feather",
    "free",
    "grace",
    "harvest",
    "homage",
    "khans",
    "knowledge",
    "money",
    "numbers",
    "peace",
    "psychosis",
    "quill",
    "sickness",
    "sprout",
    "strength",
    "taxes",
    "time",
    "torture",
    "war",
    "wild",
]

_subtypes = (_artifact_types + _creature_types + _enchantment_types
             + _land_types + _plane_types + _planeswalker_types + _spell_types)
subtypes = {}
for st in _subtypes:
    for word, token in st.dict.items():
        subtypes[word] = token

zones = {}
_zones = [
    Keyword(("BATTLEFIELD", "battlefield")),
    Keyword(("COMMAND", "command")),
    Keyword(("EXILE", "exile")),
    Noun("GRAVEYARD", "graveyard", "graveyards"),
    Noun("HAND", "hand", "hands"),
    Noun("LIBRARY", "library", "libraries"),
    Keyword(("STACK", "stack")),

    Noun("DECK", "deck", "decks"),
    Noun("GAME", "game", "games"),
    Noun("SIDEBOARD", "sideboard", "sideboards"),
    Noun("SUBGAME", "subgame", "subgames"),
    Noun("ZONE", "zone", "zones"),
    Keyword(("OUTSIDE", "outside")),
    Keyword(("ANYWHERE", "anywhere")),
]
for z in _zones:
    zones.update(z.dict)

turn_structure = {}
_turn_structure = [
    Noun("TURN", "turn", "turns"),
    Noun("PHASE", "phase", "phases"),
    Noun("STEP", "step", "steps"),

    # Phases
    Keyword(("BEGINNING", "beginning")),
    Keyword(("MAIN", "main")),
    Keyword(("PRECOMBAT", "precombat")),
    Keyword(("POSTCOMBAT", "postcombat")),
    Keyword(("COMBAT", "combat")),
    Keyword(("ENDING", "ending")),

    # Steps
    Keyword(("UNTAP", "untap")),
    Noun("UPKEEP", "upkeep", "upkeeps"),
    Keyword(("DRAW", "draw")),
    Keyword(("BEGINNING", "beginning")), # of combat
    Keyword(("DECLARE", "declare")),
    Keyword(("ATTACKERS", "attackers")),
    Keyword(("BLOCKERS", "blockers")),
    Keyword(("DAMAGE", "damage")), # combat damage
    Keyword(("END", "end")), # of combat; end step
    Keyword(("CLEANUP", "cleanup")),
]
for ts in _turn_structure:
    turn_structure.update(ts.dict)

concepts = {}
_concepts = [
    # Abilities, spells, effects
    Keyword(("ADDITION", "addition")),
    Keyword(("ADDITIONAL", "additional")),
    Keyword(("CONVERTED", "converted")),
    Noun("COST", "cost", "costs"),
    Noun("TARGET", "target", "targets"),

    # mana
    Keyword(("COMBINATION", "combination")),
    Noun("MANA", "mana", "mana"),
    Noun("POOL", "pool", "pools"),
    Noun("SYMBOL", "symbol", "symbols"),
    Keyword(("UNUSED", "unused")),

    # Object or zone parts
    Noun("BOTTOM", "bottom", "bottoms"),
    Noun("TOP", "top", "tops"),
    Keyword(("LIFE", "life")),
    Keyword(("LOYALTY", "loyalty")),
    Keyword(("TOTAL", "total", "totals")),
    Keyword(("POWER", "power")),
    Keyword(("TOUGHNESS", "toughness")),
    Keyword(("TEXT", "text")),
    Keyword(("FULL", "full")),
    Noun("INSTANCE", "instance", "instances"),
    Keyword(("JUST_BENEATH", "just beneath")),

    # numbers
    Noun("NUMBER", "number", "numbers"),

    # Math
    Keyword(("AMOUNT", "amount")),
    Keyword(("MINUS", "minus")),
    Keyword(("PLUS", "plus")),
    Keyword(("TIMES", "times")),
    Keyword(("TWICE", "twice")),
    Keyword(("TOTAL", "total")),
    Keyword(("VALUE", "value")),
    Keyword(("HALF", "half")),
    Keyword(("EVENLY", "evenly")),
    Verb(   ("ROUND", "round", "rounds"),
            ("ROUNDED", "rounded")),
    Keyword(("UP", "up")),
    Keyword(("DOWN", "down")),
    Keyword(("MAXIMUM", "maximum")),
    Keyword(("MINIMUM", "minimum")),
    Keyword(("BASE", "base")),

    # Limits
    Keyword(("ONCE", "once")),
    Keyword(("SINGLE", "single")),

    # Groupings
    Keyword(("EACH", "each")),
    Keyword(("EVERY", "every")),
    Keyword(("EVERYTHING", "everything")),
    Noun("PILE", "pile", "piles"),
    Keyword(("EVEN", "even")),
    Keyword(("ODD", "odd")),
    Keyword(("COMMON", "common")),
    Keyword(("SAME", "same")),
    Keyword(("DIFFERENT", "different")),
    Keyword(("DIFFERENCE", "difference")),
    Keyword(("KIND", "kind", "kinds")),
    Keyword(("ALL", "all")),
    Keyword(("BOTH", "both")),
    Keyword(("ONLY", "only")),
    Keyword(("MANY", "many")),
    Keyword(("ANY", "any")),
    Keyword(("SOME", "some")),
    Keyword(("NONE", "none")),
    Keyword(("NO", "no")),
    Keyword(("OTHER", "other")),
    Keyword(("ANOTHER", "another")),
    Keyword(("REST", "rest")),

    # Directions and seating
    Keyword(("DIRECTION", "direction")),
    Keyword(("LEFT", "left")),
    Keyword(("RIGHT", "right")),
    Keyword(("SEATED", "seated")),
    Keyword(("NEAREST", "nearest")),
    Keyword(("PROCEEDING", "proceeding")),
    Noun("ROUND", "round", "rounds"),

    # comparisons
    Keyword(("MOST", "most")),
    Keyword(("FEWEST", "fewest")),
    Keyword(("GREATEST", "greatest")),
    Keyword(("LEAST", "least")),
    Keyword(("MORE", "more")),
    Keyword(("LESS", "less")),
    Keyword(("HIGH", "high")),
    Keyword(("LOW", "low")),
    Keyword(("HIGHER", "higher")),
    Keyword(("LOWER", "lower")),
    Keyword(("HIGHEST", "highest")),
    Keyword(("LOWEST", "lowest")),
    Keyword(("GREATER", "greater")),
    Keyword(("FEWER", "fewer")),
    Keyword(("LESSER", "lesser")),
    Keyword(("SMALLER", "smaller")),
    Keyword(("LONG", "long")),
    Keyword(("SHORT", "short")),
    Keyword(("LONGER", "longer")),
    Keyword(("SHORTER", "shorter")),
    Keyword(("THAN", "than")),
    Keyword(("DIRECTLY", "directly")),
    Keyword(("ABOVE", "above")),
    Keyword(("BELOW", "below")),
    Keyword(("OVER", "over")),
    Keyword(("UNDER", "under")),
    Keyword(("AMONG", "among")),
    Keyword(("BETWEEN", "between")),
    Keyword(("EQUAL", "equal", "equals")),
    Keyword(("EXACTLY", "exactly")),
    Keyword(("BEYOND", "beyond")),
    Keyword(("MUCH", "much")),

    # Special states and statuses
    Keyword(("ALONE", "alone")),
    Keyword(("CHOSEN", "chosen")),
    Keyword(("DRAWN", "drawn")),
    Keyword(("FACE_UP", "face-up", "face up")),
    Keyword(("FACE_DOWN", "face-down", "face down")),
    Keyword(("LABEL", "label")),
    Keyword(("LEVEL", "level")),
    Keyword(("MARKED", "marked")),
    Keyword(("MONSTROUS", "monstrous")),
    Keyword(("ORIGINAL", "original")),
    Keyword(("PHASED_OUT", "phased-out")),
    Keyword(("POISONED", "poisoned")),
    Keyword(("TARGETED", "targeted")),
    Keyword(("UNBLOCKED", "unblocked")),
    Keyword(("UNCHANGED", "unchanged")),
    Keyword(("UNPAIRED", "unpaired")),

    # Pronouns
    Keyword(("YOU", "you")),
    Keyword(("YOUR", "your", "yours")),
    # Their, or his or her
    Keyword(("THEIR", "their")),
    # Them, or him or her
    Keyword(("THEM", "them")),
    # They, or he or she
    Keyword(("THEY", "they")),
    Keyword(("ITSELF", "itself")),
    # Planeswalkers use these
    Keyword(("HE", "he")),
    Keyword(("HIM", "him")),
    Keyword(("HIMSELF", "himself")),
    Keyword(("HIS", "his")),
    Keyword(("SHE", "she")),
    Keyword(("HER", "her")),
    Keyword(("HERSELF", "herself")),

    # Hand size
    Keyword(("SIZE", "size")),

    # Damage
    Keyword(("DAMAGE", "damage")),
    Keyword(("LETHAL", "lethal")),
    Keyword(("POINT", "point")),
    Keyword(("POISON", "poison")),

    # Randomization and guessing
    Noun("COIN", "coin", "coins"),
    Keyword(("HEADS", "heads")),
    Keyword(("TAILS", "tails")),
    Keyword(("RANDOM", "random")),
    Keyword(("WRONG", "wrong")),
    # The planar die
    Keyword(("PLANAR_DIE", "planar die")),

    # Special bidding or voting
    Keyword(("BROKEN", "broken")),
    Noun("ITEM", "item", "items"),
    Keyword(("SECRETLY", "secretly")),
    Keyword(("STAKES", "stakes")),
    Noun("VOTER", "voter", "voters"),

    # Guessing
    Keyword(("CORRECTLY", "correctly")),

    # Rules
    Keyword(("LEGAL", "legal")),
    Keyword(("LEGEND_RULE", "legend rule")),

    # Before the game
    Keyword(("MULLIGAN", "mulligan")),
    Keyword(("OPENING", "opening")),

    # Drafting
    Noun("BOOSTER_PACK", "booster pack", "booster packs"),
    Keyword(("UNOPENED", "unopened")),

    # Subgames
    Keyword(("MAGIC", "magic")),

    # Color identity (Commander)
    Keyword(("IDENTITY", "identity")),

    # Number of mana symbols of a particular color.
    Keyword(("DEVOTION", "devotion")),

    # Timing
    Keyword(("AFTER", "after")),
    Keyword(("AGAIN", "again")),
    Keyword(("BEFORE", "before")),
    Keyword(("CONTINUOUSLY", "continuously")),
    Keyword(("DURING", "during")),
    Keyword(("IMMEDIATELY", "immediately")),
    Keyword(("NEXT", "next")),
    Keyword(("PREVIOUSLY", "previously")),
    Keyword(("RECENT", "recent")),
    Keyword(("RECENTLY", "recently")),
    Keyword(("SIMULTANEOUSLY", "simultaneously")),
    Keyword(("SINCE", "since")),
    Keyword(("TIME", "time")),
    Keyword(("UNTIL", "until")),
    Keyword(("WHEN", "when", "whenever")),
    Keyword(("WHILE", "while")),

    # Conditions and references
    Keyword(("ALREADY", "already")),
    Keyword(("BACK", "back")),
    Keyword(("BY", "by")),
    Keyword(("ELSE", "else")),
    Keyword(("EXCEPT", "except")),
    Keyword(("FAR", "far")),
    Keyword(("FOLLOWED", "followed")),
    Keyword(("FOLLOWING", "following")),
    Keyword(("FROM", "from")),
    Keyword(("IF", "if")),
    Keyword(("IN", "in")),
    Keyword(("INCLUDING", "including")),
    Keyword(("INSTEAD", "instead")),
    Keyword(("INTO", "into")),
    Keyword(("IT", "it")),
    Keyword(("ITS", "its")),
    Keyword(("LIKEWISE", "likewise")),
    Keyword(("ON", "on")),
    Keyword(("ONTO", "onto")),
    Keyword(("OTHERWISE", "otherwise")),
    Keyword(("OUT", "out")),
    Keyword(("PROCESS", "process")),
    Keyword(("RATHER", "rather")),
    Keyword(("STILL", "still")),
    Keyword(("THAT", "that")),
    Keyword(("THERE", "there")),
    Keyword(("THIS", "this")),
    Keyword(("THOSE", "those")),
    Keyword(("THOUGH", "though")),
    Keyword(("TO", "to")),
    Keyword(("UNLESS", "unless")),
    Keyword(("WAY", "way")),
    Keyword(("WHERE", "where")),
    Keyword(("WHETHER", "whether")),
    Keyword(("WHICH", "which", "whichever")),
    Keyword(("WHO", "who")),
    Keyword(("WHOM", "whom")),
    Keyword(("WHOSE", "whose")),
    Keyword(("WOULD", "would")),

    # Expansions
    Keyword(("EXPANSION", "expansion")),
    Keyword(("ARABIAN_NIGHTS", "arabian nights")),
    Keyword(("ANTIQUITIES", "antiquities")),
    Keyword(("HOMELANDS", "homelands")),
    Keyword(("ORIGINALLY", "originally")),
    Keyword(("PRINTED", "printed")),
]
for c in _concepts:
    concepts.update(c.dict)

misc_words = {}
_misc = [
    Keyword(("A", "a", "an")),
    Keyword(("ALSO", "also")),
    Keyword(("AND", "and")),
    Keyword(("AND_OR", "and/or")),
    Keyword(("AS", "as")),
    Keyword(("AT", "at")),
    Keyword(("BUT", "but")),
    Keyword(("EITHER", "either")),
    Keyword(("EXCESS", "excess")),
    Keyword(("EXTRA", "extra")),
    Keyword(("FOR", "for")),
    Keyword(("HOW", "how")),
    Keyword(("MAKE", "make")),
    Noun("MODE", "mode", "modes"),
    Keyword(("MUST", "must")),
    Keyword(("NEITHER", "neither")),
    Keyword(("NEW", "new")),
    Keyword(("NON", "non", "non-")),
    Keyword(("NOR", "nor")),
    Keyword(("NOT", "not", "n't", "'t")),
    Keyword(("OF", "of")),
    Keyword(("OR", "or")),
    Keyword(("PART", "part")),
    Keyword(("SO", "so")),
    Keyword(("THE", "the")),
    Keyword(("THEN", "then")),
    Keyword(("TRUE", "true")),
    Keyword(("WITH", "with")),
    Keyword(("WITHOUT", "without")),
    Noun("WORD", "word", "words"),
]
for m in _misc:
    misc_words.update(m.dict)

number_words = {
    "zero" : 0,
    "one" : 1,
    "two" : 2,
    "three" : 3,
    "four" : 4,
    "five" : 5,
    "six" : 6,
    "seven" : 7,
    "eight" : 8,
    "nine" : 9,
    "ten" : 10,
    "eleven" : 11,
    "twelve" : 12,
    "thirteen" : 13,
    "fourteen" : 14,
    "fifteen" : 15,
    "sixteen" : 16,
    "seventeen" : 17,
    "eighteen" : 18,
    "nineteen" : 19,
    "twenty" : 20,
    "ninety-nine": 99,
}

ordinals = {
    "first" : 1,
    "second" : 2,
    "third" : 3,
    "fourth" : 4,
    "seventh": 7,
    "last" : -1,
}

all_words = {}
for d in (actions, abilities, types, zones,
          turn_structure, concepts, misc_words):
    all_words.update(d)

_macroables = {
    'ABILITY_WORD'  : set(ability_words),
    'ARB_CHOICE'    : set(choices),
    'NUMBER_WORD'   : set(number_words),
    'OBJ_COUNTER'   : set(counter_types),
    'OBJ_SUBTYPE'   : set(subtypes),
    'ORDINAL_WORD'  : set(ordinals),
}
macro_words = set()
for mwords in _macroables.values():
    macro_words.update(mwords)

def make_token_name(s):
    return s.replace("'", '').replace(' ', '_').upper()

def _check_collision(w):
    """ If w is in all_words or macro_words, return a token for it
        and put it in all_words if it's not there already. """
    if w in all_words:
        return all_words[w]
    elif w in macro_words:
        all_words[w] = make_token_name(w)
        return all_words[w]

def _get_collision(s, force_token=False):
    """ Check whether s collides with an existing token followed by one of
        the three POSS tokens (APOS_S, S_APOS, or SQUOTE),
        or simply an existing token. If so, return a list of that token
        (and the POSS token if applicable). If not, and force_token is True,
        create a token and return that. """
    t = None
    if s[-2:] == "'s":
        t = _check_collision(s[:-2])
        if t:
            return [t, 'APOS_S']
    elif s[-2:] == "s'":
        t = _check_collision(s[:-2])
        if t:
            return [t, 'S_APOS']
        t = _check_collision(s[:-1])
        if t:
            return [t, 'SQUOTE']
    t = _check_collision(s)
    if t:
        return [t]
    elif force_token:
        all_words[s] = make_token_name(s)
        return [all_words[s]]

collisions = set()
partial_collisions = {}

def get_partial_collisions(s):
    """ If s is multi-word and the first word collides with another token,
        returns a list of tokens to be used as a macro rule to match s. """
    if ' ' in s:
        words = s.split(' ')
        pt = _get_collision(words[0])
        if pt:
            for w in words[1:]:
                # Make all remaining words tokens at the all_words level.
                wt = _get_collision(w, force_token=True)
                pt.extend(wt)
            return pt

# Find partial collisions within nonmacroable tokens.
# A partial collision would be eg. "first strike" and "first".
# Wrap with list() as get_partial_collisions modifies all_words.
for s, t in list(all_words.items()):
    pt = get_partial_collisions(s)
    if pt:
        if t not in partial_collisions:
            partial_collisions[t] = {s: pt}
        else:
            partial_collisions[t][s] = pt

for t, mwords in _macroables.items():
    partial_collisions[t] = {}
    for s in mwords:
        pt = get_partial_collisions(s)
        if pt:
            partial_collisions[t][s] = pt

_msets = [set(all_words)] + list(_macroables.values())
for i, m in enumerate(_msets):
    for n in _msets[i+1:]:
        collisions |= (m & n)

_token_lookup = {}
for w, t in all_words.items():
    if t not in _token_lookup:
        _token_lookup[t] = {w}
    else:
        _token_lookup[t].add(w)

# All colliding rules must have their own tokens
for c in collisions:
    if c not in all_words:
        all_words[c] = make_token_name(c)
        continue

    # Further, don't split apart a token with multiple matches.
    # This means we might match "fuses counters" but at least we won't
    # break "numbers" matching for NUMBER.
    t = all_words[c]
    matches = _token_lookup[t]
    if len(matches) > 1:
        all_words[c] = t
    else:
        all_words[c] = make_token_name(c)

macro_rules = {}
replaced = {}

for t, spt in partial_collisions.items():
    opt = []
    for s, pt in sorted(spt.items()):
        ft = make_token_name(s)
        replaced[s] = ft
        opt.append('{} -> {}'.format(' '.join(pt), ft))
        if s in all_words:
            del all_words[s]
    tr = t.lower()
    if tr in macro_rules:
        macro_rules[tr].extend(opt)
    else:
        macro_rules[tr] = opt

for a, b in _macroables.items():
    # Everything in b that collided (but not partially) goes in the macro rule
    col_tokens = [all_words[j] for j in ((b & collisions) - set(replaced))]
    at = a.lower()
    if at in macro_rules:
        macro_rules[at] = [a] + sorted(col_tokens) + macro_rules[at]
    else:
        macro_rules[at] = [a] + sorted(col_tokens)

# everything in b that didn't collide (at all) goes in the macro token def
macro_tokens = {a: b - collisions - set(replaced)
                for a, b in _macroables.items()}

def _get_filename(grammar):
    import os
    return os.path.join(os.path.dirname(__file__), 'grammar',
                        '{}.g'.format(grammar))

_LICENSE = """
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
"""

def _get_header(grammar, gtype, desc):
    header = [
        '{gtype} grammar {grammar};',
        _LICENSE,
        '/* {desc}',
        ' *',
        ' * Autogenerated by demystify/keywords.py',
        ' * DO NOT EDIT DIRECTLY',
        ' */\n',
    ]
    return '\n'.join(header).format(grammar=grammar, gtype=gtype, desc=desc)

def _format_rule(name, options):
    """ Returns an antlr rule as a pretty-printed string. """
    sep = '\n  {bar:>{width}} '.format(bar='|', width=len(name))
    return '{} : {};\n'.format(name, sep.join(options))

def write_parser():
    grammar = 'macro'
    desc = 'Pseudotoken rules that simply match one of many tokens.'
    filename = _get_filename(grammar)
    with open(filename, 'w') as f:
        f.write(_get_header(grammar, 'parser', desc))
        for rule, options in sorted(macro_rules.items()):
            f.write('\n')
            # options pre-sorted appropriately
            f.write(_format_rule(rule, options))
    print('Generated {} macro rules, including {} token collisions.'
          .format(len(macro_rules), len(collisions) + len(replaced)))

def write_lexer():
    grammar = 'Words'
    desc = 'Keywords and misc text.'
    filename = _get_filename(grammar)
    all_tokens = (set(all_words.values()) | set(macro_tokens)
                  | set(replaced.values()))
    # token -> (text, substitute token) list
    match_cases = {}
    for text, token in all_words.items():
        if token not in match_cases:
            match_cases[token] = [text]
        else:
            match_cases[token].append(text)
    for token, words in macro_tokens.items():
        match_cases[token] = words
    def reprsinglequote(s):
        if not s:
            return ''
        a = repr(s)
        if a[0] == '"':
            a = "'" + a[1:-1].replace("'", r"\'") + "'"
        return a
    with open(filename, 'w') as f:
        f.write(_get_header(grammar, 'lexer', desc))
        f.write('\nimport Symbols;\n\n')
        f.write('tokens {{\n    {tokens};\n}}\n\n'
                .format(tokens=';\n    '.join(sorted(all_tokens))))
        for token, tlist in sorted(match_cases.items(),
                                   key=lambda x: (-len(x[0]), x[0])):
            lines = []
            for text in sorted(tlist, key=lambda x: (-len(x), x)):
                lines.append(reprsinglequote(text))
            f.write(_format_rule(token, lines))
    print('Generated {} lexer rules for {} tokens.'
          .format(len(match_cases), len(all_tokens)))

if __name__ == "__main__":
    write_lexer()
    write_parser()
