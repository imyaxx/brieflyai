# BrieflyAI

A blog platform that automatically summarizes every post with GPT-4o-mini and pushes digests to subscribers via Telegram — so readers get the value without the scroll.

## Problem It Solves

Content discovery on blogs is slow: readers either miss posts or skim walls of text looking for relevance. BrieflyAI attaches a 2–3 sentence AI summary to every post at publish time and delivers it directly to subscribers' Telegram chats, cutting time-to-relevance from minutes to seconds. Authors get distribution without building a mailing list; readers never open a post that isn't worth their time.

## Live Demo

| | |
|---|---|
| API | https://brieflyai-production-8f2c.up.railway.app/api/v1/ |
| Swagger UI | https://brieflyai-production-8f2c.up.railway.app/docs |
| Telegram Bot | @BrieflyAI_app_bot |

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI 0.115 | Async HTTP API |
| SQLAlchemy 2.0 (async) | ORM with asyncpg driver |
| PostgreSQL 16 | Primary database |
| Alembic | Schema migrations |
| Pydantic v2 | Request/response validation |
| python-jose + passlib | JWT auth, bcrypt hashing |
| OpenAI `gpt-4o-mini` | Post summarization |
| aiogram 3 | Telegram bot (async, webhook-ready) |
| Nginx | Reverse proxy, gzip, single public entry point |
| Docker Compose | Orchestration (dev + production profiles) |

## Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │                  Docker network              │
                        │                                              │
  Browser / Client ──▶  │  Nginx :80  ──▶  FastAPI :8000  ──▶  PostgreSQL
                        │                       │
                        │                       ├──▶  OpenAI API  (summarize on create)
                        │                       │
                        │                       └──▶  notify_subscribers()
                        │                                    │
  Telegram User  ──▶  Bot (aiogram 3)  ──────────────────────┘
                        │                       │
                        │              AsyncSessionLocal
                        │                       │
                        │                  PostgreSQL
                        └─────────────────────────────────────────────┘

  Post lifecycle:
  POST /api/v1/posts
    → generate_summary()  [OpenAI]
    → INSERT post
    → get_author_subscribers()
    → bot.send_message() × N  [Telegram]
```

## Features

- **JWT authentication** — register, login, Bearer token on protected routes
- **Blog CRUD** — create, read, update, delete with per-owner authorization (403 on mismatched ownership)
- **AI summaries** — GPT-4o-mini generates a 2–3 sentence TL;DR for every post at creation time; re-generated if content is edited
- **Telegram bot** — `/subscribe <author>` and `/unsubscribe <author>` commands, inline unsubscribe button on confirmation message
- **Push notifications** — new post triggers async fan-out to all subscribers with `telegram_chat_id` on record
- **Fully async** — FastAPI + asyncpg + aiogram 3; zero blocking calls in the hot path
- **Alembic migrations** — async-compatible `env.py`, autogenerate-ready
- **Dockerized** — `docker compose up --build` brings up Postgres, API, Bot, and Nginx; override file adds hot reload for local dev

## API Endpoints

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Create account |
| `POST` | `/api/v1/auth/login` | Public | Get JWT (OAuth2 form) |

### Posts

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/posts` | Required | Create post + trigger AI summary + notify subscribers |
| `GET` | `/api/v1/posts` | Public | List published posts (paginated, newest first) |
| `GET` | `/api/v1/posts/my` | Required | All posts by the authenticated user |
| `GET` | `/api/v1/posts/{id}` | Public | Single post by ID |
| `PUT` | `/api/v1/posts/{id}` | Required | Partial update; re-summarizes if content changes |
| `DELETE` | `/api/v1/posts/{id}` | Required | Delete (owner only) |

### System

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | Public | Docker health check probe |

## Quick Start (Local)

**Prerequisites:** Docker and Docker Compose installed.

```bash
# 1. Clone
git clone https://github.com/imyaxx/brieflyai.git
cd brieflyai

# 2. Configure
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD, SECRET_KEY, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN

# 3. Run (docker-compose.override.yml is merged automatically for dev)
docker compose up --build

# 4. Explore
open http://localhost/docs        # Swagger UI via Nginx
open http://localhost:8000/docs   # Direct to API (dev override)
```

Migrations run automatically when the API container starts — add this to your entrypoint or run manually:

