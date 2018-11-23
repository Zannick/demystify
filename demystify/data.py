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

import datetime
import json
import logging
import os
import shutil
import time
import urllib.request

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
ORACLE_JSON = "scryfall-oracle-cards.json"
JSONCACHE = os.path.join(DATADIR, "cache", ORACLE_JSON)
METADATA = os.path.join(DATADIR, "cache", "scryfall.metadata")

## Scryfall Client ##

_last_req = datetime.datetime.min

def send_req(req):
    """ Ratelimits 151 ms between requests. """
    n = datetime.datetime.now()
    global _last_req
    if n - _last_req < datetime.timedelta(milliseconds=150):
        time.sleep(.151)
    _last_req = datetime.datetime.now()
    return urllib.request.urlopen(req)

def get_metadata():
    """ Grab the bulk-data info for the oracle cards. """
    req = urllib.request.Request("https://api.scryfall.com/bulk-data")
    try:
        with send_req(req) as response:
            j = json.load(response)
    except urllib.error.URLError as e:
        ulog.error("Could not download bulk-data info: {}".format(e))
        return
    for obj in j["data"]:
        if obj["type"] == "oracle_cards":
            return obj
    else:
        ulog.error("Help I don't have pagination implemented!")

def save_metadata(metadata, metadata_file=METADATA):
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def load_cached_metadata(metadata_file=METADATA):
    if os.path.exists(metadata_file):
        with open(metadata_file) as f:
            return json.load(f)
    return {}

def download(filename=JSONCACHE, metadata=None):
    """ Download the file. """
    if not metadata:
        metadata = get_metadata()
        if not metadata:
            # Bail, since we get the URI from the metadata.
            return False

    save_metadata(metadata)
    req = urllib.request.Request(metadata["permalink_uri"])
    try:
        with send_req(req) as response:
            with open(filename + ".tmp", 'wb') as f:
                shutil.copyfileobj(response, f)
                os.rename(filename + ".tmp", filename)
                return True
    except urllib.error.URLError as e:
        ulog.error("Error retrieving JSON file: {}".format(e))
        return False

def maybe_download(filename=JSONCACHE):
    """ Download the file or use the cached copy. """
    if not os.path.exists(filename):
        ulog.info("JSON file not found, downloading.")
        return download(filename)
    age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
            os.path.getmtime(filename))
    # Within 2 days, it's extremely likely that we don't even
    # need to check for updates.
    if age < datetime.timedelta(days=2):
        ulog.info("Using recent JSON file.")
        return True
    metadata = get_metadata()
    m2 = load_cached_metadata()
    if not m2:
        ulog.info("No saved metadata, redownloading JSON.")
        return download(metadata)
    # These will not be exactly equal since the timestamp updates daily.
    # Zipped file size will be the most telling, esp. when new cards are added.
    # URIs in objects shouldn't change, so it should be the case that only
    # content updates change the file size.
    if metadata["compressed_size"] == m2["compressed_size"]:
        ulog.info("Using unchanged JSON file.")
        return True
    ulog.info("Redownloading due to compressed file size change: {} => {}"
              .format(m2["compressed_size"], metadata["compressed_size"]))
    return download(metadata)

## Loader ##

def load(filename=JSONCACHE):
    """ Load the cards from the Scryfall Oracle JSON file. """
    if not maybe_download(filename):
        if os.path.exists(filename):
            ulog.info("Falling back to existing JSON file.")
        else:
            ulog.critical("Failed to get JSON file.")
            return {}
    with open(filename) as f:
        j = json.load(f)
    llog.debug("Loaded {} objects from {}.".format(len(j), filename))
    return j

