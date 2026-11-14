// Sessions and cookies: HMAC-signed stateless session cookie, OAuth state
// cookie, CSRF origin check. No dependencies; WebCrypto only.
// Created: 2026-11-14

const SESSION_COOKIE = 'frf_session';
const STATE_COOKIE = 'frf_oauth';
const SESSION_DAYS = 30;

const te = new TextEncoder();

function b64url(bytes) {
  let s = '';
  const arr = new Uint8Array(bytes);
  for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i]);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function b64urlDecodeToString(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  return atob(s);
}

async function hmacKey(secret) {
  return crypto.subtle.importKey('raw', te.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}

export async function sign(value, secret) {
  const key = await hmacKey(secret);
  const sig = await crypto.subtle.sign('HMAC', key, te.encode(value));
  return `${value}.${b64url(sig)}`;
}

export async function verify(signed, secret) {
  const i = signed.lastIndexOf('.');
  if (i < 0) return null;
  const value = signed.slice(0, i);
  const key = await hmacKey(secret);
  const expected = await crypto.subtle.sign('HMAC', key, te.encode(value));
  if (b64url(expected) !== signed.slice(i + 1)) return null;
  return value;
}

export function getCookie(request, name) {
  const header = request.headers.get('Cookie') || '';
  for (const part of header.split(/;\s*/)) {
    const eq = part.indexOf('=');
    if (eq > 0 && part.slice(0, eq) === name) return part.slice(eq + 1);
  }
  return null;
}

function cookieAttrs(url, { maxAge, sameSite = 'Lax' } = {}) {
  const secure = url.protocol === 'https:' ? '; Secure' : '';
  const age = maxAge != null ? `; Max-Age=${maxAge}` : '';
  return `; Path=/; HttpOnly; SameSite=${sameSite}${secure}${age}`;
}

// --- Session cookie: "uid.exp" signed ---

export async function sessionCookie(url, userId, secret) {
  const exp = Math.floor(Date.now() / 1000) + SESSION_DAYS * 86400;
  const value = await sign(`${userId}.${exp}`, secret);
  return `${SESSION_COOKIE}=${value}${cookieAttrs(url, { maxAge: SESSION_DAYS * 86400 })}`;
}

export function clearSessionCookie(url) {
  return `${SESSION_COOKIE}=${cookieAttrs(url, { maxAge: 0 })}`;
}

export async function sessionUserId(request, secret) {
  const raw = getCookie(request, SESSION_COOKIE);
  if (!raw) return null;
  const value = await verify(raw, secret);
  if (!value) return null;
  const [uid, exp] = value.split('.');
  if (!uid || !exp || Number(exp) < Date.now() / 1000) return null;
  return Number(uid);
}

// --- OAuth state cookie: "provider.state.returnTo" signed, 10 minutes ---
// SameSite=None because Apple's form_post callback arrives as a cross-site
// POST, which a Lax cookie would not accompany. Short-lived and HttpOnly.

export async function stateCookie(url, provider, state, secret) {
  const value = await sign(`${provider}.${state}`, secret);
  const sameSite = url.protocol === 'https:' ? 'None' : 'Lax';
  return `${STATE_COOKIE}=${value}${cookieAttrs(url, { maxAge: 600, sameSite })}`;
}

export function clearStateCookie(url) {
  return `${STATE_COOKIE}=${cookieAttrs(url, { maxAge: 0 })}`;
}

export async function readStateCookie(request, secret) {
  const raw = getCookie(request, STATE_COOKIE);
  if (!raw) return null;
  const value = await verify(raw, secret);
  if (!value) return null;
  const dot = value.indexOf('.');
  if (dot < 0) return null;
  return { provider: value.slice(0, dot), state: value.slice(dot + 1) };
}

export function randomToken() {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return b64url(bytes);
}

// CSRF: every state-changing POST must come from our own origin.
export function sameOrigin(request, url) {
  const origin = request.headers.get('Origin');
  if (origin) return origin === url.origin;
  const referer = request.headers.get('Referer');
  if (referer) { try { return new URL(referer).origin === url.origin; } catch { return false; } }
  return false;
}

// Decode a JWT payload WITHOUT signature verification. Only ever used on
// id_tokens received directly from the provider's token endpoint over TLS in
// exchange for the authorization code, where the channel itself authenticates
// the issuer. iss/aud/exp are still checked by the caller.
export function decodeJwtPayload(jwt) {
  const parts = jwt.split('.');
  if (parts.length !== 3) return null;
  try { return JSON.parse(b64urlDecodeToString(parts[1])); } catch { return null; }
}

export { b64url };
