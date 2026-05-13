-- Learning Claude AI with Ashman; Supabase schema.
-- Run this once in your Supabase project: Dashboard -> SQL Editor -> New query -> paste -> Run.

-- =========================================================
-- 1. SIGNUPS table (course interest form on the landing page)
-- =========================================================
create table if not exists public.signups (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  name        text not null,
  email       text not null,
  course      text not null,
  note        text
);

alter table public.signups enable row level security;

-- Anyone can submit a signup (insert), but only authenticated admins can read.
drop policy if exists "anyone can submit signups" on public.signups;
create policy "anyone can submit signups"
  on public.signups for insert
  to anon, authenticated
  with check (true);

-- (No SELECT policy means anon/authenticated cannot read signups; you read them via the Supabase dashboard.)

-- =========================================================
-- 2. TOPICS table (forum threads)
-- =========================================================
create table if not exists public.topics (
  id                uuid primary key default gen_random_uuid(),
  created_at        timestamptz not null default now(),
  last_activity_at  timestamptz not null default now(),
  title             text not null check (char_length(title) between 3 and 200),
  body              text not null check (char_length(body) between 1 and 10000),
  author_id         uuid references auth.users(id) on delete set null,
  author_name       text,
  reply_count       integer not null default 0
);

create index if not exists topics_last_activity_idx on public.topics(last_activity_at desc);

alter table public.topics enable row level security;

drop policy if exists "anyone can read topics" on public.topics;
create policy "anyone can read topics"
  on public.topics for select
  to anon, authenticated
  using (true);

drop policy if exists "authenticated users can create topics" on public.topics;
create policy "authenticated users can create topics"
  on public.topics for insert
  to authenticated
  with check (auth.uid() = author_id);

drop policy if exists "authors can update their topics" on public.topics;
create policy "authors can update their topics"
  on public.topics for update
  to authenticated
  using (auth.uid() = author_id)
  with check (auth.uid() = author_id);

drop policy if exists "authors can delete their topics" on public.topics;
create policy "authors can delete their topics"
  on public.topics for delete
  to authenticated
  using (auth.uid() = author_id);

-- =========================================================
-- 3. REPLIES table
-- =========================================================
create table if not exists public.replies (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  topic_id    uuid not null references public.topics(id) on delete cascade,
  body        text not null check (char_length(body) between 1 and 10000),
  author_id   uuid references auth.users(id) on delete set null,
  author_name text
);

create index if not exists replies_topic_idx on public.replies(topic_id, created_at);

alter table public.replies enable row level security;

drop policy if exists "anyone can read replies" on public.replies;
create policy "anyone can read replies"
  on public.replies for select
  to anon, authenticated
  using (true);

drop policy if exists "authenticated users can post replies" on public.replies;
create policy "authenticated users can post replies"
  on public.replies for insert
  to authenticated
  with check (auth.uid() = author_id);

drop policy if exists "authors can update their replies" on public.replies;
create policy "authors can update their replies"
  on public.replies for update
  to authenticated
  using (auth.uid() = author_id)
  with check (auth.uid() = author_id);

drop policy if exists "authors can delete their replies" on public.replies;
create policy "authors can delete their replies"
  on public.replies for delete
  to authenticated
  using (auth.uid() = author_id);

-- =========================================================
-- 4. Trigger: bump topic.last_activity_at and reply_count when a reply is added
-- =========================================================
create or replace function public.on_reply_inserted()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  update public.topics
     set reply_count = reply_count + 1,
         last_activity_at = now()
   where id = new.topic_id;
  return new;
end;
$$;

drop trigger if exists trg_on_reply_inserted on public.replies;
create trigger trg_on_reply_inserted
  after insert on public.replies
  for each row execute function public.on_reply_inserted();

create or replace function public.on_reply_deleted()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  update public.topics
     set reply_count = greatest(reply_count - 1, 0)
   where id = old.topic_id;
  return old;
end;
$$;

drop trigger if exists trg_on_reply_deleted on public.replies;
create trigger trg_on_reply_deleted
  after delete on public.replies
  for each row execute function public.on_reply_deleted();
