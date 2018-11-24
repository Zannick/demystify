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

"""card -- Magic card utilities for Demystify."""

import logging
logger = logging.getLogger("card")
logger.setLevel(logging.INFO)

import copy
import queue
import multiprocessing
import multiprocessing.queues
import re
import string
import sys

import progressbar.bar
import progressbar.widgets

abil = re.compile(r'"[^"]+"')
splitname = re.compile(r'([^/]+) // ([^()]+) \((\1|\2)\)')
flipname = re.compile(r'([^()]+) \(([^()]+)\)')
nonwords = re.compile(r'\W', flags=re.UNICODE)
name_ref = re.compile(r'named |name is still |transforms into |meld them into '
                      r'|Partner with |[Cc]reate ')
gains = re.compile(r'(SELF|it|\w+) (enters?|gets?|gains?|has|have|loses?|with)'
                   r'([^.]+, and )?'
                   r'(gets?|gains?|has|have|loses?|with) "')
# common, uncommon, rare, mythic, land, special, bonus
rarities = {'C', 'U', 'R', 'M', 'L', 'S', 'B'}

all_names = {}
all_names_inv = {}
all_shortnames = {}
cards_by_set = {}
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
    "Darigaaz Reincarnated"           : "Darigaaz",
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
    return nonwords.sub(r'_', str("NAME_" + name))

def make_shortname(name):
    if ', ' in name:
        return name[:name.index(', ')].strip()
    elif ' the ' in name:
        words = name[:name.index(' the ')].split()
        # if it's 'of' or 'from', for example, ignore
        if not words[-1].islower():
            return name[:name.index(' the ')].strip()
    return shortname_exceptions.get(name)

