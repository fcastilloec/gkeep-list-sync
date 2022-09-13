#!/usr/bin/env python3
"""This script syncs a Google Keep note with Home Assistant Shopping list"""

import sys
import gkeepapi
import config_data

import ha_list

config = config_data.get_config()
token = config_data.get_token()
last_updated = config_data.get_updated_time()

# Load Google Keep List
keep = gkeepapi.Keep()
if token:
    # Resume from existing session
    try:
        keep.resume(config.email, token)
    except gkeepapi.exception.LoginException as error:
        if str(error) == "BadAuthentication":
            keep.login(config.email, config.password)
            config_data.save_token(keep.getMasterToken())
        else:
            raise error
else:
    # Login for first time
    keep.login(config.email, config.password)
    config_data.save_token(keep.getMasterToken())

# Get the list from Google Keep
gkeeplist = keep.get(config.noteID)

# Don't update if nothing has changed
if gkeeplist.timestamps.updated == last_updated:
    sys.exit()

# Check if there are items to add
num_items = len(gkeeplist.unchecked)

# Add items to HA
if num_items > 0:
    print(f"Adding {num_items}.")

    for item in gkeeplist.unchecked:
        ha_list.add(config.webhook, item.text)
        item.delete()

    keep.sync()
    config_data.save_updated_time(gkeeplist.timestamps.updated)