```bash
docker compose exec api alembic upgrade head
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL username | `brieflyai` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `changeme` |
| `POSTGRES_DB` | PostgreSQL database name | `brieflyai` |
| `DATABASE_URL` | Full async DSN — use `db` as host inside Docker | `postgresql+asyncpg://brieflyai:changeme@db:5432/brieflyai` |
| `SECRET_KEY` | JWT signing key — generate with `openssl rand -hex 32` | `a3f9...` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather | `123456789:AAF...` |

## Project Structure

```
brieflyai/
├── app/                          # FastAPI application
│   ├── main.py                   # App factory, lifespan, router mount
│   ├── core/
│   │   ├── config.py             # Pydantic-settings — single Settings instance
│   │   ├── database.py           # Async engine, session factory, Base, get_db
│   │   └── security.py           # bcrypt hashing, JWT encode/decode
│   ├── api/v1/
│   │   ├── router.py             # Central router + /health endpoint
│   │   ├── dependencies.py       # get_current_user dependency (JWT → User)
│   │   └── endpoints/
│   │       ├── auth.py           # /register, /login
│   │       └── posts.py          # Full posts CRUD
│   ├── models/
│   │   ├── user.py               # User ORM model
│   │   ├── post.py               # Post ORM model (FK → users)
│   │   └── subscription.py       # Subscription model, unique (subscriber, author)
│   ├── schemas/
│   │   ├── user.py               # UserCreate, UserResponse, Token, TokenPayload
│   │   └── post.py               # PostCreate, PostUpdate, PostResponse
│   └── services/
│       ├── auth_service.py       # register_user, authenticate_user
│       ├── post_service.py       # CRUD + notify trigger
│       └── ai_service.py         # generate_summary via OpenAI
├── bot/                          # aiogram 3 Telegram bot
│   ├── main.py                   # Bot + Dispatcher init, start_polling
│   ├── config.py                 # Re-exports TELEGRAM_BOT_TOKEN
│   ├── keyboards.py              # InlineKeyboardMarkup builders
│   ├── notifications.py          # notify_subscribers fan-out
│   ├── handlers/
│   │   ├── start.py              # /start command
│   │   └── subscriptions.py      # /subscribe, /unsubscribe, callback handler
│   └── services/
│       └── subscription_service.py  # DB queries for subscriptions
├── migrations/
│   ├── env.py                    # Async alembic env wired to app settings
│   └── versions/                 # Auto-generated migration files
├── nginx/
│   └── nginx.conf                # Upstream, proxy headers, gzip
├── Dockerfile                    # API image (python:3.12-slim, non-root)
├── Dockerfile.bot                # Bot image
├── docker-compose.yml            # Production stack
├── docker-compose.override.yml   # Dev overrides: hot reload, port 8000 exposed
├── .env.example                  # All required variables with example values
└── requirements.txt              # Pinned dependencies, Python 3.12
```

## Deployment (VPS)

```bash
# On the server — skip the override file to get the production config
git clone https://github.com/imyaxx/brieflyai.git
cd brieflyai
cp .env.example .env && nano .env   # set real secrets

docker compose -f docker-compose.yml up -d --build
docker compose exec api alembic upgrade head
```

Nginx listens on port 80. To add TLS, place a Certbot-managed config in `nginx/` and mount the cert volume — the upstream block stays unchanged.

## Engineering Decisions

- **aiogram 3 over python-telegram-bot** — aiogram 3 is fully async-native and uses the same asyncio event loop as FastAPI. PTB 20+ is also async, but aiogram's router/filter system is more composable for larger bots and its FSM support scales better if conversation flows are added later.

- **`exclude_unset=True` in update endpoints** — `model_dump(exclude_unset=True)` only returns fields the client explicitly sent. Without it, a `PUT {"is_published": true}` would also send `title=None` and `content=None`, wiping existing data. It also means the AI re-summarization only fires when `content` is genuinely in the payload.

- **`/my` declared before `/{post_id}` in the posts router** — FastAPI matches routes in registration order. If `/{post_id}` appeared first, a request to `GET /posts/my` would be captured by the UUID path parameter and fail with a 422 Unprocessable Entity before reaching the correct handler. Route ordering is not a style choice here — it is correctness.

- **Uniform `"Invalid email or password."` on login failure** — returning distinct messages for "user not found" vs "wrong password" leaks whether an email address is registered, enabling user enumeration attacks. The same response for both cases prevents this at no cost to legitimate users who know what they entered.
