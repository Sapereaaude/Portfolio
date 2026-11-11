// Content Studio sign-in, step 1: send the browser to GitHub's OAuth consent page.
// Needs two environment variables on Vercel: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.
const crypto = require('crypto');

module.exports = (req, res) => {
  const id = process.env.GITHUB_CLIENT_ID;
  if (!id) { res.status(500).send('GITHUB_CLIENT_ID is not set on Vercel.'); return; }
  const state = crypto.randomBytes(16).toString('hex');
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const redirect = `https://${host}/api/callback`;
  res.setHeader('Set-Cookie', `studio_state=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600`);
  res.setHeader('Cache-Control', 'no-store');
  res.writeHead(302, { Location: `https://github.com/login/oauth/authorize?client_id=${encodeURIComponent(id)}&redirect_uri=${encodeURIComponent(redirect)}&scope=repo&state=${state}` });
  res.end();
};
