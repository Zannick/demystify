import difflib
import os
import re
import sys
import logging

from . import card

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
    # read in the new data
    for ufile in files:
        with open(ufile) as f:
            for raw_card in smart_split(f.read()):
                name = raw_card[5:raw_card.index('\n')].strip()
                initial = name[0] if name[0] in alpha else '0'
                if name in alpha[initial]:
                    updated += 1
                    diff = differ.compare(alpha[initial][name], raw_card)
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
    summary = ("Added {} new cards and updated {} old ones."
               .format(added, updated))
    print(summary)
    ulog.info(summary)

def main():
    if len(sys.argv) > 1:
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
