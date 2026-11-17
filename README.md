# Gridclaim

**Live:** [https://eieio.ismailbiswas.com](https://eieio.ismailbiswas.com)

A real-time shared board where anyone can claim blocks and every connected client sees updates instantly.

## Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Backend | Django 5 | Clear apps, ORM, admin, migrations |
| Realtime | Django Channels + Daphne | First-class WebSockets on ASGI |
| Fan-out | Redis channel layer | Multi-worker / multi-tab safe broadcast |
| DB | PostgreSQL | Row locks for conflict-safe claims |
| UI | HTMX + compact CSS | Server-rendered HTML, tiny JS, OOB swaps |

## Architecture

Apps talk through small interfaces so ownership rules stay testable and swappable:

- `apps.identity` — anonymous session players (`PlayerDirectory`)
- `apps.board` — cells, claim rules, leaderboard (`ClaimService`)
- `apps.realtime` — WebSocket consumer + `BoardEventPublisher`

Claim flow:

1. Browser `POST`s a claim via HTMX
2. `BoardClaimService` locks the player + cell rows, enforces cooldown, bumps `version`
3. Publisher broadcasts HTML fragments over the Redis channel layer
4. Other tabs swap the cell + sidebar via HTMX WebSocket OOB updates

## Run (local / server)

```bash
docker compose up --build -d
```

App listens on **`127.0.0.1:23000`** only (for nginx).  
Postgres + Redis are **private** to the `eieio_net` Docker network (no host ports), named `eieio-db` / `eieio-redis`, so they won’t clash with other stacks.

### Production host: eieio.ismailbiswas.com

1. Point DNS `eieio.ismailbiswas.com` at the server.
2. Start the stack: `docker compose up --build -d`
3. Install nginx site from `deploy/nginx-eieio.ismailbiswas.com.conf`
4. Issue TLS: `sudo certbot --nginx -d eieio.ismailbiswas.com`

Tunable env vars (see `docker-compose.yml`):

- `BOARD_WIDTH` / `BOARD_HEIGHT`
- `CLAIM_COOLDOWN_SECONDS`
- `DJANGO_SECRET_KEY` (change in production)

## Bonus features included

- Player names + color palette
- Claim cooldown
- Live leaderboard / stats
- Flash animation on remote claims
- Soft, compact UI with clear ownership states