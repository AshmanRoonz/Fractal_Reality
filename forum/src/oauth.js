// OAuth 2.0 providers: Google, Discord, Facebook, Apple.
// Each provider exposes: configured(env), authUrl(env, redirectUri, state),
// and exchange(env, redirectUri, params) -> { providerId, name, email, avatarUrl }.
// Apple uses response_mode=form_post and a client secret that is an ES256 JWT
// signed with the developer's .p8 key.
// Created: 2026-11-14

import { decodeJwtPayload, b64url } from './auth.js';

const te = new TextEncoder();

async function postForm(url, fields) {
  const body = new URLSearchParams(fields);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' },
    body,
  });
  if (!res.ok) throw new Error(`token endpoint ${url} returned ${res.status}: ${(await res.text()).slice(0, 300)}`);
  return res.json();
}

// --- Google ---

const google = {
  id: 'google',
  label: 'Google',
  configured: (env) => Boolean(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET),
  authUrl(env, redirectUri, state) {
    const u = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    u.searchParams.set('client_id', env.GOOGLE_CLIENT_ID);
    u.searchParams.set('redirect_uri', redirectUri);
    u.searchParams.set('response_type', 'code');
    u.searchParams.set('scope', 'openid email profile');
    u.searchParams.set('state', state);
    return u.toString();
  },
  async exchange(env, redirectUri, params) {
    const tok = await postForm('https://oauth2.googleapis.com/token', {
      code: params.get('code'),
      client_id: env.GOOGLE_CLIENT_ID,
      client_secret: env.GOOGLE_CLIENT_SECRET,
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
    });
    const claims = decodeJwtPayload(tok.id_token || '') || {};
    if (!claims.sub) throw new Error('google: no subject in id_token');
    if (claims.aud !== env.GOOGLE_CLIENT_ID) throw new Error('google: aud mismatch');
    if (claims.iss !== 'https://accounts.google.com' && claims.iss !== 'accounts.google.com') throw new Error('google: iss mismatch');
    return {
      providerId: String(claims.sub),
      name: claims.name || (claims.email ? claims.email.split('@')[0] : 'Someone'),
      email: claims.email || null,
      avatarUrl: claims.picture || null,
    };
  },
};

// --- Discord ---

const discord = {
  id: 'discord',
  label: 'Discord',
  configured: (env) => Boolean(env.DISCORD_CLIENT_ID && env.DISCORD_CLIENT_SECRET),
  authUrl(env, redirectUri, state) {
    const u = new URL('https://discord.com/oauth2/authorize');
    u.searchParams.set('client_id', env.DISCORD_CLIENT_ID);
    u.searchParams.set('redirect_uri', redirectUri);
    u.searchParams.set('response_type', 'code');
    u.searchParams.set('scope', 'identify email');
    u.searchParams.set('state', state);
    u.searchParams.set('prompt', 'none');
    return u.toString();
  },
  async exchange(env, redirectUri, params) {
    const tok = await postForm('https://discord.com/api/oauth2/token', {
      code: params.get('code'),
      client_id: env.DISCORD_CLIENT_ID,
      client_secret: env.DISCORD_CLIENT_SECRET,
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
    });
    const res = await fetch('https://discord.com/api/users/@me', {
      headers: { Authorization: `Bearer ${tok.access_token}` },
    });
    if (!res.ok) throw new Error(`discord /users/@me returned ${res.status}`);
    const me = await res.json();
    const avatar = me.avatar ? `https://cdn.discordapp.com/avatars/${me.id}/${me.avatar}.png?size=96` : null;
    return {
      providerId: String(me.id),
      name: me.global_name || me.username || 'Someone',
      email: me.email || null,
      avatarUrl: avatar,
    };
  },
};

// --- Facebook ---

const FB_V = 'v21.0';

