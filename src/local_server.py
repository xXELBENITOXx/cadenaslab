"""Servidor local sin dependencias: Python + SQLite, mismo motor que Cloudflare.
Uso: python src/local_server.py ; http://localhost:8765
"""
from __future__ import annotations
import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from analysis import analyze, algorithm

DB_PATH = ROOT / '.local' / 'cadenaslab.sqlite3'
DB_PATH.parent.mkdir(exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript((ROOT / 'migrations' / '0001_init.sql').read_text(encoding='utf-8'))
    return conn


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'public'), **kwargs)

    def json_response(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == '/api/health':
            return self.json_response({'ok': True, 'engine': 'Python', 'database': 'SQLite (local)'})
        if self.path == '/api/history':
            with get_db() as db:
                rows = db.execute('SELECT * FROM analyses ORDER BY id DESC LIMIT 25').fetchall()
                return self.json_response({'items': [dict(r) for r in rows]})
        if self.path.startswith('/api/'):
            return self.json_response({'error': 'Ruta no encontrada.'}, 404)
        return super().do_GET()

    def do_POST(self):
        if self.path not in ('/api/analyze', '/api/algorithm'):
            return self.json_response({'error': 'Ruta no encontrada.'}, 404)
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length > 110_000:
                return self.json_response({'error': 'Solicitud demasiado grande.'}, 413)
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            if self.path == '/api/algorithm':
                return self.json_response(algorithm(body))
            result = analyze(body.get('text_a', ''), body.get('text_b', ''))
            if body.get('save'):
                with get_db() as db:
                    db.execute('INSERT INTO analyses (score, words_a, words_b, matched_a, matched_b, window_size) VALUES (?, ?, ?, ?, ?, ?)',
                               (result['score'], result['words_a'], result['words_b'], result['matched_words_a'], result['matched_words_b'], result['window']))
                result['saved'] = True
            else:
                result['saved'] = False
            return self.json_response(result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self.json_response({'error': str(exc)}, 400)
        except Exception:
            return self.json_response({'error': 'Error interno.'}, 500)


if __name__ == '__main__':
    with ThreadingHTTPServer(('127.0.0.1', 8765), Handler) as httpd:
        print('CadenasLab disponible en http://localhost:8765')
        httpd.serve_forever()
