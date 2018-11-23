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

import json
import logging
import os

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
JSONCACHE = os.path.join(DATADIR, "cache", "scryfall-oracle-cards.json")

## Loader ##

def load(filename=JSONCACHE):
    """ Load the cards from the Scryfall Oracle JSON file. """
    if not os.path.exists(filename):
        # TODO: download file and continue
        return []
    with open(filename) as f:
        j = json.load(f)
    llog.debug("Loaded {} objects from {}.".format(len(j), filename))
    return j

