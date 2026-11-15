-- Fractal Reality Forum: initial schema
-- Created: 2026-11-14

PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  avatar_url TEXT,
  role TEXT NOT NULL DEFAULT 'member', -- member | mod | admin
  created_at INTEGER NOT NULL,
  UNIQUE (provider, provider_id)
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  position INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE threads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL REFERENCES categories(id),
  author_id INTEGER NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  bumped_at INTEGER NOT NULL,
  locked INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_threads_category ON threads(category_id, deleted, bumped_at DESC);
CREATE INDEX idx_threads_recent ON threads(deleted, bumped_at DESC);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_id INTEGER NOT NULL REFERENCES threads(id),
  author_id INTEGER NOT NULL REFERENCES users(id),
  body TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  deleted INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_posts_thread ON posts(thread_id, deleted, created_at);
CREATE INDEX idx_posts_author_recent ON posts(author_id, created_at DESC);

-- Seed categories, in the invitation's own words.
INSERT INTO categories (slug, name, description, position) VALUES
  ('ideas', 'Ideas', 'Share what you are seeing. A thought, a connection, a draft of something true.', 1),
  ('steelman', 'The Steelman Arena', 'Bring a disagreement and build the strongest version of the other side before you answer it.', 2),
  ('corrigibility', 'Corrigibility Practice', 'Say what changed your mind. "I was wrong, and here is what corrected me" is the strongest post here.', 3),
  ('perspectives', 'New Perspectives', 'Try on a view you do not hold and report what the world looks like from inside it.', 4),
  ('questions', 'Open Questions', 'What exists? What matters? Ask what you actually want to know.', 5);
