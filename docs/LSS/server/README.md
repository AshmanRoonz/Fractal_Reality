# Last Ship Sailing ; local-host server

A tiny Bun-based WebSocket relay that lets two or more browsers play LSS together over your LAN (or your local machine, or via a tunnel for internet play). The server sits at the 0D-1D-2D substrate layer; clients render 3D locally. v7.0 is a pure relay; v7.1+ will move match-state authority and round timing onto the server itself.

## Install Bun (one time)

Bun is a single-binary JavaScript runtime; no `npm install`, no Node.js required.

**Windows (PowerShell):**

```
powershell -c "irm bun.sh/install.ps1 | iex"
```

**macOS / Linux:**

```
curl -fsSL https://bun.sh/install | bash
```

Verify:

```
bun --version
```

## Run the server

From the repo root:

```
cd docs/LSS
bun run server/main.ts
```

You should see something like:

```
===========================================
  Last Ship Sailing ; local server
===========================================
  Same machine:  http://localhost:8080
  LAN devices:   http://192.168.1.42:8080
  Health check:  http://localhost:8080/health
  WebSocket:     ws://localhost:8080/socket
===========================================
```

## Connect

**Same machine, two browser windows:** open `http://localhost:8080` in each. The server serves `last_ship_sailing_lh.html` at the root and the WebSocket auto-connects to the same origin. Press your usual lobby flow; both windows should see each other immediately under the same peer-id namespace.

**LAN play:** read the LAN IP from the startup banner (or run `ipconfig` / `ifconfig` separately) and tell other devices to open `http://<your-LAN-IP>:8080`. Their browsers fetch the page from your machine and open a WebSocket back to the same address.

**Public internet (no router config):** run a Cloudflare Tunnel against your local server. One command, free, gives you a `https://random-words.trycloudflare.com` URL that anyone can connect to:

```
cloudflared tunnel --url http://localhost:8080
```

(Install `cloudflared` from cloudflare.com first; one binary download, no account required for quick tunnels.)

## Server features

- **Static file server**: serves the LSS frontend HTML and the `ships/*.glb` model files. Nothing else; no caching, no routing surprises.
- **WebSocket relay**: assigns each connection a short peer-id (`p0001`, `p0002`, ...). Forwards every message a client sends to every other connected client, wrapped with `{from: peerId, payload: ...}` so the frontend can keep its existing per-peer handler shape.
- **Peer events**: emits `{type: 'hello', myPeerId, peers}` on connect, `{type: 'peer-join', peerId}` and `{type: 'peer-leave', peerId}` on join/leave. The frontend mirrors what Trystero gave it.
- **Health endpoint**: `GET /health` returns `{ok, clients, uptimeSeconds}` for diagnosis.

## Server NON-features (v7.0)

The server doesn't run any gameplay yet. It just relays whatever the frontend wants to broadcast (substrate deltas, hit claims, loadout announcements, etc.). All gameplay logic still lives on each client. Round-state desync that v6.x had can still happen here; the next iteration moves match authority server-side.

## Configuration

Environment variables:

- `PORT` (default 8080)
- `HOSTNAME` (default `0.0.0.0`)

Example:

```
PORT=9090 bun run server/main.ts
```

## Troubleshooting

**"Connection refused" from another machine.** Check your firewall; on Windows, allow Bun through Windows Defender Firewall on the relevant port. Confirm the server is binding to `0.0.0.0`, not `127.0.0.1`.

**"Mixed content" errors in the browser console.** That means the page is on `https://` and trying to talk to `ws://`. Either keep the page on plain `http://` (works for localhost and LAN), or use a tunnel (Cloudflare/ngrok) to get a `wss://` endpoint.

**No peer-join events fire.** Open `/health` in the browser; it should show the current client count. If it's >1 but you don't see `peer-join` messages on either client, the WebSocket is not connecting; check the browser DevTools Network tab for the `/socket` upgrade.
