"""The Google Keep List Sync integration."""

from __future__ import annotations

import logging

from gkeepapi import Keep
from gkeepapi.exception import APIException, LoginException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, InvalidStateError

from .const import (
    CONF_BASE_USERNAME,
    CONF_LIST_ID,
    CONF_LIST_TITLE,
    DOMAIN,
    MISSING_LIST,
    SERVICE_NAME_BASE,
    SHOPPING_LIST_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up of Google Keep List component."""

    hass.data.setdefault(DOMAIN, {})

    # Check for dependencies
    if not hass.data.get(SHOPPING_LIST_DOMAIN):
        _LOGGER.error(
            "Shopping list integration is missing, please add it to Home Assistant and reload",
        )
        return False

    # Get instance of Google Keep and list
    try:
        keep = Keep()
        await hass.async_add_executor_job(
            keep.authenticate,
            config_entry.data.get(CONF_USERNAME),
            config_entry.data.get(CONF_ACCESS_TOKEN),
        )
    except LoginException as ex:
        raise ConfigEntryAuthFailed from ex
    except APIException as ex:
        _LOGGER.error(
            "Unable to communicate with Google Keep API (error code %s): %s",
            ex.code,
            ex,
        )
        return False

    if not keep.get(config_entry.data.get(CONF_LIST_ID)):
        _LOGGER.error(
            "List '%s' couldn't be found", config_entry.data.get(CONF_LIST_TITLE)
        )
        hass.config_entries.async_update_entry(
            config_entry,
            data={**config_entry.data, MISSING_LIST: True},
        )  # Update config to inform that the list is the problem
        raise ConfigEntryAuthFailed

    async def handle_sync_list(call) -> None:  # pylint: disable=unused-argument
        """Handle synchronizing the Google Keep list with Shopping list."""

        # Sync to get any new items
        await hass.async_add_executor_job(keep.sync)

        # Check if the list still exists
        if not (glist := keep.get(config_entry.data.get(CONF_LIST_ID))):
            _LOGGER.error(
                "List '%s' couldn't be found when syncing",
                config_entry.data.get(CONF_LIST_TITLE),
            )
            hass.config_entries.async_update_entry(
                config_entry,
                data={**config_entry.data, MISSING_LIST: True},
            )  # Update config to inform that the list is the problem
            config_entry.async_start_reauth(hass)
            return

        # Add items to HA and delete from Google Keep
        for item in glist.unchecked:
            _LOGGER.debug("syncing item: %s", item.text)
            await hass.services.async_call(
                "shopping_list",
                "add_item",
                {"name": item.text},
                True,
            )
            await hass.async_add_executor_job(item.delete)

        # Sync again to delete already added items
        await hass.async_add_executor_job(keep.sync)

    # Register the service - Allow for as many services as we have usernames
    hass.services.async_register(
        DOMAIN, get_service_name(config_entry), handle_sync_list
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:  # pylint: disable=unused-argument
    """Unload a config entry."""
    _LOGGER.debug("Unload integration")
    hass.services.async_remove(DOMAIN, get_service_name(config_entry))
    return True


def get_service_name(config_entry: ConfigEntry) -> str:
    """Retrieve the name for running a service."""
    return (
        f"{SERVICE_NAME_BASE}_"
        f"{config_entry.data[CONF_BASE_USERNAME]}_"
        f"{config_entry.data[CONF_LIST_TITLE]}"
    )


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate from an old configuration version."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        base_username = (
            config_entry.data[CONF_USERNAME].partition("@")[0].replace(".", "_")
        )
        unique_id = f"{base_username}-{config_entry.data[CONF_LIST_ID]}"
        title = f"{config_entry.data[CONF_USERNAME]}  - {config_entry.data[CONF_LIST_TITLE]}"
        data = {**config_entry.data, CONF_BASE_USERNAME: base_username}
        hass.config_entries.async_update_entry(
            config_entry, unique_id=unique_id, title=title, data=data
        )
        config_entry.version = 2

    if config_entry.version == 2 and config_entry.minor_version == 1:
        base_username = (
            config_entry.data[CONF_USERNAME].partition("@")[0].replace(".", "_")
        )
        hass.config_entries.async_update_entry(
            config_entry, data={**config_entry.data, CONF_BASE_USERNAME: base_username}
        )
        config_entry.minor_version = 2

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
