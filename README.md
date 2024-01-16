# gkeep-list-sync

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for adding items to your **Home Assistant Shopping List** from a **Google Keep** list.
The integration relies on [gkeepapi](https://github.com/kiwiz/gkeepapi) for the synchronization.
This is meant to be used with Google Assistant to easily add items to the Home Assistant Shopping List.

## Requirements

- A Google email and password to retrieve the note.
  Using an app password is recommended.

## Installation

1. Use your tool of choice to open the directory for your HA configuration (where you find configuration.yaml).
2. If you do not have a `custom_components` directory there, you need to create it.
3. In the `custom_components` directory, create a new folder called `gkeep_list_sync`.
4. Copy the contents of the [main branch](https://github.com/fcastilloec/gkeep-list-sync/tree/main) `custom_components/gkeep_list_sync/` to `custom_components/gkeep_list_sync/` in your Home Assistant folder
5. Restart Home Assistant.
6. In the Home Assistant Configuration, add the new integration by searching for its name.

When creating a new service, you will be presented with three fields to fill in: 
- username (required)
- password (optional)
- master token (optional)

You will need to fill out either a password or master token as a way of authenticating to your Google account via `gkeepapi`. App passwords are highly recommended, but if you encounter authentication errors, see the [Authentication Options](https://github.com/fcastilloec/gkeep-list-sync/wiki/Authentication-Options) wiki page for other methods.

## Usage

The integration adds one service per entry, they can be called by any automation or script to synchronize the Google Keep List with Home Assistant Shopping List.

Each service will go through the following steps:

1. Read all unchecked items from the specified Google Keep list. Checked items are ignored.
2. Add each item to the Home Assistant Shopping List integration.
3. Delete the item from the Google Keep list. This prevents double-adding an item if the service is called again.

## Shoutouts/Credits

[@fcastilloec](https://github.com/fcastilloec) For creating this project and publishing it for us to use
[@lhy](https://github.com/LeeHanYeong) For the docker container to reliably get a master token over on [ha-google-home](https://github.com/leikoilja/ha-google-home/issues/599#issuecomment-1760800334)