class Card(object):
    """ Stores information about a Magic card, as given by Gatherer. """
    def __init__(self, name='', type_line='', mana_cost=None, colors=(),
                 loyalty=None, power=None, toughness=None, oracle_text=None,
                 set_rarity=None, multitype=None, multicard=None,
                 meld_pair=None, melded=None,
                 # catch-all
                 **kwargs):
        self.name = str(name)
        self.typeline = str(type_line.lower().replace("’", "'"))
        self.cost = mana_cost
        self.color = ''.join(colors)
        # TODO: just keep these fields separate?
        self.pt = loyalty or power and (power + '/' + toughness)
        self.rules = str(oracle_text.replace("’", "'"))
        self.sets = set()
        if set_rarity:
            for s_r in set_rarity.split(', '):
                s, r = s_r.split('-', 1)
                self.sets.add(s)
                if r not in rarities:
                    logger.error("Unknown set_rarity entry for {}: {}"
                                 .format(name, s_r))
        self.sets = sorted(self.sets)
        # TODO: Do we really need all this logic instead of simply
        # incorporating the scryfall json references?
        self.multitype = multitype
        self.multicard = multicard
        self.meld_pair = meld_pair
        self.melded = melded
        if self.multitype != 'meld':
            if self.melded:
                logger.error('Malformed multicard: {} is a {} card to {} but '
                             'melds with {} into {}.'.format(
                                 self.name, self.multitype, self.multicard,
                                 self.meld_pair, self.melded))
            elif self.meld_pair:
                logger.error('Malformed multicard: {} is a {} card to {} but '
                             'melds from {}.'.format(
                                 self.name, self.multitype, self.multicard,
                                 self.meld_pair))
            elif (self.multitype and not self.multicard
                  or self.multicard and not self.multitype):
                logger.error('Malformed multicard: {} is a {} card to {}.'
                             .format(self.name, self.multitype, self.multicard))

        # The other card should have multicard and multitype set
        # We only need to do this once, so if the other card isn't defined yet,
        # we can just wait for it to be created.
        if self.multicard and self.multicard in _all_cards:
            mc = _all_cards[self.multicard]
            if mc.multitype != self.multitype:
                logger.error('Multitype mismatch: {} ({}) vs {} ({})'
                             .format(self.name, self.multitype,
                                     mc.name, mc.multitype))
            if mc.multicard != self.name:
                logger.error('Multicard discrepancy: {} ({}) vs {} ({})'
                             .format(self.name, self.multicard,
                                     mc.name, mc.multicard))
        elif self.multitype == 'meld':
            mcards = self.melded and [self.melded] or []
            if self.meld_pair:
                mcards.extend(self.meld_pair.split('; '))
            if len(mcards) != 2:
                logger.error('Malformed meld card: {} pair/from {} into {}.'
                             .format(self.name, self.meld_pair, self.melded))
            elif all(name in _all_cards for name in mcards):
                if self.melded:
                    # This is one of the components.
                    pc = _all_cards[self.meld_pair]
                    if pc.multitype != self.multitype:
                        logger.error('Multitype mismatch: {} ({}) vs {} ({})'
                                     .format(self.name, self.multitype,
                                             pc.name, pc.multitype))
                    else:
                        if pc.meld_pair != self.name:
                            logger.error('Meld pair discrepancy: '
                                         '{} ({}) vs {} ({})'
                                         .format(self.name, self.meld_pair,
                                                 pc.name, pc.meld_pair))
                        if pc.melded != self.melded:
                            logger.error('Melded discrepancy: '
                                         '{} ({}) vs {} ({})'
                                         .format(self.name, self.melded,
                                                 pc.name, pc.melded))
                    mc = _all_cards[self.melded]
                    if mc.multitype != self.multitype:
                        logger.error('Multitype mismatch: {} ({}) vs {} ({})'
                                     .format(self.name, self.multitype,
                                             mc.name, mc.multitype))
                    elif (not mc.meld_pair or ';' not in mc.meld_pair
                          or self.name not in mc.meld_pair.split('; ')):
                        logger.error('Melded discrepancy: {} ({}) vs {} ({})'
                                     .format(self.name, self.melded,
                                             mc.name, mc.meld_pair))
                    elif pc.name not in mc.meld_pair.split('; '):
                        logger.error('Melded discrepancy: {} ({}) vs {} ({})'
                                     .format(pc.name, pc.melded,
                                             mc.name, mc.meld_pair))
                else:
                    # This is the melded card.
                    n1, n2 = mcards
                    c1, c2 = _all_cards[n1], _all_cards[n2]
                    if c1.multitype != self.multitype:
                        logger.error('Multitype mismatch: {} ({}) vs {} ({})'
                                     .format(self.name, self.multitype,
                                             c1.name, c1.multitype))
                    elif c2.multitype != self.multitype:
                        logger.error('Multitype mismatch: {} ({}) vs {} ({})'
                                     .format(self.name, self.multitype,
                                             c2.name, c2.multitype))
                    else:
                        if c1.melded != self.name:
                            logger.error('Melded discrepancy: '
                                         '{} ({}) vs {} ({})'
                                         .format(self.name, self.meld_pair,
                                                 c1.name, c1.melded))
                        if c2.melded != self.name:
                            logger.error('Melded discrepancy: '
                                         '{} ({}) vs {} ({})'
                                         .format(self.name, self.meld_pair,
                                                 c2.name, c2.melded))
                        if c1.meld_pair != c2.name or c1.name != c2.meld_pair:
                            logger.error('Meld pair discrepancy: '
                                         '{} ({}) vs {} ({})'
                                         .format(c1.name, c1.meld_pair,
                                                 c2.name, c2.meld_pair))

        self.shortname = None
        if 'legendary' in self.typeline:
            self.shortname = str(make_shortname(self.name))
            if self.shortname:
                logger.debug("Shortname for {} set to {}."
                             .format(self.name, self.shortname))
                all_shortnames[self.shortname] = self.name

        uname = construct_uname(self.name)
        all_names[self.name] = uname
        all_names_inv[uname] = self.name
        _all_cards[self.name] = self

        for s in self.sets:
            if s not in cards_by_set:
                cards_by_set[s] = {self.name}
            else:
                cards_by_set[s].add(self.name)

    def __eq__(self, c):
        return type(self) == type(c) and self.name == c.name

    def __ne__(self, c):
        return type(self) != type(c) or self.name != c.name

    def __hash__(self):
        return self.name.__hash__()

    def __repr__(self):
        return ('<{0.__module__}.{0.__name__} instance {1}>'
                .format(self.__class__, vars(self)))

    def __str__(self):
        v = vars(self)
        s = []
        for c in ['name', 'shortname', 'cost', 'color', 'typeline', 'pt',
                  'sets', 'rules', 'multitype', 'multicard']:
            if v[c]:
                s.append('{}: {}'.format(c, v[c]))
        return '\n'.join(s)


