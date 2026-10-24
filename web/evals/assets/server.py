"""Dev server for the device dashboard: serves the files beside it and a JSON
API. Every request is appended to requests.log as "METHOD path"."""

import json
import os
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
TAGS = ["edge", "core", "lab", "field", "spare", "north", "south", "east",
        "west", "indoor", "outdoor", "battery", "mains", "solar", "beta",
        "legacy", "pilot", "eu", "us", "apac"]
DEVICES = [{"id": i, "name": f"device-{(i * 7919) % 2000:04d}",
            "tags": [TAGS[i % 20], TAGS[(i * 7) % 20], TAGS[(i * 13) % 20]]}
           for i in range(2000)]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        pass

    def record(self):
        with open(os.path.join(ROOT, "requests.log"), "a") as f:
            f.write(f"{self.command} {self.path}\n")

    def send_json(self, body, status=200):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.record()
        path = self.path.split("?")[0]
        if path == "/api/user":
            return self.send_json({"name": "Ada"})
        if path == "/api/status":
            return self.send_json({"incidents": 2})
        if path == "/api/notice":
            time.sleep(0.4)
            return self.send_json({"text": "Maintenance on Sunday, 02:00-04:00 UTC."})
        if path == "/api/devices":
            return self.send_json(DEVICES)
        if path == "/api/device-status":
            return self.send_json({d["id"]: "online" if d["id"] % 9 else "offline"
                                   for d in DEVICES})
        if path.startswith("/api/device/"):
            i = int(path.rsplit("/", 1)[1])
            return self.send_json({**DEVICES[i],
                                   "samples": [(i * k) % 97 for k in range(100000)]})
        return super().do_GET()

    def do_POST(self):
        self.record()
        if self.path == "/api/settings":
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(204)
            self.end_headers()
            return
        self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8138"))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
