"""Local research app. Python standard library only; binds loopback by default."""
import argparse
import json
import os
import secrets
import threading
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from agent import configured, explain
from guide import guide
from catalog import TESTS, public_catalog
from runner import RECORDINGS, ROOT, run, source_files

TOKEN = secrets.token_urlsafe(32)
RESULTS = OrderedDict()
LOCK = threading.Lock()
RUN_SLOTS = threading.BoundedSemaphore(4)
STATIC = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
          "/lab": ("lab.html", "text/html"), "/lab/": ("lab.html", "text/html"),
          "/lab.html": ("lab.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
          "/style.css": ("style.css", "text/css"),
          "/assets/all-in-onear.png": ("assets/all-in-onear.png", "image/png"),
          "/assets/hubble.png": ("assets/hubble.png", "image/png"),
          "/assets/near.svg": ("assets/near.svg", "image/svg+xml")}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="application/json"):
        raw = json.dumps(body, ensure_ascii=False, allow_nan=False).encode() if content_type == "application/json" else body
        self.send_response(status)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") or content_type == "application/json" else ""))
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path in STATIC:
            name, content_type = STATIC[parsed.path]
            return self.send(200, (ROOT / "web" / name).read_bytes(), content_type)
        if parsed.path == "/api/catalog":
            items = public_catalog()
            for item in items:
                item["replay_available"] = (RECORDINGS / f"{item['id']}.json").exists()
                if item["mode"] == "sandbox":
                    item["sandbox_available"], item["setup_message"] = TESTS[item["id"]]["module"].availability()
            return self.send(200, {"tests": items, "csrf_token": TOKEN, "ai_configured": configured(), "version": "0.23.0"})
        if parsed.path == "/api/source":
            test_id = parse_qs(parsed.query).get("id", [""])[0]
            try:
                files = [{"path": name, "code": (ROOT / name).read_text(encoding="utf-8")} for name in source_files(test_id)]
            except ValueError:
                return self.send(404, {"error": "Unknown experiment"})
            return self.send(200, {"files": files})
        if parsed.path == "/api/health":
            return self.send(200, {"ok": True, "version": "0.23.0"})
        return self.send(404, {"error": "Not found"})

    def do_POST(self):
        origin = self.headers.get("Origin")
        if origin and urlsplit(origin).netloc != self.headers.get("Host"):
            return self.send(403, {"error": "Cross-origin execution is not supported"})
        if self.headers.get("X-Lab-Token") != TOKEN:
            return self.send(403, {"error": "Invalid local session token"})
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self.send(415, {"error": "Expected JSON"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                return self.send(413, {"error": "Request size limit exceeded"})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            if not RUN_SLOTS.acquire(blocking=False):
                return self.send(429, {"error": "Four tasks are already running; retry shortly."})
            try:
                if self.path == "/api/run":
                    result = run(data.get("id"), data.get("mode", "live"), data.get("parameters"))
                    run_id = secrets.token_hex(12)
                    with LOCK:
                        RESULTS[run_id] = result
                        if len(RESULTS) > 30:
                            RESULTS.popitem(last=False)
                    return self.send(200, {"run_id": run_id, **result})
                if self.path == "/api/guide":
                    run_id = data.get("run_id")
                    with LOCK:
                        result = RESULTS.get(run_id) if isinstance(run_id, str) else None
                    if run_id is not None and result is None:
                        raise ValueError("Result expired; run the experiment again")
                    return self.send(200, guide(data.get("question"), data.get("completed", []),
                                               data.get("provider", "local"), result))
                if self.path == "/api/explain":
                    with LOCK:
                        result = RESULTS.get(data.get("run_id"))
                    if result is None:
                        raise ValueError("Result expired; run the experiment again")
                    return self.send(200, explain(result))
                return self.send(404, {"error": "Not found"})
            finally:
                RUN_SLOTS.release()
        except (ValueError, KeyError, TypeError) as error:
            return self.send(400, {"error": str(error)[:220]})
        except (RuntimeError, OSError) as error:
            return self.send(502, {"error": str(error)[:220]})
        except Exception:
            return self.send(500, {"error": "Unexpected response; no result was substituted. Check the source schema."})

    def log_message(self, format_string, *args):
        if "/api/explain" not in self.path:
            super().log_message(format_string, *args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8765")))
    parser.add_argument("--strictPort", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"All in oNEar: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