def scryfall_card(layout=None, card_faces=None, all_parts=None,
                  **kwargs):
    """ Constructs Card objects from a Scryfall json object. """
    # Base stats. Might be overridden by card_faces.
    # Scryfall doesn't provide the list of sets a card was printed in,
    # but provides legalities if we want to group cards together.
    # MTGJSON also provides printings and keeps split etc cards separate,
    # but has multiple copies of many cards and does not provide a way
    # to identify meld direction.
    stats = ['name', 'type_line', 'mana_cost', 'colors', 'oracle_text',
             'loyalty', 'power', 'toughness', 'legalities']
    d = {stat: kwargs[stat] for stat in stats if stat in kwargs}
    name = kwargs['name']
    if layout in ('split', 'flip', 'transform'):
        # Doesn't support any number more than 2
        d['multitype'] = layout
        d2 = copy.deepcopy(d)
        d.update(card_faces[0])
        d2.update(card_faces[1])
        d2['multicard'], d['multicard'] = [c['name'] for c in card_faces]
        return [Card(**d), Card(**d2)]
    if layout == 'meld':
        d['multitype'] = layout
        # the collector number is b for the meld target
        parts = [x['name'] for x in all_parts[:3] if x['uri'][-1] == 'a']
        target = [x['name'] for x in all_parts[:3] if x['uri'][-1] == 'b']
        if name == target[0]:
            return [Card(meld_pair='; '.join(parts), **d)]
        else:
            pair = name == parts[0] and parts[1] or parts[0]
            return [Card(meld_pair=pair, melded=target[0], **d)]
    if layout not in ('normal', 'leveler', 'saga'):
        logger.error("Not a valid card: {} ({})".format(name, layout))
        return []
    return [Card(**d)]


class CardWidget(progressbar.widgets.WidgetBase):
    def __init__(self):
        self.current_card = ' '

    def __call__(self, progress, data):
        if len(self.current_card) < 16:
            return self.current_card + (16 - len(self.current_card)) * ' '
        else:
            return self.current_card[:16]

class CardProgressBar(list):
    """ A list-like object that writes a progress bar to stdout
        when iterated over. """
    def __iter__(self):
        """ A generator that writes a progress bar to stdout as its elements
            are accessed. """
        widgets = [CardWidget(), ' ', progressbar.widgets.Bar(left='[', right=']'), ' ',
                   progressbar.widgets.SimpleProgress(), ' ', progressbar.widgets.ETA()]
        pbar = progressbar.bar.ProgressBar(widgets=widgets, max_value=len(self))
        pbar.start()
        for i, card in enumerate(super(CardProgressBar, self).__iter__()):
            widgets[0].current_card = card.name
            pbar.update(i)
            yield card
        pbar.finish()

## Multiprocessing support for card-related tasks

class CardProgressQueue(multiprocessing.queues.JoinableQueue):
    def __init__(self, cards):
        super(CardProgressQueue, self).__init__(
                len(cards), ctx=multiprocessing.get_context())
        self._cw = CardWidget()
        widgets = [self._cw, ' ', progressbar.widgets.Bar(left='[', right=']'), ' ',
                   progressbar.widgets.SimpleProgress(), ' ', progressbar.widgets.ETA()]
        self._pbar = progressbar.bar.ProgressBar(widgets=widgets, max_value=len(cards))
        self._pbar.start()
        for c in cards:
            self.put(c)

    def task_done(self, cname=None):
        with self._cond:
            if not self._unfinished_tasks.acquire(False):
                raise ValueError('task_done() called too many times')
            self._cw.current_card = cname or ' '
            if self._unfinished_tasks._semlock._is_zero():
                self._pbar.finish()
                self._cond.notify_all()
            else:
                self._pbar.update(self._sem._semlock._get_value())

def _card_worker(work_queue, res_queue, func):
    logger.debug("Card worker starting up - Python {}".format(sys.version))
    try:
        while True:
            c = work_queue.get(timeout=0.2)
            try:
                res = func(c)
                res_queue.put(res)
            except queue.Full:
                logger.error("Result queue full, can't add result for {}."
                             .format(c.name))
                res_queue.put(None)
            except Exception as e:
                logger.exception('Exception encountered processing {} for '
                                 '{}: {}'.format(func.__name__, c.name, e))
                res_queue.put(None)
            finally:
                work_queue.task_done(cname=c.name)
    except queue.Empty:
        return
    except Exception as e:
        logger.fatal('Fatal exception processing {}: {}'
                     .format(func.__name__, e))

