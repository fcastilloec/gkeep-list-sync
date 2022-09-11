#!/usr/bin/env python3
"""Sync Home Assistant shopping list"""

from datetime import datetime
from os import path
from uuid import uuid4
import json


class ShoppingList:
    """Analogous to GKeep node.List."""

    __TIMEOUT = 0.5

    def __init__(self, list_path: str, api_url: str) -> None:
        self.__list_path = list_path
        self.__api_url = api_url  # pylint: disable=unused-private-member
        self.___load()

    def ___load(self) -> None:
        """Load items and last updated time."""
        self._updated = datetime.utcfromtimestamp(path.getmtime(self.__list_path))
        self._items = self.__read_list()

    def __read_list(self) -> "list":
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
        self._items.append({"name": text, "id": uuid4().hex, "complete": False})
        with open(self.__list_path, "wt", encoding="utf8") as file:
            file.write(json.dumps(self._items, indent=2))
        self.___load()  # reloads items

    def delete_all(self, checked_only: bool = False) -> None:
        """Deletes all items."""
        if not checked_only:
            with open(self.__list_path, "wt", encoding="utf8") as file:
                file.write(json.dumps([], indent=2))
        else:
            new_items = [item for item in self._items if not item["complete"]]
            with open(self.__list_path, "wt", encoding="utf8") as file:
                file.write(json.dumps(new_items, indent=2))
        self.___load()  # reloads items
