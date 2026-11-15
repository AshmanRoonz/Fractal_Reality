// The Fractal Reality forum: a Cloudflare Worker serving server-rendered HTML
// backed by D1, with OAuth sign-in (Google, Discord, Facebook, Apple).
// Created: 2026-11-14

import * as db from './db.js';
import * as views from './html.js';
import {
  sessionUserId, sessionCookie, clearSessionCookie,
  stateCookie, readStateCookie, clearStateCookie,
  randomToken, sameOrigin,
} from './auth.js';
import { providers, configuredProviders } from './oauth.js';

const POST_COOLDOWN_S = 20;

// Providers configured but temporarily not offered to the public (shown
// greyed out on the sign-in page). Facebook waits on Meta's business
// verification; remove it from this list once the app is published.
const UNAVAILABLE_PROVIDERS = ['facebook'];

const html = (body, status = 200, headers = {}) =>
  new Response(body, { status, headers: { 'Content-Type': 'text/html; charset=utf-8', ...headers } });

const redirect = (to, headers = {}) =>
  new Response(null, { status: 303, headers: { Location: to, ...headers } });

async function currentUser(request, env) {
  if (!env.SESSION_SECRET) return null;
  const uid = await sessionUserId(request, env.SESSION_SECRET);
  return uid ? await db.getUser(env, uid) : null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      return await route(request, env, url);
    } catch (err) {
      console.error('unhandled', err && err.stack ? err.stack : String(err));
      return html(views.messagePage({ title: 'Something broke', body: 'The forum hit an error. It has been logged; please try again.', user: null }), 500);
    }
  },
};

