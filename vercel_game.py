"""Stateless game API: authenticate JSON saves and replay in isolated workers."""
import base64
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
SAVE_VERSION = 1
MAX_ACTIONS = 3000
SAVE_TTL = 7 * 24 * 60 * 60


class InvalidSave(ValueError):
    pass


def secret_key():
    key = os.environ.get('NOMAD_SAVE_SECRET', '')
    if len(key) < 32:
        raise RuntimeError('NOMAD_SAVE_SECRET must be configured with at least 32 characters')
    return key.encode()


def encode_save(save, key):
    payload = base64.urlsafe_b64encode(json.dumps(save, separators=(',', ':')).encode()).decode()
    signature = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return payload + '.' + signature


def decode_save(token, key):
    if not isinstance(token, str) or len(token) > 60000:
        raise InvalidSave('Invalid save')
    try:
        payload, signature = token.rsplit('.', 1)
        expected = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise InvalidSave('Save signature is invalid')
        save = json.loads(base64.b64decode(payload, altchars=b'-_', validate=True))
        if (not isinstance(save, dict) or save.get('version') != SAVE_VERSION
                or type(save.get('seed')) is not int
                or type(save.get('created')) is not int
                or not isinstance(save.get('history'), list)
                or len(save['history']) > MAX_ACTIONS
                or any(not isinstance(x, str) or len(x) > 20 for x in save['history'])):
            raise InvalidSave('Save format is unsupported')
        if not 0 <= time.time() - save['created'] <= SAVE_TTL:
            raise InvalidSave('Save expired. Start a new journey.')
        return save
    except (ValueError, TypeError, KeyError) as exc:
        raise InvalidSave(str(exc)) from exc


def replay(save):
    with tempfile.TemporaryDirectory(prefix='nomad-turn-') as directory:
        process = subprocess.run(
            [sys.executable, str(ROOT / 'replay_worker.py')], cwd=ROOT,
            env={**os.environ, 'NOMAD_STATE_DIR': directory},
            input=json.dumps(save), text=True, encoding='utf-8',
            capture_output=True, timeout=20,
        )
    if process.returncode:
        raise RuntimeError('The game could not reconstruct this turn')
    return json.loads(process.stdout)


def handle(operation, data):
    key = secret_key()
    if operation == 'game':
        save = dict(version=SAVE_VERSION, seed=secrets.randbits(64),
                    created=int(time.time()), history=[])
        state = replay(save)
    else:
        save = decode_save(data.get('save'), key)
        state = replay(save)
        if operation == 'action':
            action = data.get('action')
            if (state['status'] != 'playing' or data.get('revision') != state['revision']
                    or action not in [option['id'] for option in state['options']]):
                raise InvalidSave('Invalid or stale action')
            if len(save['history']) >= MAX_ACTIONS:
                raise InvalidSave('Journey limit reached. Start a new game.')
            save['history'].append(action)
            state = replay(save)
        elif operation != 'state':
            raise InvalidSave('Unknown operation')
    state['save'] = encode_save(save, key)
    return state


class VercelHandler(BaseHTTPRequestHandler):
    operation = None

    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.respond(415, {'error': 'Expected JSON'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536:
                raise ValueError('Invalid request size')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected an object')
            self.respond(200, handle(self.operation, data))
        except (ValueError, TypeError) as exc:
            self.respond(400, {'error': str(exc)})
        except (RuntimeError, subprocess.TimeoutExpired, OSError):
            self.respond(503, {'error': 'Game unavailable. Check deployment configuration or try again.'})

    def do_GET(self):
        self.respond(405, {'error': 'Use POST'})
