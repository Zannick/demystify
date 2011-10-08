import difflib
import os
import re
import sys
import logging

import antlr3

from . import card
from .grammar import Demystify

logging.basicConfig(level=logging.DEBUG, filename="LOG")
plog = logging.getLogger("Parser")
plog.setLevel(logging.DEBUG)
ulog = logging.getLogger("Updater")
ulog.setLevel(logging.INFO)

DATADIR = os.path.join(os.path.dirname(__file__), "data/")
TEXTDIR = DATADIR + "text/"
TEXTFILES = [TEXTDIR + c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0']

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

nameline = re.compile(r"^Name:", re.M)

def smart_split(cardlist):
    """ Given a list of cards in gatherer format as a single string,
        splits them into blocks of single cards, each starting with a
        'Name:' line. """
    i = 0
    c = []
    for t in nameline.finditer(cardlist):
        x, _ = t.regs[0]
        if x > i:
            c += [cardlist[i:x].strip()]
            i = x
    c += [cardlist[i:].strip()]
    return c

def load():
    """ Load the cards from the data files. These are stored statically
        in the card module.
        
        Returns the number of cards loaded. """
    count = 0
    for filename in TEXTFILES:
        logging.info("Loading cards from {}...".format(filename))
        with open(filename) as f:
            raw_cards = smart_split(f.read())
            c = len(raw_cards)
            for cs in raw_cards:
                _ = card.Card.from_string(cs)
            logging.debug("Loaded {} cards from {}.".format(c, filename))
            count += c
    return count

def update(files):
    """ Given a list of text files (not the ones in data/) containing card
        data, update the text files in data/ by adding new card entries or
        updating existing entries. """
    alpha = {}
    # read in the data we already have
    for tfile in TEXTFILES:
        with open(tfile) as f:
            alpha[tfile[-1]] = {}
            for raw_card in smart_split(f.read()):
                name = raw_card[5:raw_card.index('\n')].strip()
                alpha[tfile[-1]][name] = raw_card
    added = 0
    updated = 0
    # Lines with whitespace only are junk
    differ = difflib.Differ(linejunk=lambda s: not s.strip())
    def sequencify(s):
        """ Make a sequence of lines that end in newlines. """
        return (s + '\n').splitlines(True)
    # read in the new data
    for ufile in files:
        with open(ufile) as f:
            for raw_card in smart_split(f.read()):
                name = raw_card[5:raw_card.index('\n')].strip()
                initial = name[0] if name[0] in alpha else '0'
                if name in alpha[initial]:
                    updated += 1
                    diff = differ.compare(sequencify(alpha[initial][name]),
                                          sequencify(raw_card))
                    ulog.info("Updating {}:\n{}".format(name, ''.join(diff)))
                else:
                    added += 1
                    ulog.info("Adding {}.".format(name))
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
    print(summary)
    ulog.info(summary)

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

def main():
    if len(sys.argv) > 1:
        if len(sys.argv) > 2 and sys.argv[-1] == '-q':
            update(sys.argv[1:-1])
            return
        else:
            update(sys.argv[1:])
    numcards = load()
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
