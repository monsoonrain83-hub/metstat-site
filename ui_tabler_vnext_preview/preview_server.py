"""Offline-only preview server. Explicit route allowlist; no host rewrite or PHP auth bypass."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
ROUTES = {
    '/monitoring-forecast/weather-models',
    '/monitoring-forecast/weather-models/daily',
    '/monitoring-forecast/weather-models/weekly',
    '/monitoring-forecast/weather-models/monthly',
    '/monitoring-forecast/weather-models/seasonal',
    '/monitoring-forecast/weather-models/ensemble',
    '/meteorological-tools', '/synoptic-analysis', '/climate-analytics',
    '/rainfall-isohyet', '/forecast-verification', '/flash-flood',
}


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path.rstrip('/') or '/'
        if path in ROUTES:
            self.path = '/index.html'
        elif path == '/':
            self.send_response(302)
            self.send_header('Location', '/monitoring-forecast/weather-models')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        elif path not in ('/index.html', '/theme.css', '/app.js'):
            self.send_error(404, 'Unknown preview path')
            return
        super().do_GET()

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8765)
    args = p.parse_args()
    print(f'Preview server at http://127.0.0.1:{args.port}/monitoring-forecast/weather-models')
    ThreadingHTTPServer(('127.0.0.1', args.port), PreviewHandler).serve_forever()
