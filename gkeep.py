#!/usr/bin/env python3
"""This script syncs a Google Keep note with Home Assistant Shopping list"""

import sys
from os import environ
import gkeepapi
from config import get_config, get_updated_time, get_token, save_updated_time, save_token

if environ.get("PYTHON_ENV") == "development":
    import ha_list_local as ha_list
else:
    import ha_list


config = get_config()
token = get_token()
last_updated = get_updated_time()

# Load Google Keep List
keep = gkeepapi.Keep()
if token:
    # Resume from existing session
    try:
        keep.resume(config.email, token)
    except gkeepapi.exception.LoginException as error:
        if str(error) == "BadAuthentication":
            keep.login(config.email, config.password)
            save_token(keep.getMasterToken())
        else:
            raise error
else:
    # Login for first time
    keep.login(config.email, config.password)
    save_token(keep.getMasterToken())

gkeeplist = keep.get(config.noteID)

# Load Home Assistant Shopping list
halist = ha_list.ShoppingList(config.listPath, config.webhook)

# Don't update if nothing has changed
if gkeeplist.timestamps.updated == last_updated.google_keep and halist.updated == last_updated.home_assistant:
    print("Nothing to sync.")
    sys.exit()

# Check what type of update is needed
if gkeeplist.timestamps.updated > halist.updated:
    print("Updating HA with Gkeep info.")

    # DELETE ALL.
    # There's more requests and for loops if we decide to delete/add only the necessary items.
    halist.delete_all()

    # Delete checked from Google Keep.
    for item in gkeeplist.checked:
        item.delete()

    # Add items to HA
    for item in gkeeplist.unchecked:
        halist.add(item.text)
else:
    print("Updating Gkeep with HA info.")

    # Delete all Google Keep elements.
    for item in gkeeplist.items:
        item.delete()

    # Delete checked from HA.
    halist.delete_all(True)

    # Add items to Google Keep.
    for item in halist.unchecked:
        gkeeplist.add(item, False, gkeepapi.node.NewListItemPlacementValue.Bottom)

keep.sync()

save_updated_time(gkeeplist.timestamps.updated, halist.updated)
