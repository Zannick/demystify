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
from grammar import Demystify

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

def test_lex(cards):
    """ Test the lexer against the given cards' text, logging failures. """
    Lexer = Demystify.Demystify
    for c in card.CardProgressBar(cards):
        try:
            char_stream = antlr3.ANTLRStringStream(c.rules)
            lexer = Lexer(char_stream)
            lexer.card = c.name
            # tokenizes completely and logs on errors
            tokens = antlr3.CommonTokenStream(lexer).getTokens()
        except:
            print('Error lexing {}:\n{}'.format(c.name, c.rules))
            raise

def lex_card(c):
    """ Test the lexer against one card's text. """
    Lexer = Demystify.Demystify
    if isinstance(c, str):
        c = card.get_card(c)
    char_stream = antlr3.ANTLRStringStream(c.rules)
    lexer = Lexer(char_stream)
    lexer.card = c.name
    tokens = antlr3.CommonTokenStream(lexer).getTokens()
    print(c.rules)
    tlen = max(len(t.text) for t in tokens)
    for t in tokens:
        if t.channel != Demystify.HIDDEN_CHANNEL:
            print('{0.line:>2} {0.charPositionInLine:>4} {0.index:>3} '
                  '{0.text:{tlen}} {1}'
                  .format(t, Demystify.getTokenName(t.type), tlen=tlen))

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
    s = int(len(split) / 2)
    f = int(len(flip) / 2)
    logging.info("Discovered {} unique cards, from {}, including "
                 "{} split cards and {} flip cards."
                 .format(len(cards) - s - f, numcards, s, f))
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
