# tests/test_rpc.py  –  в самом верху
import pytest               # ← добавьте эту строку
import pytest_asyncio, httpx
from httpx import ASGITransport
from app.main import app


transport = ASGITransport(app=app)

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac           # <- именно yield, а не return

@pytest.mark.asyncio
async def test_add_get_duplicate(client):
    pkg = {"jsonrpc":"2.0","method":"AddContact",
           "params":{"name":"Json","phone":"+88888888"},"id":1}
    cid = (await client.post("/rpc", json=pkg)).json()["result"]["id"]

    res = await client.post("/rpc", json={
        "jsonrpc":"2.0","method":"GetByName","params":{"name":"Json"},"id":2})
    assert res.json()["result"][0]["id"] == cid

    dup = await client.post("/rpc", json=pkg)
    assert dup.json()["error"]["code"] == -32602

@pytest.mark.asyncio
async def test_update_delete_flow(client):
    add = {"jsonrpc":"2.0","method":"AddContact",
           "params":{"name":"Flow","phone":"+99999999"},"id":10}
    cid = (await client.post("/rpc", json=add)).json()["result"]["id"]

    upd = {"jsonrpc":"2.0","method":"UpdateContact",
           "params":{"id":cid,"name":"Flow","phone":"+00000000"},"id":11}
    assert (await client.post("/rpc", json=upd)).json()["result"]["phone"] == "+00000000"

    dele = {"jsonrpc":"2.0","method":"DeleteContact","params":{"id":cid},"id":12}
    assert (await client.post("/rpc", json=dele)).json()["result"] is None

    again = await client.post("/rpc", json=dele)
    assert again.json()["error"]["code"] == -32602

@pytest.mark.asyncio
async def test_unknown_method(client):
    bad = {"jsonrpc":"2.0","method":"Nope","params":{},"id":99}
    res = await client.post("/rpc", json=bad)
    assert res.json()["error"]["code"] == -32601

@pytest.mark.asyncio
async def test_add_positional_params(client):
    pkg = {
        "jsonrpc": "2.0",
        "method":  "AddContact",
        "params":  ["Positional", "+12345678", None],   # <‑ список!
        "id": 40
    }
    r = await client.post("/rpc", json=pkg)
    assert r.json()["result"]["name"] == "Positional"


@pytest.mark.asyncio
async def test_add_positional_params_again(client):
    pkg = {"jsonrpc":"2.0","method":"AddContact",
           "params":["Dup","+12345679"],"id":41}
    r = await client.post("/rpc", json=pkg)
    assert r.json()["result"]["name"] == "Dup"

@pytest.mark.asyncio
async def test_add_positional_short(client):
    pkg = {"jsonrpc":"2.0","method":"AddContact",
           "params":["Mini","+70000001"],"id":60}
    assert (await client.post("/rpc", json=pkg)).status_code == 200

@pytest.mark.asyncio
async def test_invalid_jsonrpc_version(client):
    bad = {
        "jsonrpc": "1.0",
        "method":  "AddContact",
        "params":  {"name": "X", "phone": "+12345678"},
        "id":      999
    }
    r = await client.post("/rpc", json=bad)
    data = r.json()
    assert data["error"]["code"] == -32600
    assert data["id"] is None


@pytest.mark.asyncio
async def test_get_all_contacts(client):
    # подготовим два разных контакта
    await client.post("/rpc", json={
        "jsonrpc":"2.0","method":"AddContact",
        "params":{"name":"X","phone":"+70000001"},"id":100
    })
    await client.post("/rpc", json={
        "jsonrpc":"2.0","method":"AddContact",
        "params":{"name":"Y","phone":"+70000002"},"id":101
    })

    r = await client.post("/rpc", json={
        "jsonrpc":"2.0","method":"GetAllContacts",
        "params":{}, "id":102
    })
    data = r.json()["result"]
    # data должно быть dict: {"x":[...], "y":[...]}
    assert "+70000001" in data["x"]
    assert "+70000002" in data["y"]


