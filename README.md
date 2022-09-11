# gkeep-shopping

This project allows you to sync a **Google Keep Note** with your **Home Assistant Shopping list**.
This is useful for adding items using Google Assistant, while still keeping everything inside Home Assistant.
This is only a workaround since Google remove the option to use advance voice commands with IFTTT.

This project is a successor of the original **ifttt-server** which used IFTTT and Evernote to keep track of groceries.

## Requirements

- Python, `gkeepapi`, `pydantic`, `email-validator`, and `requests`
- A Google email and password to retrieve the note.
  See `gkeepapi` [Logging in](https://gkeepapi.readthedocs.io/en/latest/#logging-in) documentation for more details.
- A Google Keep note ID.
  See `gkeepapi` [Getting Notes](https://gkeepapi.readthedocs.io/en/latest/#getting-notes) documentation for more details.
- A Home Assistant webhook URL to interact with the Shopping List integration.
- The path to the `.shopping_list.json` file in your system.
  Usually found in `/usr/share/hassio/homeassistant/.shopping_list.json` but it varies depending on your installation/system.

## Configuration

We save the configuration and all other necessary files under the following directory:

- `%APPDATA%\gkeep-shopping` on Windows
- `$XDG_CONFIG_HOME/gkeep-shopping` or `~/.config/gkeep-shopping` on Linux
- `~/Library/Application Support/gkeep-shopping` on macOS

The main configuration file is named `config.json`, and should be place on the directory mentioned previously.
There's a template for it here: [`templates/config.json`](https://github.com/fcastilloec/gkeep-shopping/blob/master/templates/config.json)

## Running the script

The main script is called `gkeep.py` and can be call using python.
It's recommended to run the script on a regular interval, as to keep the list/note synchronized.
