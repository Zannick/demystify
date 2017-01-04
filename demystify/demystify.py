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

"""demystify -- A Magic: The Gathering parser."""

import argparse
import logging
import re

logging.basicConfig(level=logging.DEBUG, filename="LOG", filemode="w")
plog = logging.getLogger("Parser")
plog.setLevel(logging.DEBUG)
_stdout = logging.StreamHandler()
_stdout.setLevel(logging.WARNING)
_stdout.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
plog.addHandler(_stdout)

import antlr3

import card
import data
from grammar import DemystifyLexer, DemystifyParser
import test

# What we don't handle:
#   - physical interactions like dropping cards onto the table
#   - ownership changes
#   - subgames
# These aren't in Vintage anyway...
BANNED = [
    "Chaos Orb",
    "Falling Star",
    "Shahrazad",
    "Tempest Efreet",
    "Timmerian Fiends",
]
def get_cards():
    return [c for c in card.get_cards() if c.name not in BANNED]

## Lexer / Parser entry points ##

def _token_stream(name, text):
    """ Helper method for generating a token stream from text. """
    char_stream = antlr3.ANTLRStringStream(text)
    lexer = DemystifyLexer.DemystifyLexer(char_stream)
    lexer.card = name
    # tokenizes completely and logs on errors
    return antlr3.CommonTokenStream(lexer)

def _lex(c):
    try:
        tokens = _token_stream(c.name, c.rules).getTokens()
    except:
        print('Error lexing {}:\n{}'.format(c.name, c.rules))
        raise

def test_lex(cards):
    """ Test the lexer against the given cards' text, logging failures. """
    card.map_multi(_lex, cards)

def test_lex_s(cards):
    """ Test the lexer against the given cards' text, logging failures. """
    for c in card.CardProgressBar(cards):
        try:
            tokens = _token_stream(c.name, c.rules).getTokens()
        except:
            print('Error lexing {}:\n{}'.format(c.name, c.rules))
            raise

def lex_card(c):
    """ Test the lexer against one card's text. """
    if isinstance(c, str):
        c = card.get_card(c)
    tokens = _token_stream(c.name, c.rules).getTokens()
    print(c.rules)
    pprint_tokens(tokens)

def pprint_tokens(tokens):
    if not tokens:
        return
    tlen = max(len(t.text) for t in tokens)
    for t in tokens:
        if t.channel != antlr3.HIDDEN_CHANNEL:
            print('{0.line:>2} {0.charPositionInLine:>4} {0.index:>3} '
                  '{0.text:{tlen}} {0.typeName}'
                  .format(t, tlen=tlen))

def parse_card(c):
    """ Test the parser against a card. """
    Parser = DemystifyParser.DemystifyParser
    if isinstance(c, str):
        c = card.get_card(c)
    # mana cost
    ts = _token_stream(c.name, c.cost)
    ManaCostParser = Parser(ts)
    ManaCostParser.setCardState(c.name)
    parse_result = ManaCostParser.card_mana_cost()
    print(c.cost)
    pprint_tokens(ts.getTokens())
    print(parse_result.tree.toStringTree())
    # TODO: rules text

def _parse(rule, text, name, lineno=None):
    ts = _token_stream(name, text)
    if lineno:
        ts.line = lineno
    p = DemystifyParser.DemystifyParser(ts)
    p.setCardState(name)
    return p, getattr(p, rule)()

def test_parse(rule, text, name=''):
    """ Give the starting rule and try to parse text. """
    ts = _token_stream(name or 'Sample text', text)
    p = DemystifyParser.DemystifyParser(ts)
    p.setCardState(name)
    result = getattr(p, rule)()
    print(text)
    pprint_tokens(ts.getTokens())
    print(result.tree.toStringTree())
    return result

def parse_all(cards):
    """ Run the parser against each card's parseable parts. """
    # card attribute -> parser rule
    parts = { 'cost' : 'card_mana_cost',
              'typeline' : 'typeline' }
    errors = 0
    for c in card.CardProgressBar(cards):
        for part, rule in parts.items():
            a = getattr(c, part)
            if a:
                p, parse_result = _parse(rule, a, c.name)
                setattr(c, 'parsed_' + part, parse_result.tree)
                if p.getNumberOfSyntaxErrors():
                    plog.debug('result: ' + parse_result.tree.toStringTree())
                    errors += 1
    print('{} total errors.'.format(errors))

def _crawl_tree_for_errors(name, lineno, text, tree):
    """ Common helper function for gathering errors.
        Logs error text and returns a unique error case for the
        first encountered error. """
    plog.debug('{}:{}:text:{}'.format(name, lineno, text))
    plog.debug('{}:{}:result:{}'.format(name, lineno, tree.toStringTree()))
    queue = [tree]
    while queue:
        n = queue.pop(0)
        if n.children:
            queue.extend(n.children)
        if isinstance(n, antlr3.tree.CommonErrorNode):
            mstart = n.trappedException.token.start
            mend = text.find(',', mstart)
            if mend < 0:
                mend = len(text)
            mcase = text[mstart:mend]
            if not mcase:
                plog.warning('{}:{}:Empty case detected!'.format(name, lineno))
            return mcase

