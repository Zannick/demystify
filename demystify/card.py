# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger("card")
logger.setLevel(logging.INFO)
import re
import string

import progressbar

abil = re.compile(r'"[^"]+"')
splitname = re.compile(r'([^/]+) // ([^()]+) \((\1|\2)\)')
flipname = re.compile(r'([^()]+) \(([^()]+)\)')
nonwords = re.compile(r'\W', flags=re.UNICODE)

all_names = {}
all_names_inv = {}
_all_cards = {}
expect_multi = {}

# Handle any Legendary names we couldn't get with ", " or " the ", most of
# which have two words only, eg. Arcades Sabboth, or "of the".
# We wouldn't be able to guess these without also grabbing things like
# "Lady Caleria", "Sliver Overlord", "Phyrexian Tower", "Reaper King",
# "Patron of the Orochi", "Kodama of the North Tree", "Shield of Kaldra", etc.
# This list is absolutely overkill, since we know in advance whether a card
# needs its shortname, and many of these do not.
shortname_exceptions = {
    "Adun Oakenshield"                : "Adun",
    "Angus Mackenzie"                 : "Angus",
    "Arcades Sabboth"                 : "Arcades",
    "Arcum Dagsson"                   : "Arcum",
    "Axelrod Gunnarson"               : "Axelrod",
    "Ayesha Tanaka"                   : "Ayesha",
    "Barktooth Warbeard"              : "Barktooth",
    "Bartel Runeaxe"                  : "Bartel",
    "Boris Devilboon"                 : "Boris",
    "Brion Stoutarm"                  : "Brion",
    "Dakkon Blackblade"               : "Dakkon",
    "Gabriel Angelfire"               : "Gabriel",
    "Gaddock Teeg"                    : "Gaddock",
    "Gerrard Capashen"                : "Gerrard",
    "Glissa Sunseeker"                : "Glissa",
    "Gosta Dirk"                      : "Gosta",
    "Gwendlyn Di Corci"               : "Gwendlyn",
    "Hazezon Tamar"                   : "Hazezon",
    "Hivis of the Scale"              : "Hivis",
    "Hunding Gjornersen"              : "Hunding",
    "Irini Sengir"                    : "Irini",
    "Iwamori of the Open Fist"        : "Iwamori",
    "Jacques le Vert"                 : "Jacques",
    "Jasmine Boreal"                  : "Jasmine",
    "Jedit Ojanen"                    : "Jedit",
    "Jedit Ojanen of Efrava"          : "Jedit",
    "Jerrard of the Closed Fist"      : "Jerrard",
    "Jhoira of the Ghitu"             : "Jhoira",
    "Kei Takahashi"                   : "Kei",
    "The Lady of the Mountain"        : "The Lady",
    "Livonya Silone"                  : "Livonya",
    "Lovisa Coldeyes"                 : "Lovisa",
    "Maralen of the Mornsong"         : "Maralen",
    "Marhault Elsdragon"              : "Marhault",
    "Merieke Ri Berit"                : "Merieke",
    "Márton Stromgald"                : "Márton",
    "Nath of the Gilt-Leaf"           : "Nath",
    "Nicol Bolas"                     : "Nicol",
    "Pavel Maliki"                    : "Pavel",
    "Purraj of Urborg"                : "Purraj",
    "Rafiq of the Many"               : "Rafiq",
    "Rakka Mar"                       : "Rakka",
    "Raksha Golden Cub"               : "Raksha",
    "Ramirez DePietro"                : "Ramirez",
    "Ramses Overdark"                 : "Ramses",
    "Rashida Scalebane"               : "Rashida",
    "Rasputin Dreamweaver"            : "Rasputin",
    "Reya Dawnbringer"                : "Reya",
    "Riven Turnbull"                  : "Riven",
    "Rohgahh of Kher Keep"            : "Rohgahh",
    "Rorix Bladewing"                 : "Rorix",
    "Rosheen Meanderer"               : "Rosheen",
    "Rubinia Soulsinger"              : "Rubinia",
    "Saffi Eriksdotter"               : "Saffi",
    "Sidar Jabari"                    : "Sidar",
    "Sir Shandlar of Eberyn"          : "Sir Shandlar",
    "Sivitri Scarzam"                 : "Sivitri",
    "Starke of Rath"                  : "Starke",
    "Sunastian Falconer"              : "Sunastian",
    "The Tabernacle at Pendrell Vale" : "The Tabernacle",
    "Tarox Bladewing"                 : "Tarox",
    "Tetsuo Umezawa"                  : "Tetsuo",
    "Thelon of Havenwood"             : "Thelon",
    "Tivadar of Thorn"                : "Tivadar",
    "Tobias Andrion"                  : "Tobias",
    "Tolsimir Wolfblood"              : "Tolsimir",
    "Tor Wauki"                       : "Tor",
    "Torsten Von Ursus"               : "Torsten",
    "Toshiro Umezawa"                 : "Toshiro",
    "Tsabo Tavoc"                     : "Tsabo",
    "Tuknir Deathlock"                : "Tuknir",
    "Vaevictis Asmadi"                : "Vaevictis",
    "Veldrane of Sengir"              : "Veldrane",
    "Vhati il-Dal"                    : "Vhati",
    "Xira Arien"                      : "Xira",
    "Zirilan of the Claw"             : "Zirilan",
}

