#!/usr/bin/env python3
"""Sync Home Assistant shopping list"""

from enum import Enum
import requests

__TIMEOUT = 0.5


class Actions(Enum):
    """Valid action types."""

    ADD = "shopping_list.add_item"
    COMPLETE = "shopping_list.complete_item"
    INCOMPLETE = "shopping_list.incomplete_item"
    COMPLETE_ALL = "shopping_list.complete_all"
    CLEAR_COMPLETED = "shopping_list.clear_completed_items"


def add(api_url: str, text: str) -> None:
    """Add a new item to the list."""
    body = {"service": Actions.ADD.value, "name": text}
    requests.post(api_url, json=body, timeout=__TIMEOUT)
