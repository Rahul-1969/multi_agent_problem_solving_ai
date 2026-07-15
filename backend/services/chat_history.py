"""
backend/services/chat_history.py
Persistent chat history store for authenticated users (JSON-backed).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from config.path_config import DATA_DIR


DEFAULT_CHAT_TITLE = "New chat"


_CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")


class ChatHistoryManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._store: dict[str, dict[str, dict[str, Any]]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(_CHAT_HISTORY_FILE):
                with open(_CHAT_HISTORY_FILE, "r", encoding="utf-8") as fh:
                    self._store = json.load(fh)
        except (json.JSONDecodeError, OSError):
            self._store = {}

    def _persist(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)

            with open(_CHAT_HISTORY_FILE, "w", encoding="utf-8") as fh:
                json.dump(
                    self._store,
                    fh,
                    ensure_ascii=False,
                    indent=2,
                    default=lambda o:
                        o.model_dump()
                        if hasattr(o, "model_dump")
                        else (
                            o.dict()
                            if hasattr(o, "dict")
                            else str(o)
                        )
                )
        except OSError:
            pass

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _user_chats(self, username: str) -> dict[str, dict[str, Any]]:
        return self._store.setdefault(username, {})

    def _copy_message(self, message: dict[str, Any]) -> dict[str, Any]:
        return {
            "sender": message.get("sender"),
            "content": message.get("content"),
            "domain": message.get("domain"),
            "data": message.get("data"),
            "created_at": message.get("created_at"),
        }

    def _copy_chat(self, chat: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": chat["id"],
            "title": chat["title"],
            "created_at": chat["created_at"],
            "updated_at": chat["updated_at"],
            "last_message": chat.get("last_message"),
            "messages": [self._copy_message(message) for message in chat.get("messages", [])],
        }

    def list_chats(self, username: str) -> list[dict[str, Any]]:
        chats = list(self._user_chats(username).values())
        chats.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
        return [
            {
                "id": chat["id"],
                "title": chat["title"],
                "created_at": chat["created_at"],
                "updated_at": chat["updated_at"],
                "last_message": chat.get("last_message"),
            }
            for chat in chats
        ]

    def create_chat(self, username: str, title: str | None = None) -> dict[str, Any]:
        now = self._now_iso()
        chat_id = str(uuid4())
        chat = {
            "id": chat_id,
            "title": title.strip() if title and title.strip() else DEFAULT_CHAT_TITLE,
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "last_message": None,
        }
        with self._lock:
            self._user_chats(username)[chat_id] = chat
            self._persist()
        return self._copy_chat(chat)

    def get_chat(self, username: str, chat_id: str) -> dict[str, Any] | None:
        chat = self._user_chats(username).get(chat_id)
        return self._copy_chat(chat) if chat else None

    def update_title(self, username: str, chat_id: str, title: str) -> None:
        with self._lock:
            chat = self._user_chats(username).get(chat_id)
            if chat:
                chat["title"] = title
                self._persist()

    def delete_chat(self, username: str, chat_id: str) -> bool:
        with self._lock:
            chats = self._user_chats(username)
            if chat_id in chats:
                chats.pop(chat_id)
                self._persist()
                return True
        return False

    def append_message(
        self,
        username: str,
        chat_id: str,
        message: dict[str, Any]
    ) -> dict[str, Any] | None:

        with self._lock:
            chats = self._user_chats(username)
            chat = chats.get(chat_id)

            if chat is None:
                return None

            data = message.get("data")

            if hasattr(data, "model_dump"):
                data = data.model_dump()
            elif hasattr(data, "dict"):
                data = data.dict()

            entry = {
                "sender": message.get("sender"),
                "content": message.get("content"),
                "domain": message.get("domain"),
                "data": data,
                "created_at": message.get("created_at") or self._now_iso(),
            }

            chat["messages"].append(entry)
            chat["updated_at"] = self._now_iso()

            if entry["content"]:
                chat["last_message"] = entry["content"]

            self._persist()

            return self._copy_chat(chat)


chat_history_manager = ChatHistoryManager()