const facebook = {
  id: 'facebook',
  label: 'Facebook',
  configured: (env) => Boolean(env.FACEBOOK_CLIENT_ID && env.FACEBOOK_CLIENT_SECRET),
  authUrl(env, redirectUri, state) {
    const u = new URL(`https://www.facebook.com/${FB_V}/dialog/oauth`);
    u.searchParams.set('client_id', env.FACEBOOK_CLIENT_ID);
    u.searchParams.set('redirect_uri', redirectUri);
    u.searchParams.set('response_type', 'code');
    u.searchParams.set('scope', 'public_profile,email');
    u.searchParams.set('state', state);
    return u.toString();
  },
  async exchange(env, redirectUri, params) {
    const tokUrl = new URL(`https://graph.facebook.com/${FB_V}/oauth/access_token`);
    tokUrl.searchParams.set('client_id', env.FACEBOOK_CLIENT_ID);
    tokUrl.searchParams.set('client_secret', env.FACEBOOK_CLIENT_SECRET);
    tokUrl.searchParams.set('redirect_uri', redirectUri);
    tokUrl.searchParams.set('code', params.get('code'));
    const tokRes = await fetch(tokUrl);
    if (!tokRes.ok) throw new Error(`facebook token endpoint returned ${tokRes.status}`);
    const tok = await tokRes.json();
    const meUrl = new URL(`https://graph.facebook.com/${FB_V}/me`);
    meUrl.searchParams.set('fields', 'id,name,email,picture.type(large)');
    meUrl.searchParams.set('access_token', tok.access_token);
    const meRes = await fetch(meUrl);
    if (!meRes.ok) throw new Error(`facebook /me returned ${meRes.status}`);
    const me = await meRes.json();
    return {
      providerId: String(me.id),
      name: me.name || 'Someone',
      email: me.email || null,
      avatarUrl: me.picture && me.picture.data ? me.picture.data.url : null,
    };
  },
};

// --- Apple ---
// Requires an Apple Developer account: a Services ID (APPLE_CLIENT_ID), the
// Team ID, a Sign in with Apple private key (.p8) and its Key ID. The client
// secret is a short-lived ES256 JWT we mint here. Apple POSTs the callback
// (response_mode=form_post) and only sends the user's name on the FIRST
// authorization.

async function appleClientSecret(env) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: 'ES256', kid: env.APPLE_KEY_ID, typ: 'JWT' };
  const payload = {
    iss: env.APPLE_TEAM_ID,
    iat: now,
    exp: now + 3600,
    aud: 'https://appleid.apple.com',
    sub: env.APPLE_CLIENT_ID,
  };
  const enc = (obj) => b64url(te.encode(JSON.stringify(obj)));
  const signingInput = `${enc(header)}.${enc(payload)}`;
  const pem = env.APPLE_PRIVATE_KEY.replace(/-----[A-Z ]+-----/g, '').replace(/\s+/g, '');
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const key = await crypto.subtle.importKey('pkcs8', der, { name: 'ECDSA', namedCurve: 'P-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, key, te.encode(signingInput));
  return `${signingInput}.${b64url(sig)}`;
}

const apple = {
  id: 'apple',
  label: 'Apple',
  configured: (env) => Boolean(env.APPLE_CLIENT_ID && env.APPLE_TEAM_ID && env.APPLE_KEY_ID && env.APPLE_PRIVATE_KEY),
  authUrl(env, redirectUri, state) {
    const u = new URL('https://appleid.apple.com/auth/authorize');
    u.searchParams.set('client_id', env.APPLE_CLIENT_ID);
    u.searchParams.set('redirect_uri', redirectUri);
    u.searchParams.set('response_type', 'code');
    u.searchParams.set('scope', 'name email');
    u.searchParams.set('response_mode', 'form_post');
    u.searchParams.set('state', state);
    return u.toString();
  },
  async exchange(env, redirectUri, params) {
    const tok = await postForm('https://appleid.apple.com/auth/token', {
      code: params.get('code'),
      client_id: env.APPLE_CLIENT_ID,
      client_secret: await appleClientSecret(env),
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
    });
    const claims = decodeJwtPayload(tok.id_token || '') || {};
    if (!claims.sub) throw new Error('apple: no subject in id_token');
    if (claims.aud !== env.APPLE_CLIENT_ID) throw new Error('apple: aud mismatch');
    if (claims.iss !== 'https://appleid.apple.com') throw new Error('apple: iss mismatch');
    // First sign-in only: Apple sends a "user" form field with the name.
    let name = null;
    const userField = params.get('user');
    if (userField) {
      try {
        const u = JSON.parse(userField);
        if (u.name) name = [u.name.firstName, u.name.lastName].filter(Boolean).join(' ') || null;
      } catch { /* ignore malformed user field */ }
    }
    if (!name) name = claims.email ? claims.email.split('@')[0] : 'Someone';
    return {
      providerId: String(claims.sub),
      name,
      email: claims.email || null,
      avatarUrl: null,
    };
  },
};

export const providers = { google, discord, facebook, apple };

export function configuredProviders(env) {
  return Object.values(providers).filter((p) => p.configured(env));
}