def construct_uname(name):
    """ Return name with 'NAME_' appended to the front, and every non-word
        character (as in \W) replaced with an underscore. This is intended
        to be a unique mapping of the card name to one which contains only
        alphanumerics and underscores. """
    return nonwords.sub(r'_', "NAME_" + name)

def make_shortname(name):
    if ', ' in name:
        return name[:name.index(', ')].strip()
    elif ' the ' in name:
        words = name[:name.index(' the ')].split()
        # if it's 'of' or 'from', for example, ignore
        if not words[-1].islower():
            return name[:name.index(' the ')].strip()
    return shortname_exceptions.get(name)

class Card:
    """ Stores information about a Magic card, as given by Gatherer. """
    def __init__(self, name, cost, typeline,
                 pt=None, rules=None, set_rarity=None):
        self.name = name
        self.cost = cost
        self.typeline = typeline
        self.pt = pt
        self.rules = rules
        self.set_rarity = set_rarity
        # Check for split and flip cards
        self.multicard = self.multitype = None
        m = splitname.match(name)
        if m:
            first, second, self.name = m.groups()
            self.multicard = (self.name == first) and second or first
            self.multitype = "split"
        else:
            n = flipname.match(name)
            if n:
                self.multicard, self.name = n.groups()
                self.multitype = "flip"
            elif "----" in rules:
                flines = rules[rules.index("----") + 4:].strip().split("\n")
                if len(flines) < 3:
                    logger.error("Expected flip card for {} but only {} lines"
                                 " found.".format(name, len(flines)))
                else:
                    self.rules = rules[:rules.index("----")].strip()
                    fname = flines.pop(0)
                    ftype = flines.pop(0)
                    fpt = flines.pop(0)
                    # This adds the card to the _all_cards dict
                    fcard = Card(fname, '', ftype, fpt,
                                 '\n'.join(flines), set_rarity)
                    self.multicard = fname
                    fcard.multicard = name
                    self.multitype = fcard.multitype = "flip"
        # The other card should have multicard and multitype set
        if self.multicard:
            if self.multicard in _all_cards:
                _all_cards[self.multicard].multicard = self.name
                _all_cards[self.multicard].multitype = self.multitype
            else:
                # We'll note that we have to set the multi values later
                expect_multi[self.multicard] = self.name
        elif self.name in expect_multi:
            self.multicard = expect_multi[self.name]
            self.multitype = _all_cards[self.multicard].multitype
            del expect_multi[self.name]
        
        self.shortname = None
        if 'Legendary' in typeline:
            self.shortname = make_shortname(self.name)
            if self.shortname:
                logger.debug("Shortname for {} set to {}."
                             .format(self.name, self.shortname))

        uname = construct_uname(self.name)
        all_names[self.name] = uname
        all_names_inv[uname] = self.name
        _all_cards[self.name] = self

    @staticmethod
    def from_string(s):
        t = s.split('\n')
        name = cost = typeline = pt = rules = set_rarity = ""
        # Gatherer is pretty inconsistent, especially wrt split and flip cards
        for l in t:
            if l.startswith("Name:"):
                name = l[5:].strip()
                if name in _all_cards:
                    logger.debug("Previously saw {}.".format(name))
                    return _all_cards[name]
            elif l.startswith("Cost:"):
                cost = l[5:].strip()
            elif l.startswith("Type:"):
                typeline = l[5:].strip()
            elif l.startswith("Pow/Tgh:"):
                pt = l[8:].strip()
            elif l.startswith("Loyalty:"):
                pt = l[8:].strip()
            elif l.startswith("Rules Text:"):
                rules = l[11:].strip()
            elif l.startswith("Set/Rarity:"):
                set_rarity = l[11:].strip()
            else:
                if l.strip():
                    rules += '\n' + l.strip()
        assert name is not None
        logger.debug("Loaded {}.".format(name))
        return Card(name, cost, typeline, pt, rules, set_rarity)

    def __eq__(self, c):
        return type(self) == type(c) and self.name == c.name

    def __ne__(self, c):
        return type(self) != type(c) or self.name != c.name

    def __hash__(self):
        return self.name.__hash__()

