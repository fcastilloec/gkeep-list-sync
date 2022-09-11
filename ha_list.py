#!/usr/bin/env python3
"""Sync Home Assistant shopping list"""

from datetime import datetime
from enum import Enum
from os import path
import json
import requests


class Actions(Enum):
    """Valid action types."""

    ADD = "shopping_list.add_item"
    COMPLETE = "shopping_list.complete_item"
    INCOMPLETE = "shopping_list.incomplete_item"
    COMPLETE_ALL = "shopping_list.complete_all"
    CLEAR_COMPLETED = "shopping_list.clear_completed_items"


class ShoppingList:
    """Analogous to GKeep node.List."""

    __TIMEOUT = 0.5

    def __init__(self, list_path, api_url):
        self.__list_path = list_path
        self.__api_url = api_url
        self.___load()

    def ___load(self):
        """Load items and last updated time."""
        self._updated = datetime.fromtimestamp(path.getmtime(self.__list_path))
        self._items = self.__read_list()

    def __read_list(self):
        """Read shopping list from file."""
        with open(self.__list_path, "rt", encoding="utf8") as file:
            shopping_list = json.load(file)
            return shopping_list

    @property
    def updated(self) -> datetime:
        """Get the updated datetime."""
        return self._updated

    @property
    def items(self) -> "list[dict]":
        """Get all list-items."""
        return [{"text": item["name"], "checked": item["complete"]} for item in self._items]

    @property
    def text(self) -> str:
        """Get a single string of all items and checked status."""

        def box(item):
            return f"☑ {item['name']}" if item["complete"] else f"☐ {item['name']}"

        return "\n".join([box(item) for item in self._items])

    @property
    def checked(self) -> "list[str]":
        """Get all checked list-items."""
        return [item["name"] for item in self._items if item["complete"]]

    @property
    def unchecked(self) -> "list[str]":
        """Get all unchecked list-items."""
        return [item["name"] for item in self._items if not item["complete"]]

    def add(self, text: str) -> None:
        """Add a new item to the list."""
        body = {"service": Actions.ADD.value, "name": text}
        requests.post(self.__api_url, json=body, timeout=self.__TIMEOUT)
        self.___load()  # reloads items

    def delete_all(self, checked_only: bool = False) -> None:
        """Deletes all items."""
        if not checked_only:
            # First we mark all items as completed.
            body = {"service": Actions.COMPLETE_ALL.value, "name": ""}
            requests.post(self.__api_url, json=body, timeout=self.__TIMEOUT)

        # Then we clear all completed items.
        body = {"service": Actions.CLEAR_COMPLETED.value, "name": ""}
        requests.post(self.__api_url, json=body, timeout=self.__TIMEOUT)
        self.___load()  # reloads items
