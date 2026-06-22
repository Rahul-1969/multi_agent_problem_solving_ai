import json
import os
from threading import Lock
from typing import Any

from config.path_config import DATA_DIR

DEFAULT_USER_FILENAME = os.path.join(DATA_DIR, "users.json")
DEFAULT_USER_STORE = {}


class UserStore:
    def __init__(self, path: str | None = None) -> None:
        self._path = path or DEFAULT_USER_FILENAME
        self._lock = Lock()
        os.makedirs(DATA_DIR, exist_ok=True)
        self._users: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self._path):
            self._users = self._normalize_users(DEFAULT_USER_STORE)
            self._save()
            return

        try:
            with open(self._path, "r", encoding="utf-8") as file_obj:
                raw_users = json.load(file_obj)
                self._users = self._normalize_users(raw_users)
        except (json.JSONDecodeError, OSError):
            self._users = self._normalize_users(DEFAULT_USER_STORE)
            self._save()

    def _normalize_users(self, users: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        normalized_users: dict[str, dict[str, Any]] = {}
        for username, user in users.items():
            normalized_username = str(username).strip().lower()
            normalized_email = str(user.get("email", "")).strip().lower()
            normalized_users[normalized_username] = {
                "username": normalized_username,
                "name": user.get("name", "") or normalized_username,
                "email": normalized_email,
                "hashed_password": user.get("hashed_password", ""),
            }
        return normalized_users

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as file_obj:
            json.dump(self._users, file_obj, indent=2, sort_keys=True)

    def get_user(self, username: str) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        return self._users.get(normalized)

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        normalized = email.strip().lower()
        return next(
            (user for user in self._users.values() if user.get("email", "").lower() == normalized),
            None,
        )

    def create_user(self, username: str, name: str, email: str, hashed_password: str) -> dict[str, Any]:
        user = {
            "username": username,
            "name": name,
            "email": email,
            "hashed_password": hashed_password,
        }
        with self._lock:
            self._users[username] = user
            self._save()
        return user

    def username_exists(self, username: str) -> bool:
        return username in self._users

    def email_exists(self, email: str) -> bool:
        return self.get_user_by_email(email) is not None


user_store = UserStore()
