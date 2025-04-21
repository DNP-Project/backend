import asyncio
import pytest
from app.PhoneBook import PhoneBook, Contact

@pytest.fixture
def pb():
    return PhoneBook()

@pytest.mark.asyncio
async def test_add_and_get(pb):
    c = await pb.add("Alice", "+11111111", "a@a.a")
    assert isinstance(c, Contact)
    assert (await pb.get_by_name("Alice")) == [c]

@pytest.mark.asyncio
async def test_duplicate_add(pb):
    await pb.add("Bob", "+22222222")
    with pytest.raises(ValueError):
        await pb.add("Bob", "+22222222")

@pytest.mark.asyncio
async def test_update_success(pb):
    c = await pb.add("Tom", "+33333333")
    updated = await pb.update(c.id, "Tom", "+99999999")
    assert updated.phone == "+99999999"

@pytest.mark.asyncio
async def test_update_conflict(pb):
    await pb.add("Ann", "+44444444")
    b = await pb.add("Ann", "+55555555")
    with pytest.raises(ValueError):
        await pb.update(b.id, "Ann", "+44444444")

@pytest.mark.asyncio
async def test_delete(pb):
    c = await pb.add("Del", "+66666666")
    await pb.delete(c.id)
    assert await pb.get_by_name("Del") == []
    with pytest.raises(KeyError):
        await pb.delete(c.id)

@pytest.mark.asyncio
async def test_concurrent(pb):
    async def _add(i):
        return await pb.add(f"N{i}", f"+77{i:05}")
    contacts = await asyncio.gather(*[_add(i) for i in range(50)])
    assert len(contacts) == 50

@pytest.mark.asyncio
async def test_get_empty(pb):
    assert await pb.get_by_name("Ghost") == []


@pytest.mark.asyncio
async def test_update_rename(pb):
    c = await pb.add("Old", "+77777777")
    renamed = await pb.update(c.id, "New", "+77777777")
    assert await pb.get_by_name("Old") == []
    assert await pb.get_by_name("New") == [renamed]


@pytest.mark.asyncio
async def test_get_empty_again(pb):
    await pb.add("Someone", "+12345000")
    assert await pb.get_by_name("Nobody") == []

@pytest.mark.asyncio
async def test_update_not_found(pb):
    with pytest.raises(KeyError) as ei:
        await pb.update("00000000-0000-0000-0000-000000000000", "NoName", "+12345678")
    assert "Contact not found" in str(ei.value)


