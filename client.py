#!/usr/bin/env python3
"""
Escape Terminal — CLI Client
Usage: python client.py
Set ESCAPE_API_URL to override server (default: http://localhost:8000)
"""
import os
import json
import base64
import urllib.request
import urllib.error
import urllib.parse

C = {
    "green":  "\033[92m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".escape_session")
BASE_URL = os.getenv("ESCAPE_API_URL", "http://localhost:8000").rstrip("/")

BANNER = """\033[96m\033[1m
  +----------------------------------------------+
  |        E S C A P E   T E R M I N A L        |
  +----------------------------------------------+
\033[0m"""


# ── Session storage ──────────────────────────────────────────────────────────

def _load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return f.read().strip()
    return None


def _save_session(sid):
    with open(SESSION_FILE, "w") as f:
        f.write(sid)


def _clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


# ── HTTP helper ───────────────────────────────────────────────────────────────

def api(method, path, body=None, extra_headers=None, query=None):
    url = f"{BASE_URL}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)

    headers = {"Content-Type": "application/json"}
    sid = _load_session()
    if sid:
        headers["X-Session-Id"] = sid
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            try:
                return json.loads(raw), resp_headers, resp.status
            except Exception:
                return raw, resp_headers, resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        resp_headers = {k.lower(): v for k, v in e.headers.items()}
        try:
            return json.loads(raw), resp_headers, e.code
        except Exception:
            return raw, resp_headers, e.code
    except urllib.error.URLError:
        print(f"{C['red']}Cannot reach server at {BASE_URL}{C['reset']}")
        print(f"{C['dim']}Make sure the server is running (docker compose up or uvicorn main:app){C['reset']}")
        return None, {}, 0


def _get_current_room():
    data, _, _ = api("GET", "/status")
    if data and isinstance(data, dict) and "current_room" in data:
        return data["current_room"]
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args):
    difficulty = args[0] if args and args[0] in ("easy", "hard") else "easy"
    data, _, _ = api("GET", f"/start?difficulty={difficulty}")
    if not data:
        return
    if isinstance(data, dict) and data.get("session_id"):
        _save_session(data["session_id"])
        print(f"\n{C['green']}Session started!{C['reset']}")
        print(f"  ID         : {C['dim']}{data['session_id']}{C['reset']}")
        print(f"  Difficulty : {C['yellow']}{data.get('difficulty', 'easy')}{C['reset']}")
        print(f"\n{C['dim']}{data.get('instruction', '')}{C['reset']}\n")
    else:
        detail = data.get("detail", data) if isinstance(data, dict) else data
        print(f"{C['red']}{detail}{C['reset']}")


def cmd_status():
    data, _, _ = api("GET", "/status")
    if not data:
        return
    if isinstance(data, dict) and "detail" in data:
        print(f"{C['red']}{data['detail']}{C['reset']}")
        return
    completed = data.get("completed_at") or "Not yet"
    req_count = data.get("request_count", 0)
    req_limit = data.get("request_limit", "?")
    print(f"""
{C['bold']}Session Status{C['reset']}
  ID           : {C['dim']}{data.get('id', '?')}{C['reset']}
  Started      : {data.get('started_at', '?')}
  Completed    : {completed}
  Current Room : {C['yellow']}Room {data.get('current_room', '?')}{C['reset']}
  Requests     : {req_count} / {req_limit}
  Difficulty   : {data.get('difficulty', 'easy')}
""")


def cmd_room():
    room_id = _get_current_room()
    if room_id is None:
        print(f"{C['red']}No active session. Use 'start' first.{C['reset']}")
        return

    data, headers, _ = api("GET", f"/room/{room_id}")
    if not data:
        return
    if isinstance(data, dict) and "detail" in data:
        print(f"{C['red']}{data['detail']}{C['reset']}")
        return

    print(f"\n{C['bold']}{C['yellow']}--- Room {room_id} ---{C['reset']}")
    if isinstance(data, dict):
        if data.get("title"):
            print(f"{C['bold']}{data['title']}{C['reset']}\n")
        if data.get("clue"):
            print(data["clue"])
        if data.get("hint"):
            print(f"\n{C['dim']}Hint: {data['hint']}{C['reset']}")
        hidden = headers.get("x-hidden-clue")
        if hidden:
            print(f"\n{C['cyan']}[Response header detected — x-hidden-clue: {hidden}]{C['reset']}")
    print()