def map_multi(func, cards, processes=None):
    """ Applies a given function to each card in cards, utilizing
        multiple processes, and displaying progress with a CardProgressBar.
        Results are not guaranteed to be in any order relating to the
        initial order of cards, and all None results and exceptions thrown
        are stripped out. If correlated results are desired, the function
        should return the name of the card alongside the result.

        func: A function that takes in a single Card object as an argument.
            Any modifications this function makes to Card data will be lost
            when it exits, hence it should return said data and the callee
            should modify the Card as specified. The only caveat to this is
            that the data it returns must be pickleable.
        cards: An iterable of Card objects that supports __len__.
        processes: The number of processes. If None, defaults to the 
            number of CPUs. """
    if not processes:
        processes = multiprocessing.cpu_count()
    q = CardProgressQueue(cards)
    rq = multiprocessing.Queue()
    pr = [multiprocessing.Process(target=_card_worker, args=(q, rq, func))
          for i in range(processes)]
    for p in pr:
        p.start()
    q.join()
    result = []
    for i in range(len(cards)):
        res = rq.get()
        if res is not None:
            result.append(res)
    for p in pr:
        p.join()
    return result

## cardname processing ##

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
        if ', ' in name:
            ns = name.split(', ', 1)
            if ns[0] == ns[1] and ns[0] in cardnames:
                yield (ns[0],)
                return
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
    if len(words) > ll:
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
    for cardname in parentnames:
        if cardname in line:
            line, count = re.subn(r"\b{}(?!\w)".format(cardname),
                                  "PARENT", line, flags=re.UNICODE)
            if count > 0:
                change = True
                _parentcards.add(cardname)
    return line, change

def preprocess_names(line, selfnames=(), parentnames=()):
    """ This requires that each card was instantiated as a Card and their names
        added to the all_names dicts as appropriate. """
    change = False
    match = name_ref.search(line)
    while match:
        # Examine the words after the name_ref indicator
        i, j = match.regs[0]
        words = line[j:].split()
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
            res = good and good[0] or bad and bad[0] or None
            if res:
                logger.debug("Selected name(s) at position {} "
                              "as: {}".format(j, "; ".join(res)))
                line = (line[:j] + format_by_name(res, words))
                if len(res) == 1 and '"' not in line[:i] and not parentnames:
                    # Check for abilities granted
                    t = abil.search(line[j:])
                    if t:
                        m, n = t.regs[0]
                        # Created tokens don't get shortnames
                        line = (line[:m + j]
                                + preprocess_names(t.group(), (res[0],),
                                                   selfnames)
                                + line[n + j:])
                        j += n
                change = True
            else:
                logger.warning("Unable to interpret name(s) "
                               "at position {}: {}."
                               .format(j, words[0]))
        match = name_ref.search(line, j)
    # Check for abilities granted to things that aren't named tokens
    # Luckily we do not need to consider matching names in abilities
    # granted in abilities granted
    # (eg. get an emblem with "creatures have 'T: this creature...'"
    # although we could replace 'this creature' with SELF...)
    abil_change = False
    if not parentnames:
        # Granting abilities to oneself vs granting abilities to something
        # else: how do we determine it? So far, all granted abilities are
        # from a) self-granting, b) creating tokens, c) enchanting/equipping.
        # d) 'each' effects like Torrent of Lava or Slivers.
        parentwords = ('equipped', 'enchanted', 'fortified', 'create', 'each')
        i = 0
        t = abil.search(line[i:])
        if t:
            m, _ = t.regs[0]
            parent = True
            # Instead of a greedy reverse search for a related word
            # split the phrase on "," and " and " and search each segment.
            segments = preprocess_cardname(line[:m], selfnames)[0].split(', ')
            segments[-1:] = segments[-1].split(' and ')
            for segment in reversed(segments):
                for w in segment.split():
                    if w in parentwords:
                        break
                    elif w == 'SELF':
                        parent = False
                        break
                else:
                    continue
                break
        while t:
            m, n = t.regs[0]
            if parent:
                mid, change = preprocess_cardname(t.group(), (), selfnames)
            else:
                mid, change = preprocess_cardname(t.group(), selfnames)
            line = (line[:m + i] + mid + line[n + i:])
            abil_change = abil_change or change
            i += n
            t = abil.search(line[i:])
    # CARDNAME processing occurs after the "named" processing
    line, cardname_change = preprocess_cardname(line, selfnames, parentnames)
    if abil_change:
        logger.info("Detected cardnames in an ability granted by {}: {}"
                    .format(selfnames[0], line))
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
    """ Lowercase every word (but not SELF, PARENT, NAME_, or
        bare mana symbols). """
    if len(text) == 1:
        return text
    ws = text.split(' ')
    vs = []
    for w in ws:
        if 'SELF' in w or 'PARENT' in w or 'NAME_' in w:
            vs.append(w)
        else:
            vs.append(w.lower())
    return ' '.join(vs)

