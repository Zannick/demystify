# -*- coding: utf-8 -*-

import argparse
import difflib
import logging
import os
import re
import urllib
import urllib2
from functools import partial
from HTMLParser import HTMLParser

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

GATHERER = 'http://gatherer.wizards.com/Pages/Search/Default.aspx'

# Match only cards with parentheses but not split cards
_parens = re.compile(r'([^/]*) \((.*)\)')
# Remove unnecessary padding around the mdash.
_mdash = re.compile(r'\s+(—|--)\s+')
# Replace unicode quotes with standard ones.
_quotes = re.compile(r'’|‘')
# Fix up mana symbols.
# {S}i}? => {S} , {(u/r){ => {(u/r)}{ , {1}0} => {10}, and p => {p}
_mana = re.compile(r'{S}i}?|{\d}\d}|{\(?\w/\w\)?(?={)| p ')
_kaboom = re.compile(r'Kaboom(?=[^!])')

_nameline = re.compile(r"^Name:", re.M)

## Loader ##

def _smart_split(cardlist):
    """ Given a list of cards in gatherer format as a single string,
        splits them into blocks of single cards, each starting with a
        'Name:' line. """
    i = 0
    c = []
    for t in _nameline.finditer(cardlist):
        x, _ = t.regs[0]
        if x > i:
            c += [cardlist[i:x].strip()]
            i = x
    c += [cardlist[i:].strip()]
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

def _fix_mana(name, m):
    sym = m.group(0)
    if sym[1] == 'S':
        f = '{S}'
    elif sym[1] in '0123456789':
        f = sym.replace('}', '', 1)
    elif sym[1] == 'p':
        f = ' {p} '
    else:
        f = sym + '}'
    ulog.info("{}: Replacing bad mana symbol '{}' with '{}'."
              .format(name, sym, f))
    return f

