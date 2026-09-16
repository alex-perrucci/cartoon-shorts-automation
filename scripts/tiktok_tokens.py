from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
from cryptography.fernet import Fernet, InvalidToken

TOKEN_ENDPOINT = "https://open.tiktokapis.com/v2/oauth/token/"


def _fernet(key: str) -> Fernet:
    key = key.strip()
    if not key:
        raise RuntimeError("TIKTOK_TOKEN_KEY is empty")
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:
        raise RuntimeError("TIKTOK_TOKEN_KEY must be a valid Fernet key") from exc


def load_encrypted(path: Path, key: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"TikTok token state not found: {path}")
    try:
        raw = _fernet(key).decrypt(path.read_bytes())
    except InvalidToken as exc:
        raise RuntimeError("could not decrypt TikTok token state; check TIKTOK_TOKEN_KEY") from exc
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or not data.get("refresh_token"):
        raise RuntimeError("TikTok token state is invalid or missing refresh_token")
    return data


def save_encrypted(path: Path, key: str, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    encrypted = _fernet(key).encrypt(payload)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(encrypted)
    tmp.replace(path)


def refresh_access_token(
    state: dict[str, Any], *, client_key: str, client_secret: str
) -> dict[str, Any]:
    response = requests.post(
        TOKEN_ENDPOINT,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": state["refresh_token"],
        },
        timeout=30,
    )
    try:
        body = response.json()
    except ValueError as exc:
        raise RuntimeError(f"TikTok token refresh returned HTTP {response.status_code} with non-JSON body") from exc
    if response.status_code >= 400 or body.get("error"):
        raise RuntimeError(
            f"TikTok token refresh failed: HTTP {response.status_code} "
            f"{body.get('error', '')} {body.get('error_description', body)}"
        )
    if not body.get("access_token") or not body.get("refresh_token"):
        raise RuntimeError(f"TikTok token refresh returned incomplete token data: {body}")
    return body
