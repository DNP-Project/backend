## Phonebook JSON‑RPC Service

A tiny yet **fully‑tested (100% coverage)** phonebook micro‑service that exposes an **in‑memory** phonebook over a single **JSON‑RPC 2.0** endpoint.  
Built with **FastAPI & Pydantic v2** and fewer than 100 SLOC of business code.

---

### Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://127.0.0.1:5000
```

*All logs go to console **and** `app.log`*

---

### File layout

```
app/
├── PhoneBook.py      # Contact model + thread‑safe in‑mem store
├── router.py         # JSON‑RPC dispatcher on /rpc
└── main.py           # FastAPI app factory, logging, middleware
tests/
├── test_phonebook.py # unit tests
└── test_rpc.py       # end‑to‑end JSON‑RPC tests (httpx + ASGITransport)
```

---

### JSON‑RPC API


| Method             | Params                                              | Result / Error                  |
|--------------------|-----------------------------------------------------|---------------------------------|
| **AddContact**     | `name:str`, `phone:str`, `email:str\|null`         | `Contact`                       |
| **GetByName**      | `name:str`                                          | `Contact[]`                     |
| **GetAllContacts** | _none_                                              | `Dict[str, List[str]]`          |
| **UpdateContact**  | `id:str`, `name:str`, `phone:str`, `email:str\|null` | `Contact`                       |
| **DeleteContact**  | `id:str`                                            | `null`                          |

> *All phone numbers must match E.164: `+` and 7–15 digits.*  
> Duplicate (`name + phone`) raises `"code":‑32602`.

#### Request Examples

**1. AddContact**
```json
{
  "jsonrpc": "2.0",
  "method": "AddContact",
  "params": {
    "name":  "Alice",
    "phone": "+491234567",
    "email": "alice@mail.com"
  },
  "id": 1
}
```

**2. GetByName**
```json
{
  "jsonrpc": "2.0",
  "method": "GetByName",
  "params": {
    "name": "Alice"
  },
  "id": 2
}
```

**3. UpdateContact**
```json
{
  "jsonrpc": "2.0",
  "method": "UpdateContact",
  "params": {
    "id":    "<CONTACT_ID>",
    "name":  "Alice",
    "phone": "+491234800",
    "email": "alice@mail.com"
  },
  "id": 3
}
```

**4. DeleteContact**
```json
{
  "jsonrpc": "2.0",
  "method": "DeleteContact",
  "params": {
    "id": "<CONTACT_ID>"
  },
  "id": 4
}
```

**5. Get all contacts:**
```json
{
  "jsonrpc":"2.0",
  "method":"GetAllContacts",
  "params":{},
  "id":5
}
```

---

### Running the tests

```bash
pytest                                  # 13 green tests
pytest --cov=app --cov-report=term-missing
```

```
Name               Stmts   Miss  Cover   
---------------------------------------
app\PhoneBook.py      61      0   100%
app\__init__.py        0      0   100%
app\main.py           18      0   100%
app\router.py         46      0   100%
---------------------------------------
TOTAL                125      0   100%

```

*pytest‑asyncio strict‑mode; race‑conditions checked with 50 parallel `add`.*

---

### Requirements

* Python 3.10+  
* FastAPI 0.109, Pydantic 2.x, httpx 0.27, pytest 8.x

```
pip install -r requirements.txt
```

---

