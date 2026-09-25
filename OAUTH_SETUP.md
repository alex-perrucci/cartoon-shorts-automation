# OAuth setup for social publishing

The production workflow uploads successful renders to:

- **YouTube** as a private video with title, description, hashtags and tags already populated.
- **TikTok** through the official `video.upload` inbox flow. The creator receives a TikTok notification to continue the post, while Telegram receives the final caption/hashtags and YouTube metadata for copy/paste.

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

TikTok Direct Post uses the official Content Posting API and requires the `video.publish` scope. The helper also keeps `video.upload` for compatibility.

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
6. Enable Direct Post and obtain approval for the `video.publish` scope (and keep `video.upload` if desired). The TikTok account must authorize the scopes.
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
python scripts/oauth_tiktok.py --scope "video.upload,video.publish"
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

## 3. TikTok private-ready Direct Post

The normal render workflow no longer sends inbox drafts. To prepare a finished TikTok post without reopening the editor, open **Actions -> Prepare TikTok private-ready -> Run workflow**.

- provide the existing manifest path;
- explicitly confirm the `SELF_ONLY` private post;
- optionally choose Comment / Duet / Stitch permissions.

The uploader queries TikTok creator info first and rejects interaction settings that the creator account does not currently allow. Caption and 3-6 relevant hashtags come from the manifest and are sent in the Direct Post `title` field. The resulting TikTok item is a finished `SELF_ONLY` post, not an inbox draft, so no TikTok editing step is required.

TikTok requires explicit consent before each Direct Post. For an unaudited API client, TikTok additionally requires the target creator account itself to be set to Private at posting time and restricts the post to `SELF_ONLY`. After audit, public visibility can be enabled without changing the generated caption/hashtags.

After enabling `video.publish`, re-run the OAuth bootstrap and commit the newly encrypted `.auth/tiktok_tokens.enc` before using Direct Post.

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


## Current production behavior

The normal render workflow is intentionally conservative:

- YouTube is uploaded as **private**, already carrying the final title, description, hashtags and search tags.
- TikTok is uploaded with **video.upload** to the creator inbox. TikTok requires the creator to open the inbox notification to continue the creation flow; the upload endpoint does not carry the video caption/hashtags.
- Telegram sends the exact TikTok caption + hashtags to paste, plus the final YouTube title and description. No successful MP4 delivery is required through Telegram.
- Direct Post support remains in the repository for audit/testing, but it is not the default production path.
