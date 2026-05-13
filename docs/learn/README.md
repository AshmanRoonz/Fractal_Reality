# Learning Claude AI with Ashman

A static site (landing page + course list + sign-up form) plus a working forum. The frontend is plain HTML/CSS/JS so it deploys to GitHub Pages or Netlify for free; the forum and sign-ups are backed by Supabase (also free tier).

## Files

- `index.html` ; landing page (hero, courses, about, sign-up form)
- `forum.html` ; forum (sign in/up, topics, replies)
- `styles.css` ; shared styling
- `app.js` ; shared Supabase client + helpers
- `config.js` ; **paste your Supabase keys here**
- `supabase-schema.sql` ; database schema (run once in Supabase)

## One-time setup (about 10 minutes)

### 1. Create a Supabase project

1. Go to https://supabase.com and sign in with GitHub or email.
2. Click **New project**, give it a name (e.g. `learning-claude-ai`), pick a region close to you, and set a database password (save it somewhere safe).
3. Wait a minute or two while it provisions.

### 2. Run the schema

1. In your project, open **SQL Editor** in the left sidebar.
2. Click **New query**.
3. Open `supabase-schema.sql` from this folder, copy all of it, paste into the query window, and click **Run**.
4. You should see "Success. No rows returned." That's it; tables and security rules are now set up.

### 3. Paste your keys into `config.js`

1. In Supabase, go to **Settings -> API**.
2. Copy the **Project URL** and the **anon public** key.
3. Open `config.js` in this folder and replace the two placeholders:

```js
export const SUPABASE_URL = 'https://YOUR-PROJECT.supabase.co';
export const SUPABASE_ANON_KEY = 'eyJhbGciOi...';
```

The anon key is **safe to put in the frontend**; the row-level security policies in the schema are what actually protect your data.

### 4. (Optional) Disable email confirmation while you're testing

By default Supabase emails users a confirmation link before they can sign in. While you're testing the forum:

- Go to **Authentication -> Providers -> Email** and toggle **Confirm email** off.
- Turn it back on before you go live.

## Run locally

You can't open `index.html` by double-clicking it because the JS uses ES modules, which browsers refuse to load from `file://`. Run a tiny local server instead:

```bash
# Python (built in on most systems)
python -m http.server 8000

# or, if you have Node:
npx serve .
```

Then open http://localhost:8000 in your browser.

## Deploy

### Netlify (easiest)

1. Sign in at https://netlify.com.
2. Drag this whole folder onto the Netlify dashboard. Done; you'll get a URL like `learning-claude-ai.netlify.app`.
3. Whenever you change a file, drag the folder again to redeploy. (Or connect a GitHub repo for auto-deploys.)

### GitHub Pages

1. Push these files to a GitHub repo.
2. In the repo, go to **Settings -> Pages**.
3. Under **Source**, choose **Deploy from a branch**, pick `main` and `/ (root)`, save.
4. Your site will be at `https://YOUR-USERNAME.github.io/REPO-NAME/`.

## Reading sign-ups

Anyone can submit the sign-up form (good); only you can read submissions (also good). To see them:

- Open Supabase -> **Table Editor** -> `signups`.
- Or **SQL Editor** -> run `select * from signups order by created_at desc;`.

You can also wire up an email notification: Supabase -> **Database -> Webhooks** -> create a webhook on `signups` insert that hits a service like Zapier or Make to email you.

## Customising

- **Course list**: edit the `<article class="course-card">` blocks in `index.html`.
- **About text**: edit the `#about` section in `index.html`.
- **Colours / vibe**: change the `:root` CSS variables at the top of `styles.css`. The accent is a warm amber by default.
- **Forum welcome text**: edit the paragraph at the top of `#view-list` in `forum.html`.

## Costs

Supabase free tier: 500MB database, 50,000 monthly active users, 5GB bandwidth. Plenty for a local-courses forum. If you outgrow it later, paid tiers start at $25/mo.

Netlify and GitHub Pages: free for personal sites.

## Troubleshooting

- **"Setup needed" warning on the forum page** ; you haven't filled in `config.js` yet.
- **"Invalid API key" or "Failed to fetch"** ; double-check the URL and anon key in `config.js`. The URL should start with `https://` and end with `.supabase.co`.
- **Sign-up form does nothing** ; if Supabase isn't configured yet, the form falls back to opening your email app with a pre-filled message. Once Supabase is set up, submissions go to the `signups` table.
- **Topics don't appear after posting** ; check the Supabase **Logs -> API** for any RLS errors. The schema should have been run in full.

Questions? Email ashroney@gmail.com.
