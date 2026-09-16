# Social auth state

TikTok refresh tokens can rotate. The production workflow therefore stores TikTok's token bundle only as an encrypted Fernet payload at `.auth/tiktok_tokens.enc`.

- The encryption key lives only in the GitHub Actions secret `TIKTOK_TOKEN_KEY`.
- Plain JSON token files are ignored by git and must never be committed.
- `scripts/oauth_tiktok.py` performs the one-time Desktop OAuth flow and writes the encrypted state file.
- `scripts/upload_tiktok_draft.py` decrypts the state, refreshes the access token, replaces a rotated refresh token, re-encrypts the state, and uploads the rendered video to TikTok's inbox/draft flow.
- GitHub Actions commits only the encrypted state if TikTok rotated it.

Do not paste access tokens, refresh tokens, client secrets, or the Fernet key into repository files or logs.