def CardProgressBar(cards):
    """ A generator that writes a progress bar to stdout as its elements
        are accessed. """
    current_card = ' '
    class CardWidget(progressbar.ProgressBarWidget):
        def update(self, pbar):
            if len(current_card) < 16:
                return current_card + (16 - len(current_card)) * ' '
            else:
                return current_card[:16]
    widgets = [CardWidget(), ' ', progressbar.Bar(left='[', right=']'), ' ',
               progressbar.SimpleProgress(sep='/'), ' ', progressbar.ETA()]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(cards))
    pbar.start()
    for i, card in enumerate(cards):
        current_card = card.name
        pbar.update(i)
        yield card
    pbar.finish()

def potential_names(words, cardnames):
    """ cardnames is a list of potential names, either SELF or PARENT,
        that should not be replaced with NAME_ tokens. """
    name = words[0]
    name2 = ''
    namelist = False
    if name[-1] in ':."':
        yield (name[:-1],)
    else:
        for i, w in enumerate(words[1:]):
            if w[0].isupper():
                name += name2 + ' ' + w
                name2 = ''
                if name[-1] in ':."':
                    break
            elif w in ['of', 'from', 'to', 'in', 'on', 'the', 'a']:
                name2 += ' ' + w
            elif w in ['and', 'or']:
                namelist = True
                name2 += ' ' + w
            else:
                break
        name = name.rstrip(',.:"')
        yield (name, )
        if namelist:
            for sep in [' and ', ' or ']:
                names = name.split(sep)
                if len(names) > 1:
                    # pick each separator, join the rest,
                    # split those left of it on commas
                    # and iterate through joining them
                    # (but only from the left)
                    # eg. Example, This and That, Silly, and Serious or Not
                    # when "Example, This and That", "Silly", and
                    #      "Serious or Not" are the card names
                    for i in range(len(names) - 1, 0, -1):
                        left = sep.join(names[:i])
                        right = sep.join(names[i:])
                        lnames = left.split(', ')
                        if lnames[-1][-1] == ',':
                            lnames[-1] = lnames[-1][:-1]
                            # we saw ", and " for a 2-card list?
                            # the latter is probably SELF or PARENT
                            if len(lnames) == 1 and right in cardnames:
                                yield (lnames[0], )
                        if len(lnames) > 1:
                            yield tuple(lnames) + (right, )
                            if len(lnames) > 2:
                                for j in range(len(lnames) - 2, 1, -1):
                                    yield ((', '.join(lnames[:j]), )
                                           + tuple(lnames[j:])
                                           + (right, ))
                                # don't include right in this last case
                                # if it's SELF or PARENT
                                t = ((', '.join(lnames[:-1]), )
                                     + tuple(lnames[-1:]))
                                if right not in cardnames:
                                    t += (right, )
                                yield t
                        else:
                            yield (left, right)
        else:
            names = name.split(', ')
            while len(names) > 1:
                del names[-1]
                yield (', '.join(names), )

