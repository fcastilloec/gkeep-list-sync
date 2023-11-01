# gkeep-list-sync

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for adding items to your **Home Assistant Shopping List** from a **Google Keep** list.
The integration relies on [gkeepapi](https://github.com/kiwiz/gkeepapi) for the synchronization.
This is meant to be used with Google Assistant to easily add items to Home Assistant Shopping List.

## Requirements

- A Google email and password to retrieve the note.
  Using an app password is recommended.

## Installation

1. Use your tool of choice to open the directory for your HA configuration (where you find configuration.yaml).
2. If you do not have a `custom_components` directory there, you need to create it.
3. In the `custom_components` directory, create a new folder called `gkeep_list_sync`.
4. Copy the contents of the [main branch](https://github.com/fcastilloec/gkeep-list-sync/tree/main) `custom_components/gkeep_list_sync/` to `custom_components/gkeep_list_sync/` in your Home Assistnat folder
5. Restart Home Assistant.
6. In the Home Assistant Configuration, add the new integration by searching for its name.

## Usage

The integration adds a service call that can be used on any automation to synchronize Google Keep List with Home Assistant Shopping List.

The service goes through the following steps:

1. Reads all unchecked items from the specified Google Keep list. Checked items are ignored.
2. Adds each item to Home Assistant Shopping List integration.
3. Delete the item from Google Keep list. This prevent double adding an item if the service is called again.
