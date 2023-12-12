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

When creating a new service you will be presented with 3 fields to fill in: 
- username (requred)
- password (optional)
- master token (optional)

You will need to fill out either password or master token as a way of authenticating to your google account via the keep api. App passwords are highly recommended, but if you are seeing authentication errors see the Authentication Options section for other methods.

## Usage

The integration adds one service per service entry in the integration page that can be called by any automation or script to synchronize Google Keep List with Home Assistant Shopping List.

Each service will go through the following steps:

1. Read all unchecked items from the specified Google Keep list. Checked items are ignored.
2. Adds each item to Home Assistant Shopping List integration.
3. Delete the item from Google Keep list. This prevent double adding an item if the service is called again.


## Authentication Options
It is recommended to login with an app password as this can be easily revoked if it were to become compromised. That being said, some accounts seem to have issues logging in with passwords (both the regular password and app passwords) depending on which device you are attempting to get a token from. A workaround that seems to work for these "problematic" accounts is to create a docker container and run a script to get the tokens which we can then pass into the keep api. Although this is the least secure by far (master tokens never expire) it should allow for any google account to use this integration

Steps to acquire a master token: (**only do this if username and password are NOT working**)
1. Install docker container if you do not already have it
2. In your preferred cli run the following commands

```
$ docker pull breph/ha-google-home_get-token:latest
$ docker run -it -d breph/ha-google-home_get-token
# use the returned container id inside the next command
$ docker exec -it <id> bash

# inside container
root@<id>:/# python3 get_tokens.py`
```

3. From the printed output you should get the master token for the account you entered, it will start with: aas_et/. Copy the whole token without any additional spaces into the master token field when setting up a new service in the integration ui. 


## Shoutouts/Credits
[@fcastilloec](https://github.com/fcastilloec) For creating this project and publishing it for us to use
[@lhy](https://github.com/LeeHanYeong) For the docker container to reliably get a master token over on [ha-google-home](https://github.com/leikoilja/ha-google-home/issues/599#issuecomment-1760800334)