def format_by_name(names, words):
    for name in names:
        if name not in all_names:
            logger.info("Found token name: {}".format(name))
            uname = construct_uname(name)
            all_names[name] = uname
            all_names_inv[uname] = name
    if len(names) == 1:
        # number of words == number of spaces + 1
        ll = len([a for a in names[0] if a == ' ']) + 1
        namelist = all_names[names[0]]
    else:
        logger.info("Multiple names being replaced: {}."
                    .format("; ".join(names)))
        s = [all_names[name] for name in names]
        ll = sum([len([a for a in name if a == ' ']) + 1
                  for name in names[:-1]])
        c = words[ll]
        # + 2 because we have to count the connector word 'and' or 'or'
        ll += len([a for a in names[-1] if a == ' ']) + 2
        namelist = ', '.join(s[:-1]) + ', ' + c + ' ' + s[-1]
    if words[ll - 1][-1] in ',.:"':
        if words[ll - 1][-2] in ',.:':
            namelist += words[ll - 1][-2:]
        else:
            namelist += words[ll - 1][-1]
    namelist += ' ' + ' '.join(words[ll:])
    return namelist

# For testing PARENT detection.
_parentcards = set()

def preprocess_cardname(line, selfnames=(), parentnames=()):
    """ Checks only for matches against a card's name. """
    change = False
    for cardname in selfnames:
        if cardname in line:
            line, count = re.subn(r"\b{}(?!\w)".format(cardname),
                                  "SELF", line, flags=re.UNICODE)
            if count > 0:
                change = True
                if parentnames:
                    logger.info("Detected SELF in an ability granted by {}."
                                .format(parentnames[0]))
    for cardname in parentnames:
        if cardname in line:
            line, count = re.subn(r"\b{}(?!\w)".format(cardname),
                                  "PARENT", line, flags=re.UNICODE)
            if count > 0:
                change = True
                logger.info("Detected PARENT in an ability granted by {}."
                            .format(cardname))
                _parentcards.add(cardname)
    return line, change

def preprocess_names(line, selfnames=(), parentnames=()):
    """ This requires that each card was instantiated as a Card and their names
        added to the all_names dicts as appropriate. """
    i = line.find("named ")
    change = False
    while i > -1:
        words = line[i + 6:].split()
        if not words[0][0].islower():
            good = []
            bad = []
            for names in potential_names(words, selfnames + parentnames):
                if all((name in all_names for name in names)):
                    good += [names]
                else:
                    bad += [names]
            if len(good) > 1:
                logger.warning("Multiple name splits possible: {}."
                               .format("; ".join(map(str, good))))
            res = good and good[0] or bad and bad[-1] or None
            if res:
                logger.debug("Selected name(s) at position {} "
                              "as: {}".format(i + 6, "; ".join(res)))
                line = (line[:i + 6] + format_by_name(res, words))
                if len(res) == 1 and '"' not in line[:i] and not parentnames:
                    # Check for abilities granted
                    t = abil.search(line[i + 6:])
                    if t:
                        m, n = t.regs[0]
                        # Created tokens don't get shortnames
                        line = (line[:m + i + 6]
                                + preprocess_names(t.group(), (res[0],),
                                                   selfnames)
                                + line[n + i + 6:])
                        i += n
                change = True
            else:
                logger.warning("Unable to interpret name(s) "
                               "at position {}: {}."
                               .format(i + 6, words[0]))
        i = line.find("named ", i + 6)
    # Check for abilities granted to things that aren't named tokens
    if not parentnames:
        i = 0
        t = abil.search(line[i:])
        while t:
            m, n = t.regs[0]
            line = (line[:m + i]
                    + preprocess_cardname(t.group(), (),
                                          selfnames)[0]
                    + line[n + i:])
            i += n
            t = abil.search(line[i:])
    # CARDNAME processing occurs after the "named" processing
    line, cardname_change = preprocess_cardname(line, selfnames, parentnames)
    if change or cardname_change:
        sname = selfnames and selfnames[0] or "?.token"
        logger.debug("Now: {} | {}".format(sname, line))
    return line

