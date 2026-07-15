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
                "profile": user.get("profile", {}),
                "saved_colleges": user.get("saved_colleges", []),
                "career_plans": user.get("career_plans", []),
                "scholarship_bookmarks": user.get("scholarship_bookmarks", []),
                "resume_matches": user.get("resume_matches", []),
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
            "profile": {},
            "saved_colleges": [],
            "career_plans": [],
            "scholarship_bookmarks": [],
            "resume_matches": [],
        }
        with self._lock:
            self._users[username] = user
            self._save()
        return user

    def username_exists(self, username: str) -> bool:
        return username in self._users

    def email_exists(self, email: str) -> bool:
        return self.get_user_by_email(email) is not None

    def update_profile(self, username: str, profile_data: dict[str, Any]) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        with self._lock:
            if normalized in self._users:
                self._users[normalized]["profile"] = profile_data
                self._save()
                return self._users[normalized]
        return None

    def update_saved_colleges(self, username: str, saved_colleges: list[dict[str, Any]]) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        with self._lock:
            if normalized in self._users:
                self._users[normalized]["saved_colleges"] = saved_colleges
                self._save()
                return self._users[normalized]
        return None

    def update_career_plans(self, username: str, career_plans: list[dict[str, Any]]) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        with self._lock:
            if normalized in self._users:
                self._users[normalized]["career_plans"] = career_plans
                self._save()
                return self._users[normalized]
        return None

    def update_scholarship_bookmarks(self, username: str, scholarship_bookmarks: list[dict[str, Any]]) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        with self._lock:
            if normalized in self._users:
                self._users[normalized]["scholarship_bookmarks"] = scholarship_bookmarks
                self._save()
                return self._users[normalized]
        return None

    def update_resume_matches(self, username: str, resume_matches: list[dict[str, Any]]) -> dict[str, Any] | None:
        normalized = str(username).strip().lower()
        with self._lock:
            if normalized in self._users:
                self._users[normalized]["resume_matches"] = resume_matches
                self._save()
                return self._users[normalized]
        return None

    def list_users(self) -> list[dict[str, Any]]:
        """
        Returns a list of users with non-sensitive fields only.
        """
        with self._lock:
            users = []
            for username, data in self._users.items():
                users.append({
                    "username": username,
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "career_plans_count": len(data.get("career_plans", [])),
                    "saved_colleges_count": len(data.get("saved_colleges", [])),
                })
            return users

user_store = UserStore()
