#!/usr/bin/env python3
"""Gets the configuration from a file."""

from os import geteuid, environ, path
from sys import stderr, platform, path as __dirname
from datetime import datetime
from pydantic import BaseModel, AnyHttpUrl, FilePath, EmailStr

PKG_NAME = "gkeep-shopping"
CONFIG_NAME = "config.json"
UPDATED_NAME = "last_updated.json"


class Config(BaseModel):
    """Configuration object."""

    email: EmailStr
    password: str
    webhook: AnyHttpUrl
    noteID: str
    listPath: FilePath


class Updated(BaseModel):
    """Updated object."""

    google_keep: datetime
    home_assistant: datetime


def __get_config_dir() -> str:
    """Gets the config directory."""

    if geteuid() == 0 and not environ.get("CONFIG_DIR"):
        print("Need a configuration directory path when running as root", file=stderr)
        raise Exception("Need a configuration directory path when running as root")

    if environ.get("CONFIG_DIR"):
        if not path.exists(environ.get("CONFIG_DIR")):
            print("Configuration directory does not exist", file=stderr)
            raise Exception("Configuration directory does not exist")

        return environ.get("CONFIG_DIR")

    if environ.get("PYTHON_ENV") == "development":
        return path.join(__dirname[0], "config")

    if platform in ("linux", "darwin"):
        _dir = (
            path.join(environ.get("XDG_CONFIG_HOME"), PKG_NAME)
            if environ.get("XDG_CONFIG_HOME")
            else path.join(environ.get("HOME"), ".config", PKG_NAME)
        )
    elif platform == "win32":
        _dir = path.join(environ.get("APPDATA"), PKG_NAME)
    else:
        raise Exception("Platform not supported.")

    return _dir


def get_config() -> dict:
    """Get the configuration object."""
    config_path = path.join(__get_config_dir(), CONFIG_NAME)
    return Config.parse_file(config_path)


def get_updated() -> dict:
    """Get the last updated form."""
    config_path = path.join(__get_config_dir(), UPDATED_NAME)
    try:
        return Updated.parse_file(config_path)
    except FileNotFoundError:
        return Updated(google_keep=0, home_assistant=0)


def save_updated(google_keep: datetime, home_assistant: datetime) -> None:
    """Save the updated object."""
    with open(path.join(__get_config_dir(), UPDATED_NAME), "wt", encoding="utf8") as file:
        file.write(Updated(google_keep=google_keep, home_assistant=home_assistant).json())
