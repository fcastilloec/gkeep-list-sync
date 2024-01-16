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
    CONF_BASE_USERNAME,
    DEFAULT_LIST_TITLE,
    MISSING_LIST
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(
    hass: HomeAssistant,
    user_input: dict[str, Any],
    reauth_entry: config_entries.ConfigEntry | None = None,
) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    config: dict[str, Any] = {}
    keep = Keep()

    try:
        if reauth_entry and reauth_entry.data.get(MISSING_LIST):
            config[CONF_USERNAME] = reauth_entry.data.get(CONF_USERNAME)
            await hass.async_add_executor_job(
                keep.resume,
                reauth_entry.data.get(CONF_USERNAME),
                reauth_entry.data.get(CONF_ACCESS_TOKEN),
            )
        elif user_input.get(CONF_ACCESS_TOKEN):
            config[CONF_USERNAME] = user_input[CONF_USERNAME]
            await hass.async_add_executor_job(
                keep.resume,
                user_input[CONF_USERNAME],
                user_input[CONF_ACCESS_TOKEN]
            )
        elif user_input.get(CONF_PASSWORD):
            config[CONF_USERNAME] = user_input[CONF_USERNAME]
            await hass.async_add_executor_job(
                keep.login,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
        else:
            _LOGGER.error("Invalid configuration provided.")
            raise InvalidConfig()
    except LoginException as ex:
        _LOGGER.error("Login error: %s ", ex)
        raise CannotLogin() from ex

    # Find note or create it
    for note in keep.all():
        if note.title == user_input[CONF_LIST_TITLE] and isinstance(note, GKeepList):
            _LOGGER.debug("Valid list found: %s", note)
            glist = note
            break
    else:
        _LOGGER.info("List '%s' not found. Creating a new list", user_input[CONF_LIST_TITLE])
        glist = keep.createList(title=user_input[CONF_LIST_TITLE])
        await hass.async_add_executor_job(keep.sync)

    config[CONF_ACCESS_TOKEN] = keep.getMasterToken()
    config[CONF_BASE_USERNAME] = config[CONF_USERNAME].partition("@")[0]
    config[CONF_LIST_ID] = glist.id
    config[CONF_LIST_TITLE] = user_input[CONF_LIST_TITLE]
    config[MISSING_LIST] = False

    return config


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Keep List Sync."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the Google Keep config flow."""
        self._username: str = None
        self._list_title: str = DEFAULT_LIST_TITLE
        self._reauth_entry: config_entries.ConfigEntry | None = None
        self._missing_list: bool = False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, Any] = {}

        # Check that the dependency is loaded
        if not self.hass.data.get(SHOPPING_LIST_DOMAIN):
            _LOGGER.error("Shopping List integration needs to be setup")
            return self.async_abort(reason="dependency_not_found")

        if user_input is not None:
            try:
                config_data = await validate_input(self.hass, user_input, self._reauth_entry)
            except CannotLogin:
                errors["base"] = "cannot_login"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

            if not errors:
                if self._reauth_entry:
                    _LOGGER.debug("Updating Config Entry because of re-authentication")
                    self.hass.config_entries.async_update_entry(self._reauth_entry, data=config_data)
                    await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

                _LOGGER.debug("Config Entry didn't exists, creating one")
                await self.async_set_unique_id(f"{config_data[CONF_BASE_USERNAME]}-{config_data[CONF_LIST_ID]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{config_data[CONF_USERNAME]} - {config_data[CONF_LIST_TITLE]}",
                    data=config_data,
                )

        return self.async_show_form(
            step_id="user", data_schema=self._async_schema(), errors=errors,
        )

    def _async_schema(self):
        """Fetch required schema with defaults."""
        if self._missing_list:
            # Schema for specifying only a new list name
            return vol.Schema(
                {
                    vol.Required(CONF_LIST_TITLE, default=self._list_title): str,
                }
            )

        # Schema for initial setup and re-authentications
        msg="A Password or Master Token is needed but not both"
        return vol.Schema(
            {
                vol.Required(CONF_USERNAME, default=self._username): str,
                vol.Exclusive(CONF_PASSWORD, 'password/token', msg=msg): str,
                vol.Exclusive(CONF_ACCESS_TOKEN, 'password/token', msg=msg): str,
                vol.Required(CONF_LIST_TITLE, default=self._list_title): str,
            }
        )

    async def async_step_reauth(self, data: Mapping[str, Any]) -> FlowResult:
        """Handle configuration by re-auth."""
        _LOGGER.debug("Re-authentication needed")
        self._username = data[CONF_USERNAME]
        self._list_title = data[CONF_LIST_TITLE]
        self._missing_list = data[MISSING_LIST]
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_user()

class CannotLogin(HomeAssistantError):
    """Error to indicate we cannot login."""

class InvalidConfig(HomeAssistantError):
    """Error to indicate the user entered invalid config"""
