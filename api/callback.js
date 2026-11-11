// Content Studio sign-in, step 2: exchange GitHub's code for a token, server-side, and hand it to
// the Decap window that opened the sign-in (its own origin only). Only the accounts listed in
// STUDIO_ALLOWED_USERS (default: Sapereaaude) are let in.
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const origin = `https://${host}`;
  const page = (status, payload) => {
    const msg = `authorization:github:${status}:${JSON.stringify(payload)}`;
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(200).send(`<!doctype html><meta charset="utf-8"><title>Signing in…</title><p style="font-family:sans-serif">${status === 'success' ? 'Signed in. You can close this window.' : 'Sign-in failed: ' + String(payload.error || '').replace(/</g, '&lt;')}</p>
<script>
(function () {
  var origin = ${JSON.stringify(origin)}, msg = ${JSON.stringify(msg)};
  function receive(e) { if (e.origin !== origin) { return; } window.opener.postMessage(msg, origin); window.removeEventListener('message', receive); }
  window.addEventListener('message', receive, false);
  if (window.opener) { window.opener.postMessage('authorizing:github', origin); }
})();
</script>`);
  };
  try {
    const url = new URL(req.url, origin);
    const code = url.searchParams.get('code');
    const state = url.searchParams.get('state');
    const cookie = (req.headers.cookie || '').split(';').map((c) => c.trim()).find((c) => c.startsWith('studio_state='));
    if (!code || !state || !cookie || cookie.split('=')[1] !== state) { page('error', { error: 'invalid sign-in state, please try again' }); return; }
    const r = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: process.env.GITHUB_CLIENT_ID, client_secret: process.env.GITHUB_CLIENT_SECRET, code, redirect_uri: `${origin}/api/callback` })
    });
    const data = await r.json();
    if (!data.access_token) { page('error', { error: data.error_description || 'GitHub refused the sign-in' }); return; }
    const who = await fetch('https://api.github.com/user', { headers: { Authorization: `Bearer ${data.access_token}`, 'User-Agent': 'content-studio' } }).then((x) => x.json());
    const allowed = (process.env.STUDIO_ALLOWED_USERS || 'Sapereaaude').split(',').map((s) => s.trim().toLowerCase());
    if (!who || !who.login || allowed.indexOf(who.login.toLowerCase()) === -1) { page('error', { error: 'this GitHub account is not allowed' }); return; }
    page('success', { token: data.access_token, provider: 'github' });
  } catch (err) {
    page('error', { error: 'sign-in failed' });
  }
};