class ListCards(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        names = []
        with values as f:
            names = [line.strip().replace(' ', r'\s').replace('AE', u'Æ')
                     for line in f]
        setattr(namespace, self.dest, names)

class GathererParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self._level = 0
        self._parsed_cards = []
        self._current_card = []
        self._rules_text = ''

    def _finish_card(self):
        self._parsed_cards.append(''.join(self._current_card))
        self._current_card = []

    def get_output(self):
        self.close()
        if self._current_card:
            self._finish_card()
        return self._parsed_cards

    def handle_starttag(self, tag, attrs):
        if self._level == 0 and tag == 'div':
            if ('class', 'textspoiler') in attrs:
                self._level += 1
        elif self._level == 1 and tag == 'table':
            self._level += 1
            self._name = None
        elif self._level == 2 and tag == 'tr':
            self._level += 1
            self._header = None
        elif self._level == 3 and tag == 'td':
            self._level += 1

    def handle_data(self, data):
        if self._level == 4:
            s = data.strip()
            if self._header == 'Name:':
                # Fix up issues with names
                t, n = _quotes.subn("'", s)
                m = _parens.match(t)
                if m:
                    o, g = m.groups()
                    if o[2:].lower() in g.lower():
                        ulog.info('Correcting "{}" to "{}".'.format(s, g))
                        s = g
                    else:
                        ulog.info('Not correcting flip card "{}".'.format(s))
                elif n:
                    ulog.info('Correcting "{}" to "{}".'.format(s, t))
                    s = t
                if s:
                    self._name = s
            elif self._header == 'Type:':
                s = _mdash.sub(r' \1 ', s)
                s, n = _quotes.subn("'", s)
                if n:
                    ulog.info("{}: Corrected unicode quotes in the typeline."
                              .format(self._name))
            elif self._header == 'Rules Text:':
                s = _mana.sub(partial(_fix_mana, self._name), s)
                if self._name == 'Kaboom!':
                    s, c = _kaboom.subn('Kaboom!', s)
                    if c:
                        ulog.info("Corrected Kaboom!'s name in {} place(s)."
                                  .format(c))
                s, n = _quotes.subn("'", s)
                if n:
                    ulog.info("{}: Corrected unicode quotes in the rules text."
                              .format(self._name))
                self._rules_text += s
                return
            if s:
                if s[-1] == ':':
                    self._header = s
                    spacing = ' ' * (4 - (len(s) % 4))
                    if spacing == ' ':
                        spacing += ' ' * 4
                    s += spacing
                self._current_card.append(s)

    def handle_endtag(self, tag):
        if self._level == 1 and tag == 'div':
            self._level -= 1
        elif self._level == 2 and tag == 'table':
            self._level -= 1
        elif self._level == 3 and tag == 'tr':
            if self._rules_text:
                self._current_card.append(self._rules_text.strip())
                self._rules_text = ''
            if self._current_card:
                self._current_card.append('\n')
            self._level -= 1
            self._header = None
        elif self._level == 4 and tag == 'td':
            self._level -= 1

    def handle_startendtag(self, tag, attrs):
        if self._level == 4 and tag == 'br':
            if self._header == 'Rules Text:':
                self._rules_text += '\n'
            else:
                self._finish_card()

def _send_request(params):
    """ Build the actual request and send it. Returns the full html
        of the result. """
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    f = opener.open(GATHERER + '?' + urllib.urlencode(params))
    html = f.read()
    f.close()
    return html

def _request(alpha=False, format=None, cardset=None, cards=None):
    """ Construct and send requests to Gatherer.
        Results are yielded as a pair (html result, shortname),
        where shortname is a short description of the result, such as
        'Vintage-A' to describe Vintage cards starting with A. """
    params = {'output': 'spoiler', 'method': 'text'}
    if format:
        params['format'] = '["{}"]'.format(format)
    if cardset:
        params['set'] = '["{}"]'.format(cardset)
    ckpt_name = format or cardset or 'cards'
    if cards:
        params['name'] = '[m/^({})$/]'.format('|'.join(cards))
        yield (_send_request(params), ckpt_name)
    elif alpha:
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        headings = letters + ['(?!{})'.format('|'.join(letters))]
        for h in headings:
            ulog.info('Requesting for {}...'.format(h))
            params['name'] = '[m/^{}/]'.format(h)
            c = h if len(h) == 1 else '0'
            yield (_send_request(params), '{}-{}'.format(ckpt_name, c))
    else:
        yield (_send_request(params), ckpt_name)

def _parse(html_data, ckpt_file, checkpoint):
    parser = GathererParser()
    parser.feed(html_data)
    result = parser.get_output()
    if checkpoint:
        with open(ckpt_file, 'w') as f:
            f.write('\n'.join(result))
    return result

def _update(raw_cards):
    """ Given a list of raw cards (in Gatherer format, but already separated,
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
        description='Download data from gatherer and import into demystify.')
    subparser.add_argument('-a', '--alpha', action='store_true',
        help=('Use multiple requests, splitting by first letter. Useful for '
              'large requests like --format Vintage. Ignored if the '
              '--cards mode is used.'))
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--format',
        help='Limit the card search by format.')
    group.add_argument('-s', '--set', dest='cardset', metavar='SET',
        help='Limit the card search by set.')
    group.add_argument('-c', '--cards', metavar='INFILE',
        action=ListCards, type=argparse.FileType('r'),
        help=('Grab specific cards, each listed in the given file on its own '
              'line. You may use AE to indicate the symbol Æ. You must '
              'specify more than one card in this file this way, due to '
              'limitations in gatherer.'))
    group.add_argument('-p', '--parse', nargs='+',
        type=argparse.FileType('r'), metavar='INFILE',
        help=('Skip making any requests to gatherer, and parse the files '
              'given as if they were returned by gatherer.'))
    group.add_argument('-u', '--update', nargs='+', metavar='INFILE',
        # The loader will open these files, so we don't use FileType here
        help=('Skip sending requests and parsing html, and update the data '
              'files with the new data in the parsing checkpoint '
              'files listed.'))
    subparser.add_argument('--checkpoint-dir', metavar='CKPT_DIR',
        dest='ckpt_dir', default='/tmp/demystify',
        help=('With --checkpoint-requests and/or --checkpoint-parsing, '
              'sets the location of the directory that will contain the '
              'checkpoint files. Defaults to /tmp/demystify.'))
    subparser.add_argument('--checkpoint-requests', action='store_true',
        help=('Write the responses from Gatherer to files in the '
              'checkpoint directory.'))
    subparser.add_argument('--checkpoint-parsing', action='store_true',
        help=('Write the parsing results into files in the '
              'checkpoint directory.'))
    subparser.add_argument('--checkpoint-only', action='store_true',
        help=('Quit immediately after the last checkpoint instead of '
              'continuing to the next step. No effect without at least '
              'one of --checkpoint-requests or --checkpoint-parsing.'))
    subparser.set_defaults(func=run_update)

def run_update(args):
    """ Main entry point for the 'update' subcommand.
        args is a Namespace object with the proper flags. """
    if args.checkpoint_requests or args.checkpoint_parsing:
        if not os.path.exists(args.ckpt_dir):
            os.makedirs(args.ckpt_dir)
    skip_parse = (args.checkpoint_only and args.checkpoint_requests
                  and not args.checkpoint_parsing)
    skip_update = (args.checkpoint_only
                   and (args.checkpoint_requests or args.checkpoint_parsing))
    card_data = []
    if args.update:
        skip_update = False
        for raw_cards in load(args.update).values():
            card_data.extend(raw_cards)
    elif args.parse:
        for rfile in args.parse:
            cfile = os.path.splitext(rfile.name)[0] + '.txt'
            with rfile as g:
                raw_cards = _parse(g.read(), cfile, args.checkpoint_parsing)
                card_data.extend(raw_cards)
    else:
        # Run the parser after each request rather than after all of them.
        # But collate all the parsed data together and run the update last.
        for result, ckpt_name in _request(args.alpha, args.format,
                                          args.cardset, args.cards):
            if args.checkpoint_requests:
                cfile = os.path.join(args.ckpt_dir, ckpt_name + '.html')
                with open(cfile, 'w') as f:
                    f.write(result)
            if not skip_parse:
                cfile = os.path.join(args.ckpt_dir, ckpt_name + '.txt')
                raw_cards = _parse(result, cfile, args.checkpoint_parsing)
                card_data.extend(raw_cards)
    # Finally, run the update.
    if not skip_update:
        _update(card_data)

