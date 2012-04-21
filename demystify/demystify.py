# -*- coding: utf-8 -*-

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
BANNED = [
    "Chaos Orb",
    "Falling Star",
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
                  '{0.text:{tlen}} {1}'
                  .format(t, DemystifyLexer.getTokenName(t.type), tlen=tlen))

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
            p, parse_result = _parse(rule, getattr(c, part), c.name)
            setattr(c, 'parsed_' + part, parse_result.tree)
            if p.getNumberOfSyntaxErrors():
                plog.debug('result: ' + parse_result.tree.toStringTree())
                errors += 1
    print('{} total errors.'.format(errors))

_cost = ur"""(?:^|— | "| ')([^."'()—]*?):"""
costregex = re.compile(_cost)

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

def _parse_ability_costs(c):
    """ Parse all ability costs of a single card, and list them
        in c.parsed_costs.
        Returns a pair (number of errors, set of unique errors). """
    c.parsed_costs = []
    errors = 0
    uerrors = set()
    for lineno, line in enumerate(c.rules.split('\n')):
        lineno += 1
        for m in costregex.finditer(line):
            text = m.group(1)
            p, parse_result = _parse('cost', text, c.name, lineno)
            tree = parse_result.tree
            c.parsed_costs.append(tree)
            if p.getNumberOfSyntaxErrors():
                mcase = _crawl_tree_for_errors(c.name, lineno, text, tree)
                if mcase:
                    uerrors.add(mcase)
                errors += 1
    return c.name, [t.toStringTree() for t in c.parsed_costs], errors, uerrors

def parse_ability_costs(cards):
    """ Find all ability costs in the cards and attempt to parse them. """
    ccards = set(card.get_card(c[0])
                 for c in card.search_text(_cost, cards=cards))
    errors = 0
    uerrors = set()
    plog.removeHandler(_stdout)
    # list of (cardname, parsed costs, number of errors, set of errors)
    results = card.map_multi(_parse_ability_costs, ccards)
    for cname, pc, e, u in results:
        card.get_card(cname).parsed_costs = pc
        errors += e
        uerrors |= u
    plog.addHandler(_stdout)
    print('{} total errors.'.format(errors))
    if uerrors:
        print('{} unique cases missing.'.format(len(uerrors)))
        plog.debug('Missing cases: ' + '; '.join(sorted(uerrors)))

# require two characters
_keyword_line = r'.[^."]$'
kwregex = re.compile(_keyword_line)
lvlptregex = re.compile(r'level \d|\d+/\d+')

def _parse_keywords(c):
    """ Parse all keyword lines of a single card, and list them
        in c.parsed_keywords.
        Returns a pair (number of errors, set of unique errors). """
    c.parsed_keywords = []
    errors = 0
    uerrors = set()
    for lineno, line in enumerate(c.rules.split('\n')):
        lineno += 1
        if kwregex.search(line) and not lvlptregex.match(line):
            p, parse_result = _parse('keywords', line, c.name, lineno)
            tree = parse_result.tree
            c.parsed_keywords.append(tree)
            if p.getNumberOfSyntaxErrors():
                mcase = _crawl_tree_for_errors(c.name, lineno, line, tree)
                if mcase:
                    uerrors.add(mcase)
                errors += 1
    return (c.name, [t.toStringTree() for t in c.parsed_keywords],
            errors, uerrors)

def parse_keyword_lines(cards):
    """ Parse all lines in the cards that are lists of keywords. """
    ccards = set(card.get_card(c[0])
                 for c in card.search_text(_keyword_line, cards=cards)
                 if not lvlptregex.match(c[1]))
    errors = 0
    uerrors = set()
    plog.removeHandler(_stdout)
    # list of (cardname, parsed_keywords, number of errors, set of errors)
    results = card.map_multi(_parse_keywords, ccards)
    for cname, pc, e, u in results:
        card.get_card(cname).parsed_keywords = pc
        errors += e
        uerrors |= u
    plog.addHandler(_stdout)
    print('{} total errors.'.format(errors))
    if uerrors:
        print('{} unique cases missing.'.format(len(uerrors)))
        plog.debug('Missing cases: ' + '; '.join(sorted(uerrors)))

def preprocess(args):
    raw_cards = []
    for clist in data.load().values():
        raw_cards.extend(clist)
    numcards = len(raw_cards)
    for rc in raw_cards:
        _ = card.Card.from_string(rc)
    cards = card.get_cards()
    split = set([c.name for c in cards if c.multitype == "split"])
    xsplit = set([c.multicard for c in cards if c.multitype == "split"])
    logging.debug("Split cards: " + "; ".join(sorted(split)))
    if split != xsplit:
        logging.error("Difference: " + "; ".join(split ^ xsplit))
    flip = set([c.name for c in cards if c.multitype == "flip"])
    xflip = set([c.multicard for c in cards if c.multitype == "flip"])
    logging.debug("Flip cards: " + "; ".join(sorted(flip)))
    if flip != xflip:
        logging.error("Difference: " + "; ".join(flip ^ xflip))
    trans = set([c.name for c in cards if c.multitype == "transform"])
    xtrans = set([c.multicard for c in cards if c.multitype == "transform"])
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
