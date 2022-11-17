"""The Google Keep List Sync integration."""
from __future__ import annotations

import logging

from gkeepapi import Keep
from gkeepapi.exception import LoginException, APIException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, InvalidStateError
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_USERNAME

from .const import (
    DOMAIN,
    CONF_LIST_ID,
    SHOPPING_LIST_DOMAIN,
    MISSING_LIST,
    SERVICE,
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
            keep.resume,
            config_entry.data.get(CONF_USERNAME),
            config_entry.data.get(CONF_ACCESS_TOKEN),
        )
    except LoginException as ex:
        hass.data[DOMAIN] = {MISSING_LIST: False}  # the credentials are the problem
        raise ConfigEntryAuthFailed from ex
    except APIException as ex:
        _LOGGER.error(
            "Unable to communicate with Google Keep API (error code %s): %s",
            ex.code,
            ex,
        )
        return False

    if not keep.get(config_entry.data.get(CONF_LIST_ID)):
        hass.data[DOMAIN] = {MISSING_LIST: True}  # the list is the problem
        raise ConfigEntryAuthFailed

    async def handle_sync_list(call) -> None:  # pylint: disable=unused-argument
        """Handle synchronizing the Google Keep list with Shopping list"""

        # Sync to get any new items
        await hass.async_add_executor_job(keep.sync)

        # Check if the list still exists
        if not (glist := keep.get(config_entry.data.get(CONF_LIST_ID))):
            hass.data[DOMAIN] = {MISSING_LIST: True}  # the list is the problem
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

    # Register the service
    hass.services.async_register(DOMAIN, SERVICE, handle_sync_list)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:  # pylint: disable=unused-argument
    """Unload a config entry."""
    _LOGGER.debug("Unload integration")
    hass.services.async_remove(DOMAIN, SERVICE)
    del hass.data[DOMAIN]
    return True
