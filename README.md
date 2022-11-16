# gkeep-list-sync

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for adding items to your **Home Assistant Shopping List** from a **Google Keep** list.
The integration relies on [gkeepapi](https://github.com/kiwiz/gkeepapi) for the synchronization.
This is meant to be used with Google Assistant to easily add items to Home Assistant Shopping List.

## Requirements

- A Google email and password to retrieve the note.
  Using an app password is recommended.

## Installation

1. Use the tool of choice to open the directory for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory there, you need to create it.
3. In the custom*components directory create a new folder called \_gkeep_list_sync*.
4. Download all the files from the custom_components/gkeep_list_sync/ directory in this repository.
5. Place the files you downloaded in the new directory you created.
6. Restart Home Assistant.
7. In the Home Assistant Configuration, add the new integration by searching for its name.

## Usage

The integration adds a service call that can be used on any automation to synchronize Google Keep List with Home Assistant Shopping List.

The service goes through the following steps:

1. Reads all unchecked items from the specified Google Keep list. Checked items are ignored.
2. Adds each item to Home Assistant Shopping List integration.
3. Delete the item from Google Keep list. This prevent double adding an item if the service is called again.
