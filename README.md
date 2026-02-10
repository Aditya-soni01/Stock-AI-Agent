# Stock AI Agent

## Upstox integration

### You do NOT put any "code" in the callback URL

The callback `http://127.0.0.1:8000/upstox/callback` is **only** used when **Upstox redirects the user** after they approve your app. Upstox then adds the code automatically:  
`http://127.0.0.1:8000/upstox/callback?code=XXXXX`

**Correct flow:**

1. In your app, click **Connect Upstox** (header dropdown).
2. You are sent to the backend `/upstox/login`, then to Upstox’s login page.
3. Log in to Upstox and approve the app.
4. Upstox redirects the browser to `http://127.0.0.1:8000/upstox/callback?code=...` (code is added by Upstox).
5. The backend exchanges that code for an access token and redirects you back to the app.

Do **not** open the callback URL manually or paste a code into it. The code is single-use and short-lived (about 1–2 minutes).

### If you see "Invalid Auth code" (UDAPI100057)

- **Redirect URI must match exactly**  
  In the Upstox developer dashboard, the redirect URI must be **exactly** the same as in your `.env`:
  - If `.env` has `UPSTOX_REDIRECT_URI=http://127.0.0.1:8000/upstox/callback`, use that same value in Upstox (not `http://localhost:8000/...`).
  - No trailing slash, same scheme (http/https) and host (127.0.0.1 vs localhost).
- **Do the full flow**  
  Start from **Connect Upstox** each time. Do not reuse an old callback URL or refresh the callback page (the code is one-time use).
- **Don’t delay**  
  Complete the login and approval within a couple of minutes so the code does not expire.
