# OAuth setup for social drafts

The production workflow uploads successful renders to:

- **YouTube** as a private video with title, description, hashtags and tags already populated.
- **TikTok** through the official `video.upload` Content Posting API, which delivers the video to the creator inbox/draft flow for final editing and posting.

Telegram is used only for pipeline failures once social uploads are configured.

## 1. YouTube OAuth

### Google Cloud setup

1. Create or select a Google Cloud project.
2. Enable **YouTube Data API v3**.
3. Configure the OAuth consent screen.
4. Create an OAuth client of type **Desktop app**.
5. Download the client JSON locally. Do **not** commit it.
6. For long-lived automation, move the OAuth app to **In production**. External apps left in `Testing` receive refresh tokens that normally expire after 7 days when using the YouTube upload scope.

### Obtain the refresh token

From a local clone of this repository:

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/oauth_youtube.py --client-secrets "C:\path\to\client_secret.json"
```

Authorize the Google/YouTube account that owns the **Ti Fregano Così** channel. The helper prints three values. Add each one under GitHub **Settings -> Secrets and variables -> Actions -> New repository secret**:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

The workflow requests only the `youtube.upload` scope and uploads with `privacyStatus=private`.

## 2. TikTok OAuth

TikTok's draft upload uses the official Content Posting API and the `video.upload` scope.

### TikTok Developer setup

1. Sign in to TikTok for Developers and create an app.
2. Add **Login Kit**.
3. Add **Content Posting API**.
4. Configure the app for **Desktop**.
5. Register this redirect URI in Login Kit:

```text
http://127.0.0.1:3455/callback/
```

   TikTok Desktop Login Kit also allows a wildcard loopback port, but the helper intentionally uses fixed port `3455` to make setup deterministic.
6. Request/obtain approval for the `video.upload` scope. The TikTok account must then authorize that scope.
7. Copy the app's **Client Key** and **Client Secret**, but do not commit either value.

### Generate the encryption key

TikTok refresh tokens may rotate. The repository therefore persists TikTok's token bundle only as encrypted ciphertext.

Generate a Fernet key locally:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add these three GitHub Actions secrets:

- `TIKTOK_CLIENT_KEY`
- `TIKTOK_CLIENT_SECRET`
- `TIKTOK_TOKEN_KEY` (the Fernet key generated above)

For the one-time local OAuth bootstrap, set the same values in your terminal environment. Example for PowerShell:

```powershell
$env:TIKTOK_CLIENT_KEY="..."
$env:TIKTOK_CLIENT_SECRET="..."
$env:TIKTOK_TOKEN_KEY="..."
python scripts/oauth_tiktok.py
```

A browser opens. Authorize the **@tifregano_cosi** account. The helper receives the callback locally, exchanges the code, and writes:

```text
.auth/tiktok_tokens.enc
```

Only this encrypted file may be committed. The plain access/refresh tokens are never printed by the helper.

Commit and push the encrypted state once:

```bash
git add .auth/tiktok_tokens.enc
git commit -m "chore: seed encrypted TikTok OAuth state"
git push
```

On subsequent production runs, GitHub Actions decrypts the state with `TIKTOK_TOKEN_KEY`, refreshes the access token, replaces a rotated refresh token if TikTok returns one, encrypts the new state again, and commits only the ciphertext.

## 3. TikTok draft metadata limitation

The TikTok **video upload/draft** endpoint accepts the video but does not accept the video's caption/hashtags in the upload payload. The scheduler still generates `tiktok.caption` and `tiktok.hashtags` in the manifest so they are ready for the final editing step inside TikTok.

TikTok **Direct Post** (`video.publish`) can carry caption and hashtags, but it is intentionally not used by this repository. TikTok's current Direct Post guidelines require a creator-facing publishing UX with explicit per-post consent, editable metadata/privacy controls, and creator information. They also state that a utility limited to uploading content to accounts managed by the developer/team is not an acceptable Direct Post use case. Unaudited clients are additionally restricted to private (`SELF_ONLY`) posts. Enabling Direct Post in the Developer Portal therefore does not change this repository's production behavior; the supported automation remains `video.upload` to the TikTok draft/inbox flow.

## 4. Expected GitHub secrets

```text
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
TIKTOK_CLIENT_KEY
TIKTOK_CLIENT_SECRET
TIKTOK_TOKEN_KEY
```

Optional failure notifications:

```text
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
```

Never commit OAuth client secrets, access tokens, refresh tokens, plaintext token JSON, or the Fernet encryption key.
