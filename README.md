# Escape the API

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

> An escape room that lives inside HTTP. Each room is a puzzle locked by a different HTTP concept — headers, status codes, methods, encoding, authentication. The response body is rarely where the answer lives.

🎮 **Live Demo:** [escape.xviilab.com](https://escape.xviilab.com)

---

## The Game

Players interact with the API using any HTTP client — `curl`, Postman, Insomnia, or browser DevTools. The web terminal at `/` is a guided way in, but the API itself is the real playground. Look at the headers. Decode the payload. Try the method you weren't told about.

## Tech Stack

**Backend** — FastAPI, PostgreSQL 15, Docker Compose
**Frontend** — Next.js 14 (App Router), TypeScript, Tailwind CSS (CRT terminal aesthetic)
**Infrastructure** — Nginx reverse proxy with path-based routing, PM2 process manager, Let's Encrypt TLS

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Game rules and welcome |
| `GET` | `/start` | Start a new session |
| `GET` | `/status` | Check current progress |
| `GET` | `/room/{room_id}` | Fetch room clue |
| `POST` | `/room/{room_id}` | Submit an answer |

### Quick taste

```bash
# Start a session
curl https://escape.xviilab.com/api/start

# Submit an answer to room 1
curl -X POST https://escape.xviilab.com/api/room/1 \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: <your-session-id>" \
  -d '{"answer": "..."}'
```

## Project Structure

```
escape-the-api/
├── escape_api/          # FastAPI backend
├── escape_terminal/     # Next.js frontend (CRT terminal UI)
├── docker-compose.yml   # Backend + Postgres
├── seed.sql             # Room data
└── client.py            # Optional terminal-based client
```

## Local Development

**Prerequisites:** Docker, Docker Compose, Node.js 18+

### Backend + Database

```bash
docker compose up -d --build
docker compose exec -T db psql -U postgres -d escape_db < seed.sql
# API → http://localhost:8000
```

### Frontend

```bash
cd escape_terminal
npm install
npm run dev
# UI → http://localhost:3000
```

## Environment Variables

**Backend** (`.env` at root)

| Variable | Default | Description |
|---|---|---|
| `ADMIN_KEY` | `change-me-in-production` | Admin endpoint auth |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `SESSION_REQUEST_LIMIT` | `150` | Max requests per session |

**Frontend** (`escape_terminal/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## Production Deployment

Deployed on a single Ubuntu VPS:

- **Nginx** reverse proxy with path-based routing — `/api/*` → FastAPI, `/*` → Next.js
- **Docker Compose** runs backend + Postgres, bound to localhost only
- **PM2** manages the Next.js process
- **Let's Encrypt** (via Certbot) handles TLS renewal

## License

MIT

## Author

Built by **Burak Yıldırım** — [github.com/xviiburaklab](https://github.com/xviiburaklab)
