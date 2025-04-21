from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Optional, List, Dict, Set

from pydantic import BaseModel, Field, EmailStr, constr

logger = logging.getLogger("phonebook")


class Contact(BaseModel):

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    phone: constr(regex=r"^\+\d{7,15}$")
    email: Optional[EmailStr] = None


class PhoneBook:

    def __init__(self) -> None:
        self._by_id: Dict[str, Contact] = {}
        self._by_name: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()
        logger.info("PhoneBook initialised (in‑memory)")

    async def add(self, name: str, phone: str, email: Optional[str] = None) -> Contact:
        contact = Contact(name=name, phone=phone, email=email)
        async with self._lock:
            # duplicate check — same name & phone
            for cid in self._by_name.get(name.lower(), set()):
                if self._by_id[cid].phone == phone:
                    logger.warning("AddContact refused: duplicate %s / %s", name, phone)
                    raise ValueError("Contact already exists")
            self._by_id[contact.id] = contact
            self._by_name.setdefault(contact.name.lower(), set()).add(contact.id)
            logger.info("AddContact: %s", contact.dict())
        return contact

    async def get_by_name(self, name: str) -> List[Contact]:
        async with self._lock:
            ids = self._by_name.get(name.lower(), set())
            contacts = [self._by_id[i] for i in ids]
            logger.debug("GetByName '%s' -> %d records", name, len(contacts))
            return contacts

    async def update(self, id: str, name: str, phone: str, email: Optional[str] = None) -> Contact:
        async with self._lock:
            if id not in self._by_id:
                logger.error("UpdateContact: id %s not found", id)
                raise KeyError("Contact not found")
            # duplicate check against other ids
            for cid in self._by_name.get(name.lower(), set()):
                if cid != id and self._by_id[cid].phone == phone:
                    logger.warning("UpdateContact duplicate for id %s -> %s/%s", id, name, phone)
                    raise ValueError("Contact already exists")

            old = self._by_id[id]
            if old.name.lower() != name.lower():
                self._by_name[old.name.lower()].remove(id)
                self._by_name.setdefault(name.lower(), set()).add(id)
            updated = Contact(id=id, name=name, phone=phone, email=email)
            self._by_id[id] = updated
            logger.info("UpdateContact %s -> %s", id, updated.dict())
            return updated

    async def delete(self, id: str) -> None:
        async with self._lock:
            contact = self._by_id.pop(id, None)
            if contact is None:
                logger.error("DeleteContact: id %s not found", id)
                raise KeyError("Contact not found")
            self._by_name[contact.name.lower()].remove(id)
            logger.info("DeleteContact %s (%s)", id, contact.name)


phonebook = PhoneBook()