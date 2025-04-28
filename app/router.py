from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Request

from app.PhoneBook import phonebook, Contact  # noqa: E402

router = APIRouter()
log = logging.getLogger("rpc")


async def _json_success(result: Any, id_: Optional[str]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": id_}


AUTHORISATION_ERROR_CODES = {
    KeyError:   (-32602, "Not found"),
    ValueError: (-32602, None),
}


@router.post("")
async def rpc_entrypoint(request: Request) -> Dict[str, Any]:

    payload: Dict[str, Any] = await request.json()
    log.debug("<= %s", payload)

    if payload.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON‑RPC version"}, "id": None}

    method: str = payload.get("method", "")
    params: Dict[str, Any] | List[Any] | None = payload.get("params", {})
    id_: Optional[str] = payload.get("id", str(uuid.uuid4()))

    try:
        if isinstance(params, list):
            if method == "AddContact":
                name, phone, *rest = params  # type: ignore[misc]
                email = rest[0] if rest else None
                params = {"name": name, "phone": phone, "email": email}

        if method == "AddContact":
            contact = await phonebook.add(**params)
            resp = await _json_success(contact.dict(), id_)

        elif method == "GetByName":
            contacts = await phonebook.get_by_name(params["name"])
            resp = await _json_success([c.dict() for c in contacts], id_)

        elif method == "UpdateContact":
            contact = await phonebook.update(**params)
            resp = await _json_success(contact.dict(), id_)

        elif method == "DeleteContact":
            await phonebook.delete(params["id"])
            resp = await _json_success(None, id_)

        elif method == "GetAllContacts":
            all_contacts = await phonebook.get_all()
            resp = await _json_success(all_contacts, id_)

        else:
            resp = {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method {method!r}"}, "id": id_}

        log.debug("=> %s", resp)
        return resp

    except Exception as exc:
        code, default_msg = AUTHORISATION_ERROR_CODES.get(type(exc), (-32000, None))
        message = default_msg if default_msg is not None else str(exc)
        resp = {
                "jsonrpc": "2.0",
                "error": {"code": code, "message": message},
                "id": id_,
        }
        log.warning("! %s -> %s", method, message)
        return resp