# Min length is 2 to avoid the sole exception of "none".
_non = re.compile(r"\bnon(\w{2,})", flags=re.I|re.U)

def preprocess_non(text):
    """ Ensure a dash appears between non and the word it modifies. """
    return _non.sub(r"non-\1", text)

## Main entry point for the preprocessing step ##

def preprocess_all(cards):
    """ Scans the rules texts of every card to replace any card names that
        appear with appropriate symbols, and eliminates reminder text. """
    print("Processing cards for card names...")
    for c in CardProgressBar(cards):
        names = (c.name,)
        if c.shortname:
            names += (c.shortname,)
        lines = [preprocess_capitals(preprocess_names(
                    preprocess_reminder(line), names))
                 for line in c.rules.split("\n")]
        c.rules = preprocess_non("\n".join(lines))

def get_cards():
    """ Returns a set of all the Cards instantiated with the Card class. """
    return set(_all_cards.values())

def get_card_set(setname):
    """ Returns a set of all the Cards in the given set. """
    if setname not in cards_by_set:
        return set()
    return {_all_cards.get(cardname) for cardname in cards_by_set[setname]}

def get_card(cardname):
    """ Returns a specific card by name, or None if no such card exists. """
    cardname = str(cardname)
    return _all_cards.get(all_shortnames.get(cardname, cardname))

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
    r = re.compile(r"([\w'-—]+)(?: | ?—){}".format(text), reflags)
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
    r = re.compile(r"{}(?: |— ?)([\w'-—]+)".format(text), reflags)
    a = set()
    for c in cards:
        a.update(r.findall(c.rules))
    return a

def matching_text(text, cards=None, reflags=re.I|re.U, group=0):
    """ Returns a set of all matches for the given regex.
        By default use the whole match. Set group to use only the specific
        match group.

        A subset of cards can be specified if one doesn't want to search
        the entire set. """
    if not cards:
        cards = get_cards()
    r = re.compile(text, reflags)
    a = set()
    for c in cards:
        for m in r.finditer(c.rules):
            a.add(m.group(group))
    return a

def counter_types(cards=None):
    """ Returns a list of counter types named in the given cards. """
    cwords = preceding_words('counter', cards=cards)
    # Disallow punctuation, common words, and words about countering spells.
    cwords = {w for w in cwords if w and w[-1] not in '—-,.:\'"'}
    common = {'a', 'all', 'and', 'be', 'control', 'each', 'five', 'had',
              'have', 'is', 'may', 'more', 'of', 'or', 'spell', 'that',
              'those', 'was', 'with', 'would', 'x'}
    return sorted(cwords - common)

def missing_words(cards=None):
    """ Returns a set of new words not accounted for in keywords.py. """
    from keywords import all_words, macro_words
    existing_words = {w for y in set(all_words) | macro_words for w in y.split()}
    if not cards:
        cards = get_cards()
    # May miss words with apostrophes and dashes. Do we care?
    seen_words = set(w for c in cards
                     for w in c.rules.split()
                     if w.isalpha())
    common_words = {'SELF', 'PARENT', 'x', 'y', 'plainswalk', 'islandwalk',
                    'swampwalk', 'mountainwalk', 'forestwalk', 'desertwalk',
                    'plainscycling', 'islandcycling', 'swampcycling',
                    'mountaincycling', 'forestcycling', 'landcycling',
                    'slivercycling', 'wizardcycling',
                    'arabian', 'nights'}
    return seen_words - existing_words - common_words

def missing_types(cards=None):
    """ Returns a set of new subtypes not accounted for in keywords.py. """
    from keywords import subtypes, types
    existing_types = set(subtypes) | set(types)
    if not cards:
        cards = get_cards()
    seen_types = set(w for c in cards for w in c.typeline.split())
    not_types = {'—'}
    return seen_types - existing_types - not_types

