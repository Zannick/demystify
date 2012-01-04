import argparse
import logging

logging.basicConfig(level=logging.DEBUG, filename="LOG", filemode="w")
plog = logging.getLogger("Parser")
plog.setLevel(logging.DEBUG)
_stdout = logging.StreamHandler()
_stdout.setLevel(logging.WARNING)
_stdout.setFormatter('%(levelname)s: %(message)s')
plog.addHandler(_stdout)

import antlr3

import card
import data
from grammar import DemystifyLexer, DemystifyParser

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

def test_lex(cards):
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
                  .format(t, DemystifyParser.getTokenName(t.type), tlen=tlen))

def parse_card(c):
    """ Test the parser against a card. """
    Parser = DemystifyParser.DemystifyParser
    if isinstance(c, str):
        c = card.get_card(c)
    # mana cost
    ts = _token_stream(c.name, c.cost)
    ManaCostParser = Parser(ts)
    parse_result = ManaCostParser.card_mana_cost()
    print(c.cost)
    pprint_tokens(ts.getTokens())
    print(parse_result.tree.toStringTree())
    # TODO: rules text

def test_parse(rule, text, name=''):
    """ Give the starting rule and try to parse text. """
    ts = _token_stream(name or 'Sample text', text)
    p = DemystifyParser.DemystifyParser(ts)
    result = getattr(p, rule)()
    print(text)
    pprint_tokens(ts.getTokens())
    print(result.tree.toStringTree())

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
    loader = subparsers.add_parser('load')
    loader.add_argument('-i', '--interactive', action='store_true',
                        help='Enter interactive mode instead of exiting.')
    loader.set_defaults(func=preprocess)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
