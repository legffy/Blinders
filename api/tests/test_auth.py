from __future__ import annotations

from typing import Any

import uuid
import pytest
from httpx import AsyncClient


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex}@example.com"


@pytest.mark.asyncio
async def test_signup_ok(client: AsyncClient) -> None:
    email: str = unique_email("signup")
    res = await client.post("/auth/signup", json={"email": email, "password": "password123"})
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_login_sets_cookies(client: AsyncClient) -> None:
    email: str = unique_email("login")
    await client.post("/auth/signup", json={"email": email, "password": "password123"})

    res = await client.post("/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200

    set_cookie: list[str] = res.headers.get_list("set-cookie")
    joined: str = " | ".join(set_cookie)

    assert "access_token=" in joined
    assert "refresh_token=" in joined


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    res = await client.get("/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_works_after_login(client: AsyncClient) -> None:
    await client.post("/auth/signup", json={"email": "me_user@example.com", "password": "password123"})
    await client.post("/auth/login", json={"email": "me_user@example.com", "password": "password123"})

    # same client => cookies persist
    res = await client.get("/auth/me")
    assert res.status_code == 200

    data: dict[str, Any] = res.json()
    assert data["email"] == "me_user@example.com"
