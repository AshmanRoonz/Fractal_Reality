// All D1 queries. Prepared statements only.
// Created: 2026-11-14

const now = () => Math.floor(Date.now() / 1000);

export async function findOrCreateUser(env, { provider, providerId, name, email, avatarUrl }) {
  const existing = await env.DB.prepare(
    'SELECT * FROM users WHERE provider = ? AND provider_id = ?'
  ).bind(provider, providerId).first();
  if (existing) {
    // Refresh avatar and email quietly; keep the user's chosen display name.
    await env.DB.prepare('UPDATE users SET email = ?, avatar_url = ? WHERE id = ?')
      .bind(email, avatarUrl, existing.id).run();
    return { ...existing, email, avatar_url: avatarUrl };
  }
  const admins = (env.ADMIN_EMAILS || '').split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);
  const role = email && admins.includes(email.toLowerCase()) ? 'admin' : 'member';
  const res = await env.DB.prepare(
    'INSERT INTO users (provider, provider_id, name, email, avatar_url, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).bind(provider, providerId, name.slice(0, 60), email, avatarUrl, role, now()).run();
  return await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(res.meta.last_row_id).first();
}

export function getUser(env, id) {
  return env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(id).first();
}

export function renameUser(env, id, name) {
  return env.DB.prepare('UPDATE users SET name = ? WHERE id = ?').bind(name, id).run();
}

export function getCategories(env) {
  return env.DB.prepare(`
    SELECT c.*, COUNT(t.id) AS thread_count
    FROM categories c
    LEFT JOIN threads t ON t.category_id = c.id AND t.deleted = 0
    GROUP BY c.id ORDER BY c.position
  `).all();
}

export function getCategory(env, slug) {
  return env.DB.prepare('SELECT * FROM categories WHERE slug = ?').bind(slug).first();
}

const THREAD_COLS = `
  t.id, t.title, t.created_at, t.bumped_at, t.locked, t.category_id,
  u.name AS author_name, u.avatar_url AS author_avatar,
  c.name AS category_name, c.slug AS category_slug,
  (SELECT COUNT(*) FROM posts p WHERE p.thread_id = t.id AND p.deleted = 0) - 1 AS reply_count
`;

export function recentThreads(env, limit = 25) {
  return env.DB.prepare(`
    SELECT ${THREAD_COLS} FROM threads t
    JOIN users u ON u.id = t.author_id
    JOIN categories c ON c.id = t.category_id
    WHERE t.deleted = 0
    ORDER BY t.bumped_at DESC LIMIT ?
  `).bind(limit).all();
}

export function categoryThreads(env, categoryId, limit, offset) {
  return env.DB.prepare(`
    SELECT ${THREAD_COLS} FROM threads t
    JOIN users u ON u.id = t.author_id
    JOIN categories c ON c.id = t.category_id
    WHERE t.deleted = 0 AND t.category_id = ?
    ORDER BY t.bumped_at DESC LIMIT ? OFFSET ?
  `).bind(categoryId, limit, offset).all();
}

export function getThread(env, id) {
  return env.DB.prepare(`
    SELECT t.*, c.name AS category_name, c.slug AS category_slug
    FROM threads t JOIN categories c ON c.id = t.category_id
    WHERE t.id = ? AND t.deleted = 0
  `).bind(id).first();
}

export function threadPosts(env, threadId) {
  return env.DB.prepare(`
    SELECT p.id, p.body, p.created_at, p.deleted,
           u.id AS author_id, u.name AS author_name, u.avatar_url AS author_avatar, u.role AS author_role
    FROM posts p JOIN users u ON u.id = p.author_id
    WHERE p.thread_id = ?
    ORDER BY p.created_at, p.id
  `).bind(threadId).all();
}

export async function lastPostAt(env, userId) {
  const row = await env.DB.prepare(
    'SELECT created_at FROM posts WHERE author_id = ? ORDER BY created_at DESC LIMIT 1'
  ).bind(userId).first();
  return row ? row.created_at : 0;
}

export async function createThread(env, { categoryId, authorId, title, body }) {
  const t = now();
  const tr = await env.DB.prepare(
    'INSERT INTO threads (category_id, author_id, title, created_at, bumped_at) VALUES (?, ?, ?, ?, ?)'
  ).bind(categoryId, authorId, title, t, t).run();
  const threadId = tr.meta.last_row_id;
  await env.DB.prepare(
    'INSERT INTO posts (thread_id, author_id, body, created_at) VALUES (?, ?, ?, ?)'
  ).bind(threadId, authorId, body, t).run();
  return threadId;
}

export async function createReply(env, { threadId, authorId, body }) {
  const t = now();
  await env.DB.batch([
    env.DB.prepare('INSERT INTO posts (thread_id, author_id, body, created_at) VALUES (?, ?, ?, ?)')
      .bind(threadId, authorId, body, t),
    env.DB.prepare('UPDATE threads SET bumped_at = ? WHERE id = ?').bind(t, threadId),
  ]);
}

export function setThreadLocked(env, id, locked) {
  return env.DB.prepare('UPDATE threads SET locked = ? WHERE id = ?').bind(locked ? 1 : 0, id).run();
}

export function softDeleteThread(env, id) {
  return env.DB.prepare('UPDATE threads SET deleted = 1 WHERE id = ?').bind(id).run();
}

export function softDeletePost(env, id) {
  return env.DB.prepare('UPDATE posts SET deleted = 1 WHERE id = ?').bind(id).run();
}

export function getPost(env, id) {
  return env.DB.prepare('SELECT * FROM posts WHERE id = ?').bind(id).first();
}

// Self-serve account deletion: permanently removes everything received from
// the sign-in provider (name, email, avatar) and unlinks the provider
// identity, so the account can never be signed into again. Posts remain,
// attributed to "Deleted member" (stated in the privacy policy).
export function deleteUserData(env, id) {
  return env.DB.prepare(
    "UPDATE users SET provider = 'deleted', provider_id = 'deleted-' || id, name = 'Deleted member', email = NULL, avatar_url = NULL, role = 'member' WHERE id = ?"
  ).bind(id).run();
}
