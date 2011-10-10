# -*- coding: utf-8 -*-

import argparse
import re
import sys
import urllib
import urllib2
from functools import partial
from HTMLParser import HTMLParser

GATHERER = 'http://gatherer.wizards.com/Pages/Search/Default.aspx'

# Match only cards with parentheses but not split cards
_parens = re.compile(r'([^/]*) \((.*)\)')
# Fix up mana symbols.
# {S}i}? => {S} , {(u/r){ => {(u/r)}{ , {1}0} => {10}
_mana = re.compile(r'{S}i}?|{\d}\d}|{\(?\w/\w\)?(?={)| p ')

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
    print "{}: Replacing bad mana symbol '{}' with '{}'.".format(name, sym, f)
    return f

class ListCards(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        names = []
        with values as f:
            names = [line.strip().replace(' ', r'\s').replace('AE', u'Æ')
                     for line in f]
        setattr(namespace, self.dest, names)

class GathererParser(HTMLParser):
    def __init__(self, outstream):
        HTMLParser.__init__(self) # calls reset()
        self._out = outstream

    def reset(self):
        HTMLParser.reset(self)
        self._level = 0

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
                m = _parens.match(s)
                if m:
                    o, g = m.groups()
                    if o[2:].lower() in g.lower():
                        print 'Correcting "{}" to "{}".'.format(s, g)
                        s = g
                    else:
                        print 'Not correcting flip card "{}".'.format(s)
                if s:
                    self._name = s
            elif self._header == 'Rules Text:':
                s = _mana.sub(partial(_fix_mana, self._name), s)
            if len(s) > 1:
                if s[-1] == ':':
                    self._header = s
                    s += '    '
                self._out.write(s)

    def handle_endtag(self, tag):
        if self._level == 1 and tag == 'div':
            self._level -= 1
        elif self._level == 2 and tag == 'table':
            self._level -= 1
        elif self._level == 3 and tag == 'tr':
            self._out.write('\n')
            self._level -= 1
            self._header = None
        elif self._level == 4 and tag == 'td':
            self._level -= 1

    def handle_startendtag(self, tag, attrs):
        if self._level == 4 and tag == 'br':
            self._out.write('\n')

def send_request(params):
    """ Build the actual request and send it. Returns the full html
        of the result. """
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    f = opener.open(GATHERER + '?' + urllib.urlencode(params))
    html = f.read()
    f.close()
    return html

def get_html(alpha=False, format=None, cardset=None, cards=None):
    """ Construct and send requests to Gatherer, yielding the
        html results as strings. """
    params = {'output': 'spoiler', 'method': 'text'}
    if format:
        params['format'] = '["{}"]'.format(format)
    if cardset:
        params['set'] = '["{}"]'.format(cardset)
    if cards:
        params['name'] = '[m/^({})$/]'.format('|'.join(cards))
        yield send_request(params)
    elif alpha:
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        headings = letters + ['(?!{})'.format('|'.join(letters))]
        for h in headings:
            print 'Requesting for {}...'.format(h)
            params['name'] = '[m/^{}/]'.format(h)
            yield send_request(params)
    else:
        yield send_request(params)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='Download data from gatherer for import by demystify.')
    argparser.add_argument('-a', '--alpha', action='store_true',
        help=('Use multiple requests, splitting by first letter. Useful for '
              'large requests like --format Vintage. Ignored if the '
              '--cards mode is used.'))
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--format',
        help='Limit the card search by format.')
    group.add_argument('-s', '--set', dest='cardset', metavar='SET',
        help='Limit the card search by set.')
    group.add_argument('-c', '--cards', metavar='INFILE',
        action=ListCards, type=argparse.FileType('r'),
        help=('Grab specific cards, each listed in the given file on its own '
              'line. You may use AE to indicate the symbol Æ.'))
    group.add_argument('-p', '--parse-only',
        type=argparse.FileType('r'), metavar='INFILE',
        help=('Skip making any requests to gatherer, and parse the file '
              'given as if it were returned by gatherer.'))
    argparser.add_argument('-o', '--outfile',
        type=argparse.FileType('w'), default=sys.stdout,
        help=('Output file. Even with -a, all output goes here. '
              'If unspecified, output is printed to stdout.'))
    argparser.add_argument('--save-result', metavar='OUTFILE',
        type=argparse.FileType('w'),
        help='Write the html result of the request to the given file.')
    args = argparser.parse_args()
    with args.outfile:
        parser = GathererParser(args.outfile)
        if args.parse_only:
            with args.parse_only as g:
                parser.feed(g.read())
        else:
            for result in get_html(args.alpha, args.format,
                                   args.cardset, args.cards):
                if args.save_result:
                    args.save_result.write(result)
                    args.save_result.write('\n\n')
                parser.reset()
                parser.feed(result)
    if args.save_result:
        args.save_result.close()
