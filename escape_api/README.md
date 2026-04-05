# Escape API (Backend)
FastAPI backend for the Terminal Escape Game.

## Requirements
- Python 3.9+
- PostgreSQL

## Setup
1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy `.env.example` to `.env` and set up database connection:
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/escape_db"
ADMIN_KEY="your-secret-key"
```
4. Start the server:
```bash
uvicorn main:app --reload
```

## Admin API Examples

Create a room (Requires X-Admin-Key header):
```bash
curl -X POST "http://localhost:8000/admin/rooms" \
     -H "X-Admin-Key: your-secret-key" \
     -H "Content-Type: application/json" \
     -d '{"type": "cipher", "title": "First Gate", "clue": "Uryyb Jbeyq", "answer": "Hello World", "room_order": 1, "active": true}'
```

Get all players:
```bash
curl -X GET "http://localhost:8000/admin/sessions" \
     -H "X-Admin-Key: your-secret-key"
```
