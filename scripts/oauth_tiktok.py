from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

from tiktok_tokens import save_encrypted

AUTHORIZE_ENDPOINT = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_ENDPOINT = "https://open.tiktokapis.com/v2/oauth/token/"


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="One-time TikTok Desktop OAuth bootstrap.")
    parser.add_argument("--port", type=int, default=3455)
    parser.add_argument("--output", type=Path, default=Path(".auth/tiktok_tokens.enc"))
    parser.add_argument("--scope", default="video.upload")
    args = parser.parse_args()

    client_key = _env("TIKTOK_CLIENT_KEY")
    client_secret = _env("TIKTOK_CLIENT_SECRET")
    token_key = _env("TIKTOK_TOKEN_KEY")
    redirect_uri = f"http://127.0.0.1:{args.port}/callback/"

    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)[:96]
    # TikTok Desktop Login Kit documents the S256 challenge as hex SHA-256.
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).hexdigest()
    result: dict[str, str] = {}
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args: object) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback/":
                self.send_response(404)
                self.end_headers()
                return
            query = urllib.parse.parse_qs(parsed.query)
            result["code"] = query.get("code", [""])[0]
            result["state"] = query.get("state", [""])[0]
            result["error"] = query.get("error", [""])[0]
            result["error_description"] = query.get("error_description", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>TikTok authorization received.</h2>"
                b"<p>You can close this tab and return to the terminal.</p></body></html>"
            )
            done.set()

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    params = {
        "client_key": client_key,
        "response_type": "code",
        "scope": args.scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "disable_auto_auth": "1",
    }
    auth_url = AUTHORIZE_ENDPOINT + "?" + urllib.parse.urlencode(params)
    print(f"Opening TikTok authorization in your browser. Redirect URI: {redirect_uri}")
    print(auth_url)
    webbrowser.open(auth_url)

    if not done.wait(timeout=300):
        server.shutdown()
        raise RuntimeError("TikTok authorization timed out after 5 minutes")
    server.shutdown()

    if result.get("state") != state:
        raise RuntimeError("TikTok OAuth state mismatch")
    if result.get("error"):
        raise RuntimeError(
            f"TikTok authorization failed: {result.get('error')} {result.get('error_description', '')}"
        )
    code = result.get("code", "")
    if not code:
        raise RuntimeError("TikTok callback did not contain an authorization code")

    response = requests.post(
        TOKEN_ENDPOINT,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        },
        timeout=30,
    )
    body = response.json()
    if response.status_code >= 400 or body.get("error"):
        raise RuntimeError(
            f"TikTok token exchange failed: HTTP {response.status_code} "
            f"{body.get('error', '')} {body.get('error_description', body)}"
        )
    if not body.get("access_token") or not body.get("refresh_token"):
        raise RuntimeError("TikTok token exchange returned incomplete token data")

    save_encrypted(args.output, token_key, body)
    print(f"Encrypted TikTok token state written to {args.output}")
    print(f"Authorized scopes: {body.get('scope', '')}")
    print("No access or refresh token was printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