async function route(request, env, url) {
  const { pathname } = url;
  const method = request.method;

  if (!env.SESSION_SECRET) {
    return html(views.messagePage({ title: 'Not configured', body: 'SESSION_SECRET is not set. See forum/README.md.', user: null }), 500);
  }

  // ---------- Auth ----------

  if (pathname === '/login' && method === 'GET') {
    const user = await currentUser(request, env);
    if (user) return redirect('/');
    return html(views.loginPage({
      providerList: configuredProviders(env).map((p) => ({
        id: p.id, label: p.label, unavailable: UNAVAILABLE_PROVIDERS.includes(p.id),
      })),
      devLogin: env.DEV_LOGIN === '1',
      error: url.searchParams.get('error') ? 'Sign-in did not complete. Please try again.' : null,
    }));
  }

  if (pathname === '/logout' && method === 'POST') {
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    return redirect('/', { 'Set-Cookie': clearSessionCookie(url) });
  }

  // Local-development sign-in, enabled only by DEV_LOGIN=1 in .dev.vars.
  if (pathname === '/auth/dev' && method === 'GET') {
    if (env.DEV_LOGIN !== '1') return html('Not found', 404);
    const user = await db.findOrCreateUser(env, {
      provider: 'dev', providerId: 'test-user-1',
      name: 'Test Wanderer', email: 'test@example.test', avatarUrl: null,
    });
    return redirect('/', { 'Set-Cookie': await sessionCookie(url, user.id, env.SESSION_SECRET) });
  }

  let m;

  // Start OAuth: GET /auth/:provider
  if ((m = pathname.match(/^\/auth\/(google|discord|facebook|apple)$/)) && method === 'GET') {
    const provider = providers[m[1]];
    if (!provider.configured(env)) return html('Provider not configured', 404);
    const state = randomToken();
    const redirectUri = `${url.origin}/auth/${provider.id}/callback`;
    return new Response(null, {
      status: 302,
      headers: {
        Location: provider.authUrl(env, redirectUri, state),
        'Set-Cookie': await stateCookie(url, provider.id, state, env.SESSION_SECRET),
      },
    });
  }

  // OAuth callback: GET (Google/Discord/Facebook) or POST (Apple form_post)
  if ((m = pathname.match(/^\/auth\/(google|discord|facebook|apple)\/callback$/))) {
    const provider = providers[m[1]];
    if (!provider.configured(env)) return html('Provider not configured', 404);

    let params;
    if (method === 'POST') {
      const form = await request.formData();
      params = new URLSearchParams();
      for (const [k, v] of form.entries()) if (typeof v === 'string') params.set(k, v);
    } else if (method === 'GET') {
      params = url.searchParams;
    } else {
      return html('Method not allowed', 405);
    }

    const clear = clearStateCookie(url);
    if (params.get('error')) return redirect('/login?error=1', { 'Set-Cookie': clear });

    const saved = await readStateCookie(request, env.SESSION_SECRET);
    if (!saved || saved.provider !== provider.id || !params.get('state') || saved.state !== params.get('state')) {
      return redirect('/login?error=1', { 'Set-Cookie': clear });
    }
    if (!params.get('code')) return redirect('/login?error=1', { 'Set-Cookie': clear });

    let identity;
    try {
      identity = await provider.exchange(env, `${url.origin}/auth/${provider.id}/callback`, params);
    } catch (err) {
      console.error(`oauth ${provider.id}`, String(err));
      return redirect('/login?error=1', { 'Set-Cookie': clear });
    }

    const user = await db.findOrCreateUser(env, {
      provider: provider.id,
      providerId: identity.providerId,
      name: identity.name,
      email: identity.email,
      avatarUrl: identity.avatarUrl,
    });

    const headers = new Headers({ Location: '/' });
    headers.append('Set-Cookie', clear);
    headers.append('Set-Cookie', await sessionCookie(url, user.id, env.SESSION_SECRET));
    return new Response(null, { status: 303, headers });
  }

  // ---------- Pages ----------

  const user = await currentUser(request, env);

  if (pathname === '/' && method === 'GET') {
    const [cats, threads] = await Promise.all([db.getCategories(env), db.recentThreads(env)]);
    return html(views.homePage({ categories: cats.results, threads: threads.results, user }));
  }

  if (pathname === '/guidelines' && method === 'GET') {
    return html(views.guidelinesPage({ user }));
  }

  if (pathname === '/me' && method === 'GET') {
    if (!user) return redirect('/login');
    return html(views.mePage({ user, saved: url.searchParams.has('saved') }));
  }

  if (pathname === '/me' && method === 'POST') {
    if (!user) return redirect('/login');
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    const form = await request.formData();
    const name = String(form.get('name') || '').trim().slice(0, 60);
    if (name.length >= 2) await db.renameUser(env, user.id, name);
    return redirect('/me?saved=1');
  }

  if (pathname === '/me/delete' && method === 'POST') {
    if (!user) return redirect('/login');
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    await db.deleteUserData(env, user.id);
    return html(
      views.messagePage({ title: 'Account deleted', body: 'Your name, email, avatar, and sign-in link have been permanently removed. Thank you for having been here.', user: null }),
      200,
      { 'Set-Cookie': clearSessionCookie(url) }
    );
  }

  if ((m = pathname.match(/^\/c\/([a-z0-9-]+)$/)) && method === 'GET') {
    const category = await db.getCategory(env, m[1]);
    if (!category) return html(views.messagePage({ title: 'Not found', body: 'No such place.', user }), 404);
    const page = Math.max(1, Number(url.searchParams.get('page')) || 1);
    const limit = 30;
    const rows = await db.categoryThreads(env, category.id, limit + 1, (page - 1) * limit);
    const threads = rows.results.slice(0, limit);
    return html(views.categoryPage({ category, threads, user, page, hasMore: rows.results.length > limit }));
  }

  if ((m = pathname.match(/^\/t\/(\d+)$/)) && method === 'GET') {
    const thread = await db.getThread(env, Number(m[1]));
    if (!thread) return html(views.messagePage({ title: 'Not found', body: 'This thread does not exist or was removed.', user }), 404);
    const posts = await db.threadPosts(env, thread.id);
    return html(views.threadPage({ thread, posts: posts.results, user, error: url.searchParams.get('error') }));
  }

  if (pathname === '/new' && method === 'GET') {
    if (!user) return redirect('/login');
    const cats = await db.getCategories(env);
    return html(views.newThreadPage({ categories: cats.results, selected: url.searchParams.get('c') || 'ideas', user }));
  }

  if (pathname === '/new' && method === 'POST') {
    if (!user) return redirect('/login');
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    const form = await request.formData();
    const title = String(form.get('title') || '').trim().slice(0, 200);
    const body = String(form.get('body') || '').trim().slice(0, 20000);
    const category = await db.getCategory(env, String(form.get('category') || ''));
    const cats = await db.getCategories(env);
    const draft = { title, body };
    if (!category) return html(views.newThreadPage({ categories: cats.results, selected: 'ideas', user, error: 'Pick a place for the thread.', draft }), 400);
    if (title.length < 4) return html(views.newThreadPage({ categories: cats.results, selected: category.slug, user, error: 'The title is too short.', draft }), 400);
    if (body.length < 10) return html(views.newThreadPage({ categories: cats.results, selected: category.slug, user, error: 'Say a little more in the first post.', draft }), 400);
    const last = await db.lastPostAt(env, user.id);
    if (Date.now() / 1000 - last < POST_COOLDOWN_S) {
      return html(views.newThreadPage({ categories: cats.results, selected: category.slug, user, error: 'You are posting very fast. Give it a few seconds.', draft }), 429);
    }
    const threadId = await db.createThread(env, { categoryId: category.id, authorId: user.id, title, body });
    return redirect(`/t/${threadId}`);
  }

  if ((m = pathname.match(/^\/t\/(\d+)\/reply$/)) && method === 'POST') {
    if (!user) return redirect('/login');
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    const thread = await db.getThread(env, Number(m[1]));
    if (!thread) return html(views.messagePage({ title: 'Not found', body: 'This thread does not exist or was removed.', user }), 404);
    if (thread.locked) return redirect(`/t/${thread.id}?error=${encodeURIComponent('This thread is locked.')}`);
    const form = await request.formData();
    const body = String(form.get('body') || '').trim().slice(0, 20000);
    if (body.length < 2) return redirect(`/t/${thread.id}?error=${encodeURIComponent('That reply was empty.')}`);
    const last = await db.lastPostAt(env, user.id);
    if (Date.now() / 1000 - last < POST_COOLDOWN_S) {
      return redirect(`/t/${thread.id}?error=${encodeURIComponent('You are posting very fast. Give it a few seconds.')}`);
    }
    await db.createReply(env, { threadId: thread.id, authorId: user.id, body });
    return redirect(`/t/${thread.id}`);
  }

  // ---------- Moderation ----------

  const isMod = user && (user.role === 'admin' || user.role === 'mod');

  if ((m = pathname.match(/^\/t\/(\d+)\/(lock|unlock|delete)$/)) && method === 'POST') {
    if (!isMod) return html('Forbidden', 403);
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    const id = Number(m[1]);
    if (m[2] === 'delete') { await db.softDeleteThread(env, id); return redirect('/'); }
    await db.setThreadLocked(env, id, m[2] === 'lock');
    return redirect(`/t/${id}`);
  }

  if ((m = pathname.match(/^\/p\/(\d+)\/delete$/)) && method === 'POST') {
    if (!isMod) return html('Forbidden', 403);
    if (!sameOrigin(request, url)) return html('Forbidden', 403);
    const post = await db.getPost(env, Number(m[1]));
    if (post) await db.softDeletePost(env, post.id);
    return redirect(post ? `/t/${post.thread_id}` : '/');
  }

  return html(views.messagePage({ title: 'Not found', body: 'Nothing lives at this address.', user }), 404);
}