def parse_helper(cards, name, rulename, yesregex=None, noregex=None):
    """ Parse a given subset of text on a given subset of cards.

        This function may override some re flags on the
        provided regex objects.

        cards: An iterable of cards to search for matching text. To save time,
            the provided regexes will be used to pare down this list to just
            those that will actually have text to attempt to parse.
        name: The function will be named _parse_{name} and the results for
            card c will be saved to c.parsed_{name}.
        rulename: The name of the parser rule to run.
        yesregex: If provided, run the parser rule on each match within each
            line of the card. The text selected is group 1 if it exists, or
            group 0 (the entire match) otherwise. If not provided, use each
            line in its entirety.
        noregex: Any text found after considering yesregex (or its absence)
            is skipped if it matches this regex. """
    def _parse_helper(c):
        """ Returns a pair (number of errors, set of unique errors). """
        results = []
        errors = 0
        uerrors = set()
        for lineno, line in enumerate(c.rules.split('\n')):
            lineno += 1
            if yesregex:
                texts = [m.group(1) if m.groups() else m.group(0)
                         for m in yesregex.finditer(line)]
            else:
                texts = [line]
            if noregex:
                texts = [text for text in texts if not noregex.match(text)]
            for text in texts:
                p, parse_result = _parse(rulename, text, c.name, lineno)
                tree = parse_result.tree
                results.append(tree)
                if p.getNumberOfSyntaxErrors():
                    mcase = _crawl_tree_for_errors(c.name, lineno, text, tree)
                    if mcase:
                        uerrors.add(mcase)
                    errors += 1
        return (c.name, [t.toStringTree() for t in results], errors, uerrors)
    _parse_helper.__name__ = '_parse_{}'.format(name)

    if yesregex:
        pattern = yesregex.pattern
        if noregex:
            ccards = {card.get_card(c[0])
                      for c in card.search_text(pattern, cards=cards)
                      if not noregex.match(c[1])}
        else:
            ccards = {card.get_card(c[0])
                      for c in card.search_text(pattern, cards=cards)}
    elif noregex:
        ccards = {c for c in cards
                  if not all(noregex.match(line)
                             for line in c.rules.split('\n'))}
    else:
        ccards = set(cards)

    errors = 0
    uerrors = set()
    plog.removeHandler(_stdout)
    # list of (cardname, parsed result trees, number of errors, set of errors)
    results = card.map_multi(_parse_helper, ccards)
    cprop = 'parsed_{}'.format(name)
    for cname, pc, e, u in results:
        setattr(card.get_card(cname), cprop, pc)
        errors += e
        uerrors |= u
    plog.addHandler(_stdout)
    print('{} total errors.'.format(errors))
    if uerrors:
        print('{} unique cases missing.'.format(len(uerrors)))
        plog.debug('Missing cases: ' + '; '.join(sorted(uerrors)))

# All costs come before a colon, but these may occur at the start of a line,
# after an mdash, or after an opening quote for an ability.
costregex = re.compile(r"""(?:^|— | "| ')([^."'()—]*?):""")

# Skip lines that end in . or " or —, lines that are LEVEL dependent,
# and lines that have fewer than 2 characters.
keywordskipregex = re.compile(r'^.*[."—]$|{level |^.?$')

levels = re.compile(r'^{level')

# Triggers. Similar to costregex, these can occur at the start of an ability
# or sentence.
triggerregex = re.compile(r"""(?:^|— | "| '|\. )when(?:ever)? ([^,]*),""")

def parse_ability_costs(cards):
    """ Find all ability costs in the cards and attempt to parse them. """
    parse_helper(cards, 'costs', 'cost', yesregex=costregex, noregex=levels)

def parse_keyword_lines(cards):
    """ Parse all lines in the cards that are lists of keywords. """
    parse_helper(cards, 'keywords', 'keywords', noregex=keywordskipregex)

def parse_triggers(cards):
    """ Parse all trigger conditions in the cards. """
    parse_helper(cards, 'triggers', 'triggers', yesregex=triggerregex,
                 noregex=levels)

def preprocess(args):
    raw_cards = []
    for clist in data.load().values():
        raw_cards.extend(clist)
    numcards = len(raw_cards)
    for rc in raw_cards:
        _ = card.Card.from_string(rc)
    cards = card.get_cards()
    split = {c.name for c in cards if c.multitype == "Split"}
    xsplit = {c.multicard for c in cards if c.multitype == "Split"}
    logging.debug("Split cards: " + "; ".join(sorted(split)))
    if split != xsplit:
        logging.error("Difference: " + "; ".join(split ^ xsplit))
    flip = {c.name for c in cards if c.multitype == "Flip"}
    xflip = {c.multicard for c in cards if c.multitype == "Flip"}
    logging.debug("Flip cards: " + "; ".join(sorted(flip)))
    if flip != xflip:
        logging.error("Difference: " + "; ".join(flip ^ xflip))
    trans = {c.name for c in cards if c.multitype == "Transform"}
    xtrans = {c.multicard for c in cards if c.multitype == "Transform"}
    logging.debug("Transform cards: " + "; ".join(sorted(trans)))
    if trans != xtrans:
        logging.error("Difference: " + "; ".join(trans ^ xtrans))
    s = int(len(split) / 2)
    f = int(len(flip) / 2)
    t = int(len(trans) / 2)
    logging.info("Discovered {} unique (physical) cards, from {}, including "
                 "{} split cards, {} flip cards, and {} transform cards."
                 .format(len(cards) - s - f - t, numcards, s, f, t))
    legalcards = get_cards()
    logging.info("Found {} banned cards.".format(len(cards) - len(legalcards)))
    if len(cards) - len(legalcards) != len(BANNED):
        logging.warning("...but {} banned cards were named."
                        .format(len(BANNED)))
    card.preprocess_all(legalcards)
    if args.interactive:
        import code
        code.interact(local=globals())

def main():
    parser = argparse.ArgumentParser(
        description='A Magic: the Gathering parser.')
    subparsers = parser.add_subparsers()
    data.add_subcommands(subparsers)
    test.add_subcommands(subparsers)
    loader = subparsers.add_parser('load')
    loader.add_argument('-i', '--interactive', action='store_true',
                        help='Enter interactive mode instead of exiting.')
    loader.set_defaults(func=preprocess)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