# Basically, LPAREN then anything until RPAREN, but there may
# be nested parentheses inside braces for hybrid mana symbols
# (this occurs in reminder text about hybrid mana symbols).
# Also watch out for the parentheses inside hybrid mana symbols themselves.
_reminder_text = re.compile(r".?\([^{()]*(\{[^}]*\}[^{()]*)*\).?")

def _reminder_chop(m):
    s = m.group(0)
    if s[0] == '{':
        return s
    elif s[0] == ' ' and s[-1] != ')':
        return s[-1]
    return ''

def preprocess_reminder(text):
    """ Chop out reminder text during the preprocessing step.
    
        While this isn't strictly necessary because we can ignore reminder
        text via an ignore token, it is useful to do during preprocessing
        so that searching cards for text won't match reminder text. """
    return _reminder_text.sub(_reminder_chop, text).strip()

def preprocess_capitals(text):
    """ Lowercase every word (but not SELF, PARENT, or NAME_). """
    ws = text.split(' ')
    caps = set(string.uppercase)
    lows = set(string.lowercase)
    vs = []
    for w in ws:
        if 'SELF' in w or 'PARENT' in w or 'NAME_' in w:
            vs.append(w)
        else:
            vs.append(w.lower())
    return ' '.join(vs)

## Main entry point for the preprocessing step ##

def preprocess_all(cards):
    """ Scans the rules texts of every card to replace any card names that
        appear with appropriate symbols, and eliminates reminder text. """
    print("Processing cards for card names...")
    for c in CardProgressBar(cards):
        names = (c.name,)
        if c.shortname:
            names += (c.shortname,)
        lines = [preprocess_capitals(
                    preprocess_reminder(preprocess_names(line, names)))
                 for line in c.rules.split("\n")]
        c.rules = "\n".join(lines)

def get_cards():
    """ Returns a set of all the Cards instantiated with the Card class. """
    return set(_all_cards.values())

def get_card(cardname):
    """ Returns a specific card by name, or None if no such card exists. """
    return _all_cards.get(cardname)

def get_name_from_uname(uname):
    """ Returns the English card for an object, given its unique name. """
    return all_names_inv[uname]

## Utility functions to search card text, get simple text stats ##

def search_text(text, cards=None, reflags=re.I|re.U):
    """ Returns a list of (card name, line of text), containing
        every line in the text of a card that contains a match for the
        given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(text, reflags)
    return [(c.name, line) for c in cards for line in c.rules.split('\n')
            if r.search(line)]

def preceding_words(text, cards=None, reflags=re.I|re.U):
    """ Returns a set of words which appear anywhere in a card's rules text
        before the given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(r"([\w'-]+) {}".format(text), reflags)
    a = set()
    for c in cards:
        a.update(r.findall(c.rules))
    return a

def following_words(text, cards=None, reflags=re.I|re.U):
    """ Returns a set of words which appear anywhere in a card's rules text
        after the given text.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(r"{} ([\w'-]+)".format(text), reflags)
    a = set()
    for c in cards:
        a.update(r.findall(c.rules))
    return a
