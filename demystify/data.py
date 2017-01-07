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

"""data -- Demystify library for loading and updating card data."""

import difflib
import logging
import os
import re
from functools import partial

llog = logging.getLogger('Loader')
llog.setLevel(logging.INFO)
ulog = logging.getLogger('Updater')
ulog.setLevel(logging.INFO)
_stdout = logging.StreamHandler()
_stdout.setLevel(logging.INFO)
ulog.addHandler(_stdout)
dlog = logging.getLogger('Differ')
dlog.setLevel(logging.INFO)

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEXTFILES = [os.path.join(DATADIR, "text", c)
             for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0']

## Loader ##

_nameline = re.compile(r"^Name:", re.M)

def _smart_split(cardlist):
    """ Given a list of cards in Oracle format as a single string,
        splits them into blocks of single cards, each starting with a
        'Name:' line. """
    i = 0
    c = []
    for t in _nameline.finditer(cardlist):
        x, _ = t.regs[0]
        if x > i:
            c += [cardlist[i:x].strip()]
            i = x
    rem = cardlist[i:].strip()
    if rem.startswith('Name:'):
        c += [rem]
    return c

def load(files=None):
    """ Load the cards from the data files, and split them logically.
        
        Returns the raw cards as a dict mapping from filename to
        the list of cards in that file. """
    raw_cards = {}
    if not files:
        files = TEXTFILES
    for filename in files:
        llog.info("Loading cards from {}...".format(filename))
        with open(filename) as f:
            cards = _smart_split(f.read())
            c = len(cards)
            llog.debug("Loaded {} cards from {}.".format(c, filename))
            raw_cards[filename] = cards
    ncards = sum(len(rc) for rc in raw_cards.values())
    llog.info("Loaded {} cards total.".format(ncards))
    return raw_cards

## Updater ##

_cost = re.compile(r'^([0-9WUBRGCX]|\([0-9WUBRGCPS]/[0-9WUBRGCPS]\))+$', re.I)
_pt = re.compile(r'^[0-9*+-]+(/[0-9*+-]+)?$')
_sr = re.compile(r'^[0-9A-Z, -]+$')
_color = re.compile(r'^((White|Blue|Black|Red|Green)/?)+$')
_multi = re.compile(r'(Flip|Transform|split)s? (?:into|from|card) (.+).]$')
_meldwith = re.compile(r'Melds with (.+) into (.+).]$')
_meldfrom = re.compile(r'Melds from (.+) and (.+).]$')
_abil = re.compile(r'^\[[+-]?\d+\]')

class BasicTextParser:
    """ A parser for the text Oracle wordings as provided by
        http://www.yawgatog.com/resources/oracle/, which has already
        corrected many common old Gatherer text errors.

        The resultant format of the cards will add tags for everything but
        rules text, and they will appear in different order:
            Name:   Ravager of the Fells
            Color:  Red/Green
            Type:   Creature -- Werewolf
            P/T:    4/4
            S/R:    DKA-M
            M-type: Transform
            M-card: Huntmaster of the Fells
            Trample
            Whenever...
            At the...

        This guarantees that every multicard has the same format referencing
        its other half. (Of course, this only works for 2-in-1 cards. It will
        not work for split transform, flip transform, split flip transform,
        or the Unhinged card Who/What/When/Where/Why.)

        Meld cards will have M-type: Meld, but instead of M-card they will have
        M-pair and Melded, for the card they meld with and into, respectively.
        The melded card will only have M-pair, which will contain both
        components separated with a semi-colon.
    """

    def __init__(self):
        self._parsed_cards = []
        self._current_card = []
        self._rules_text = []
        self._has_type = False

    def _finish_card(self):
        if self._rules_text:
            self._current_card.extend(self._rules_text)
            self._rules_text = []
        # Don't put in any of the combined split cards.
        if '//' not in self._name:
            self._parsed_cards.append('\n'.join(self._current_card))
        self._current_card = []
        self._has_type = False

    def get_output(self):
        if self._current_card:
            self._finish_card()
        return self._parsed_cards

    def parse_data(self, data):
        if self._current_card:
            self._finish_card()
        for line in data:
            s = line.strip()
            if not s:
                self._finish_card()
                continue
            # First line is always name.
            # Then match for Cost, P/T, S/R.
            # Color indicators and multicard metadata are in brackets.
            # Type and Rules text are everything else. Since everything
            # must have a typeline, the first nonmatching line is the type.
            if not self._current_card:
                self._current_card.append('Name:   ' + s)
                self._name = s
            elif not self._has_type and _cost.match(s):
                self._current_card.append('Cost:   ' + s.upper())
            elif _pt.match(s):
                self._current_card.append('P/T:    ' + s)
            elif _sr.match(s):
                self._current_card.append('S/R:    ' + s)
            elif s.startswith('[') and not _abil.match(s):
                # Color indicator and multicard metadata.
                n = s.find(' color indicator')
                if n > -1:
                    c = s[1:n].strip()
                    if not _color.match(c):
                        ulog.error('{}: Bad color indicator {!r}'
                                   .format(self._name, c))
                    self._current_card.append('Color:  ' + c)
                m = _multi.search(s)
                if m:
                    t, c = m.groups()
                    t = t.capitalize()
                    self._current_card.append('M-type: ' + t)
                    if t == 'Split':
                        cards = c.split(' // ')
                        if len(cards) != 2:
                            ulog.error('{}: Unrecognized split card {!r}'
                                       .format(self._name, c))
                        elif self._name not in cards:
                            ulog.error('{}: Name not in split cardname {!r}'
                                       .format(self._name, c))
                        c = cards[1] if self._name == cards[0] else cards[0]
                    self._current_card.append('M-card: ' + c)
                    continue
                m = _meldwith.search(s)
                if m:
                    mw, mt = m.groups()
                    self._current_card.extend([
                        'M-type: Meld',
                        'M-pair: ' + mw,
                        'Melded: ' + mt,
                    ])
                    continue
                m = _meldfrom.search(s)
                if m:
                    self._current_card.extend([
                        'M-type: Meld',
                        'M-pair: ' + '; '.join(m.groups()),
                    ])
                    continue
            else:
                s = s.replace('--', '—')
                if not self._has_type:
                    self._has_type = True
                    self._current_card.append('Type:   ' + s)
                else:
                    s = s.replace('·', '\u2022')
                    self._rules_text.append(s)

def _parse(text_data, ckpt_file, checkpoint):
    parser = BasicTextParser()
    parser.parse_data(text_data)
    result = parser.get_output()
    if checkpoint:
        with open(ckpt_file, 'w') as f:
            f.write('\n\n'.join(result))
    return result

def _update(raw_cards):
    """ Given a list of raw cards (in Oracle format, but already separated,
        eg. by _smart_split), update the text files in data/
        by adding new card entries or updating existing entries. """
    alpha = {}
    # read in the data we already have
    for tfile, rcs in load().items():
        alpha[tfile[-1]] = {}
        for raw_card in rcs:
            name = raw_card[5:raw_card.index('\n')].strip()
            alpha[tfile[-1]][name] = raw_card
    added = 0
    updated = 0
    # Lines with whitespace only are junk
    differ = difflib.Differ(linejunk=lambda s: not s.strip())
    def sequencify(s):
        """ Make a sequence of lines that end in newlines. """
        return (s + '\n').splitlines(True)
    # Sort the new data
    for raw_card in raw_cards:
        raw_card = raw_card.strip()
        # Standardize capitalization of AE cards.
        raw_card = raw_card.replace('AE', 'Ae')
        name = raw_card[5:raw_card.index('\n')].strip()
        # TODO: factor out name -> filename function in case we decide
        # to reorganize again?
        initial = name[0] if name[0] in alpha else '0'
        if name in alpha[initial]:
            if alpha[initial][name] != raw_card:
                updated += 1
                diff = differ.compare(sequencify(alpha[initial][name]),
                                      sequencify(raw_card))
                dlog.info("Updating {}:\n{}"
                          .format(name, ''.join(diff)))
        else:
            added += 1
            dlog.info("Adding {}.".format(name))
        alpha[initial][name] = raw_card
    # write out the data
    for tfile in TEXTFILES:
        with open(tfile, 'w') as f:
            f.write('\n\n'.join(sorted(alpha[tfile[-1]].values())))
            f.write('\n')
    # The update count might include those with no changes.
    # But this usually doesn't happen, as reprinted cards get a new expansion.
    summary = ("Added {} new cards and updated {} old ones."
               .format(added, updated))
    ulog.info(summary)

def add_subcommands(subparsers):
    """ Adds the 'update' command to the main parser.
        subparsers should be the object returned by add_subparsers()
        called on the main parser. """
    subparser = subparsers.add_parser('update',
        description='Parse Oracle data and import into demystify.')
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--update', nargs='+', metavar='INFILE',
        # The loader will open these files, so we don't use FileType here
        help=('Skip parsing the raw data, and update the data '
              'files with the new data in the parsing checkpoint '
              'files listed.'))
    group.add_argument('-p', '--parse', nargs='+', metavar='INFILE',
        help=('Raw data, from eg. http://www.yawgatog.com/resources/oracle/, '
              'which will be parsed and modified into the format demystify '
              'expects.'))
    subparser.add_argument('--checkpoint-dir', metavar='CKPT_DIR',
        dest='ckpt_dir', default='/tmp/demystify',
        help=('With --checkpoint-requests and/or --checkpoint-parsing, '
              'sets the location of the directory that will contain the '
              'checkpoint files. Defaults to /tmp/demystify.'))
    subparser.add_argument('--checkpoint-parsing', action='store_true',
        help=('Write the parsing results into files in the '
              'checkpoint directory.'))
    subparser.add_argument('--checkpoint-only', action='store_true',
        help=('Quit immediately after the last checkpoint instead of '
              'continuing to the next step. No effect without '
              '--checkpoint-parsing.'))
    subparser.set_defaults(func=run_update)

def run_update(args):
    """ Main entry point for the 'update' subcommand.
        args is a Namespace object with the proper flags. """
    if args.checkpoint_parsing:
        if not os.path.exists(args.ckpt_dir):
            os.makedirs(args.ckpt_dir)
    skip_update = args.checkpoint_only and args.checkpoint_parsing
    card_data = []
    if args.update:
        skip_update = False
        for raw_cards in load(args.update).values():
            card_data.extend(raw_cards)
    else:
        for filename in args.parse:
            cfile = os.path.join(args.ckpt_dir, os.path.basename(filename))
            with open(filename, encoding='latin-1') as f:
                raw_cards = _parse(f, cfile, args.checkpoint_parsing)
                card_data.extend(raw_cards)

    # Finally, run the update.
    if not skip_update:
        _update(card_data)
