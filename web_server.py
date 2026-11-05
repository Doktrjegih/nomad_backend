"""Local browser server. Each browser session runs in its own game process."""
import argparse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import selectors
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parent


class Game:
    def __init__(self):
        self.lock = threading.Lock()
        self.touched = time.monotonic()
        self.directory = Path(tempfile.mkdtemp(prefix='nomad-web-'))
        self.error_log = (self.directory / 'worker-error.log').open('w')
        self.process = subprocess.Popen(
            [sys.executable, '-u', str(ROOT / 'web_worker.py')], cwd=ROOT,
            env={**os.environ, 'NOMAD_STATE_DIR': str(self.directory)},
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.error_log,
            text=True, encoding='utf-8',
        )
        try:
            self.state = self.receive()
        except Exception:
            self.close()
            raise

    def receive(self):
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            if not selector.select(timeout=10):
                raise TimeoutError('The game took too long to respond')
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError('Game process stopped')
        return json.loads(line)

    def act(self, revision, action):
        with self.lock:
            self.touched = time.monotonic()
            if self.state['status'] != 'playing':
                raise ValueError('This game has ended')
            if revision != self.state['revision'] or action not in {x['id'] for x in self.state['options']}:
                raise ValueError('Action is invalid or out of date; refresh the game')
            self.process.stdin.write(json.dumps(dict(action=action, revision=revision)) + '\n')
            self.process.stdin.flush()
            try:
                self.state = self.receive()
            except Exception:
                self.close()
                raise
            return self.state

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()
        self.error_log.close()
        shutil.rmtree(self.directory, ignore_errors=True)


class GameServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, Handler)
        self.games = {}
        self.games_lock = threading.Lock()

    def server_close(self):
        with self.games_lock:
            for game in self.games.values():
                game.close()
            self.games.clear()
        super().server_close()


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, value, cookie=None):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if cookie:
            self.send_header('Set-Cookie', f'nomad={cookie}; HttpOnly; SameSite=Strict; Path=/')
        self.end_headers()
        self.wfile.write(body)

    def token(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
            return cookie['nomad'].value if 'nomad' in cookie else None
        except Exception:
            return None

    def do_GET(self):
        if self.path == '/':
            body = (ROOT / 'web' / 'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/state':
            with self.server.games_lock:
                game = self.server.games.get(self.token())
                if game:
                    game.touched = time.monotonic()
            if not game:
                self.reply(404, {'error': 'Start a new journey'})
            else:
                with game.lock:
                    self.reply(200, game.state)
        else:
            self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        # JSON-only writes plus same-origin checks keep cross-site forms out.
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.reply(415, {'error': 'Expected JSON'})
            return
        origin = self.headers.get('Origin')
        if origin and origin not in (f"http://{self.headers.get('Host')}", f"https://{self.headers.get('Host')}"):
            self.reply(403, {'error': 'Origin not allowed'})
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                raise ValueError('Invalid request size')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Expected an object')
            if self.path == '/api/game':
                with self.server.games_lock:
                    now = time.monotonic()
                    for token, game in list(self.server.games.items()):
                        if now - game.touched > 1800 or token == self.token():
                            with game.lock:
                                game.close()
                            del self.server.games[token]
                    if len(self.server.games) >= 16:
                        self.reply(503, {'error': 'All journeys are busy. Try later.'})
                        return
                    token = secrets.token_urlsafe(32)
                    game = Game()
                    self.server.games[token] = game
                self.reply(201, game.state, cookie=token)
            elif self.path == '/api/action':
                with self.server.games_lock:
                    game = self.server.games.get(self.token())
                if not game:
                    self.reply(404, {'error': 'Session expired. Start a new journey.'})
                else:
                    self.reply(200, game.act(data.get('revision'), data.get('action')))
            else:
                self.reply(404, {'error': 'Not found'})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.reply(400, {'error': str(exc)})
        except (RuntimeError, TimeoutError, OSError):
            self.reply(500, {'error': 'Game unavailable. Start a new journey.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = GameServer((args.host, args.port))
    print(f'Nomad web server listening on port {server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
