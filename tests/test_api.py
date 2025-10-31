import uuid

import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from src.app import app


@pytest.mark.asyncio
async def test_get_activities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/activities")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)
        # basic sanity: known activity exists
        assert "Chess Club" in data


@pytest.mark.asyncio
async def test_signup_and_unregister():
    activity_name = "Chess Club"
    # unique email per test run
    email = f"test-{uuid.uuid4().hex}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # ensure the email is not already present
        r = await ac.get("/activities")
        assert r.status_code == 200
        participants_before = r.json()[activity_name]["participants"]
        assert email not in participants_before

        # sign up
        r = await ac.post(f"/activities/{activity_name}/signup?email={email}")
        assert r.status_code == 200
        assert "Signed up" in r.json()["message"]

        # verify presence
        r = await ac.get("/activities")
        participants_after = r.json()[activity_name]["participants"]
        assert email in participants_after

        # unregister
        r = await ac.delete(f"/activities/{activity_name}/participants?email={email}")
        assert r.status_code == 200
        assert "Unregistered" in r.json()["message"]

        # final verify - removed
        r = await ac.get("/activities")
        participants_final = r.json()[activity_name]["participants"]
        assert email not in participants_final
