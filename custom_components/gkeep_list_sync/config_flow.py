"""Config flow for Google Keep List Sync integration."""
from __future__ import annotations

import logging
from typing import Any
from collections.abc import Mapping

import voluptuous as vol
from gkeepapi import Keep
from gkeepapi.exception import LoginException
from gkeepapi.node import List as GKeepList

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError


from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PASSWORD,
    CONF_USERNAME,
)

from .const import (
    DOMAIN,
    SHOPPING_LIST_DOMAIN,
    CONF_LIST_TITLE,
    CONF_LIST_ID,
    DEFAULT_LIST_TITLE,
    MISSING_LIST,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    config = {}
    keep = Keep()

    try:
        if len(data) == 1:
            # Get previous saved data
            config_entry = hass.config_entries.async_entries(DOMAIN)[0]
            config[CONF_USERNAME] = config_entry.data.get(CONF_USERNAME)
            await hass.async_add_executor_job(
                keep.resume,
                config_entry.data.get(CONF_USERNAME),
                config_entry.data.get(CONF_ACCESS_TOKEN),
            )
        else:
            config[CONF_USERNAME] = data[CONF_USERNAME]
            await hass.async_add_executor_job(
                keep.login,
                data[CONF_USERNAME],
                data[CONF_PASSWORD],
            )
    except LoginException as ex:
        _LOGGER.error("Login error: %s ", ex)
        raise CannotLogin() from ex

    # Find note or create it
    for note in keep.all():
        if note.title == data[CONF_LIST_TITLE] and isinstance(note, GKeepList):
            _LOGGER.debug("Valid list found: %s", note)
            glist = note
            break
    else:
        _LOGGER.debug("List '%s' not found. Creating a new list", data[CONF_LIST_TITLE])
        glist = keep.createList(title=data[CONF_LIST_TITLE])
        await hass.async_add_executor_job(keep.sync)

    config[CONF_ACCESS_TOKEN] = keep.getMasterToken()
    config[CONF_LIST_ID] = glist.id
    config[CONF_LIST_TITLE] = data[CONF_LIST_TITLE]
    config[MISSING_LIST] = False

    return config


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Keep List Sync."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the Google Keep config flow."""
        self.username = None
        self.list_title = DEFAULT_LIST_TITLE
        self.reauth = False
        self.missing_list = False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        # Check that the dependency is loaded
        if not self.hass.data.get(SHOPPING_LIST_DOMAIN):
            _LOGGER.error("Shopping List integration needs to be setup")
            return self.async_abort(reason="dependency_not_found")

        # Get any current configuration entries
        if self._async_current_entries():
            config_entry = self._async_current_entries()[0]
        else:
            config_entry = None

        # Check that single instance of the config is allowed
        if config_entry and not self.reauth:
            return self.async_abort(reason="single_instance_allowed")

        # Schema for initial setup of loging re-auth
        all_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self.username,
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                ): str,
                vol.Required(
                    CONF_LIST_TITLE,
                    default=self.list_title,
                ): str,
            }
        )

        # Schema for List name re-auth
        list_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LIST_TITLE,
                    default=self.list_title,
                ): str,
            }
        )

        if user_input is None:
            if self.missing_list:
                errors["list_title"] = "list_not_found"
                return self.async_show_form(
                    step_id="user",
                    data_schema=list_schema,
                    errors=errors,
                )
            return self.async_show_form(
                step_id="user",
                data_schema=all_schema,
                errors=errors,
            )

        try:
            info = await validate_input(self.hass, user_input)
        except CannotLogin:
            errors["base"] = "cannot_login"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            if config_entry:
                self.hass.config_entries.async_update_entry(config_entry, data=info)
                await self.hass.config_entries.async_reload(config_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            return self.async_create_entry(title=info[CONF_USERNAME], data=info)

    async def async_step_reauth(self, data: Mapping[str, Any]) -> FlowResult:
        """Handle configuration by re-auth."""

        _LOGGER.debug("Re-authentication needed")
        self.username = data[CONF_USERNAME]
        self.list_title = data[CONF_LIST_TITLE]
        self.reauth = True
        self.missing_list = self.hass.data[DOMAIN][MISSING_LIST]
        return await self.async_step_user()


class CannotLogin(HomeAssistantError):
    """Error to indicate we cannot login."""
