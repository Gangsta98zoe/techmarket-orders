#!/usr/bin/env python3
import http.server, os, sys

PORT = int(os.environ.get("PORT", 8080))
BASE = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)
    def log_message(self, *a): pass

with http.server.HTTPServer(("", PORT), Handler) as s:
    print(f"Serving {BASE} on {PORT}", flush=True)
    s.serve_forever()
