"""Standalone read-only localhost server for MetStat vNext r4 UI preview.

Only serves the documented demo routes and an exact allowlist of static files.
No writes, no network calls, no hosting deployment, no authentication claims.
Usage: python preview_server.py --port 8063; http://127.0.0.1:8063/
"""
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / 'route_catalog.json').read_text(encoding='utf-8'))
ROUTES = {entry['path'] for entry in CATALOG}
ALIASES = {
    '/monitoring-forecast/weather-models/online-maps',
    '/forecast-verification',
    '/rainfall-isohyet',
    '/flash-flood',
}
ALLOWED = {
    '/styles.css',
    '/app.js',
    '/account-r4.js',
    '/drawing-r4.js',
    '/palette-data.js',
    '/route-data.js',
    '/palettes.json',
    '/route_catalog.json',
    '/assets/homepage_atmosphere.webp',
}


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if '\\' in path or '\0' in path or '..' in path.split('/'):
            self.send_error(404, 'Not found')
            return
        path = path.rstrip('/') or '/'
        if path in ROUTES or path in ALIASES or path == '/index.html':
            file = ROOT / 'index.html'
            mimetype = 'text/html; charset=utf-8'
        elif path in ALLOWED:
            file = ROOT / path.lstrip('/')
            mimetype = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
        else:
            self.send_error(404, 'Unknown preview route')
            return
        try:
            content = file.read_bytes()
        except FileNotFoundError:
            self.send_error(404, 'Missing preview resource')
            return
        self.send_response(200)
        self.send_header('Content-Type', mimetype)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt, *args):
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8063)
    args = parser.parse_args()
    if args.host not in {'127.0.0.1', 'localhost'}:
        parser.error('This preview is intentionally localhost only')
    print(f'MetStat UI-only preview: http://127.0.0.1:{args.port}', flush=True)
    print('No live model data or cPanel integration is provided.', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), PreviewHandler).serve_forever()