def cmd_answer(args):
    """
    answer <text>               POST {"answer": text}
    answer --base64 <text>      POST with x-secret-base: base64(text) header
    answer --method <METHOD>    Send with specified HTTP method (DELETE, PUT, etc.)
    answer --ua <user-agent>    POST with custom User-Agent header
    answer --key <text>         POST with ?key=text query param
    answer --nested <text>      POST {"secret": {"key": text}}
    """
    if not args:
        print(f"{C['red']}Usage: answer <text>  (or with a flag, see 'help'){C['reset']}")
        return

    room_id = _get_current_room()
    if room_id is None:
        print(f"{C['red']}No active session. Use 'start' first.{C['reset']}")
        return

    method = "POST"
    body = None
    extra_headers = {}
    query = None

    if args[0].startswith("--"):
        flag = args[0]
        value = " ".join(args[1:])
        if not value:
            print(f"{C['red']}Flag {flag} requires a value.{C['reset']}")
            return
        if flag == "--base64":
            extra_headers["x-secret-base"] = base64.b64encode(value.encode()).decode()
            body = {"answer": value}
        elif flag == "--method":
            method = value.upper()
            body = {"answer": value}
        elif flag == "--ua":
            extra_headers["User-Agent"] = value
            body = {"answer": value}
        elif flag == "--key":
            query = {"key": value}
            body = {"answer": value}
        elif flag == "--nested":
            body = {"secret": {"key": value}}
        else:
            print(f"{C['red']}Unknown flag: {flag}. See 'help'.{C['reset']}")
            return
    else:
        body = {"answer": " ".join(args)}

    data, _, _ = api(method, f"/room/{room_id}", body=body, extra_headers=extra_headers, query=query)
    if not data:
        return
    if isinstance(data, dict):
        msg = data.get("message", str(data))
        if any(kw in msg for kw in ("Correct", "proceed", "Congratulations", "escaped")):
            print(f"\n{C['green']}{msg}{C['reset']}\n")
        else:
            print(f"\n{C['red']}{msg}{C['reset']}")
        if data.get("hint"):
            print(f"{C['dim']}Hint: {data['hint']}{C['reset']}")
    print()


def cmd_reset():
    if not _load_session():
        print(f"{C['yellow']}No active session.{C['reset']}")
        return
    confirm = input(f"{C['yellow']}Delete current session? (y/N): {C['reset']}").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    data, _, _ = api("DELETE", "/session")
    _clear_session()
    if data:
        msg = data.get("message", str(data)) if isinstance(data, dict) else str(data)
        print(f"{C['green']}{msg}{C['reset']}")


def print_help():
    print(f"""
{C['bold']}Commands:{C['reset']}
  {C['cyan']}start{C['reset']} [easy|hard]           Start a new session
  {C['cyan']}status{C['reset']}                       Show session progress
  {C['cyan']}room{C['reset']}                         Show current room clue
  {C['cyan']}answer{C['reset']} <text>                Submit plain answer
  {C['cyan']}answer --base64{C['reset']} <text>       Send base64-encoded in x-secret-base header
  {C['cyan']}answer --method{C['reset']} <METHOD>     Send request with specified HTTP method
  {C['cyan']}answer --ua{C['reset']} <user-agent>     Send with custom User-Agent header
  {C['cyan']}answer --key{C['reset']} <text>          Add ?key=text to the request URL
  {C['cyan']}answer --nested{C['reset']} <text>       Send {{"secret": {{"key": text}}}}
  {C['cyan']}reset{C['reset']}                        Delete current session
  {C['cyan']}help{C['reset']}                         Show this help
  {C['cyan']}quit{C['reset']} / exit                  Exit
""")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print(BANNER)
    print(f"{C['dim']}Server: {BASE_URL}{C['reset']}")
    sid = _load_session()
    if sid:
        print(f"{C['dim']}Resuming session: {sid[:8]}...{C['reset']}")
    print()

    while True:
        try:
            line = input(f"{C['green']}escape> {C['reset']}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C['dim']}Goodbye.{C['reset']}")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "exit", "q"):
            print(f"{C['dim']}Goodbye.{C['reset']}")
            break
        elif cmd == "help":
            print_help()
        elif cmd == "start":
            cmd_start(args)
        elif cmd == "status":
            cmd_status()
        elif cmd == "room":
            cmd_room()
        elif cmd == "answer":
            cmd_answer(args)
        elif cmd == "reset":
            cmd_reset()
        else:
            print(f"{C['red']}Unknown command: '{cmd}'. Type 'help'.{C['reset']}")


if __name__ == "__main__":
    main()
