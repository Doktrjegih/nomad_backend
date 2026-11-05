"""Serverless saves must survive separate workers and reject tampering."""
import secrets
import time

import pytest
from vercel_game import InvalidSave, decode_save, encode_save, handle


@pytest.fixture
def key(monkeypatch):
    key = secrets.token_hex(32)
    monkeypatch.setenv('NOMAD_SAVE_SECRET', key)
    return key.encode()


def click(state, label):
    option = next(o for o in state['options'] if label in o['label'])
    return handle('action', dict(save=state['save'], revision=state['revision'], action=option['id']))


def test_turns_and_restore_work_across_disposable_workers(key):
    state = handle('game', {})
    state = click(state, 'enter tavern')
    state = click(state, 'take a beer')
    assert state['player']['gold'] == 5
    assert state['player']['drunk'] == 10
    assert handle('state', {'save': state['save']}) == state
    state = click(state, 'exit game')
    state = click(state, 'Yes')
    assert state['status'] == 'finished'
    assert handle('state', {'save': state['save']}) == state


def test_tampered_expired_and_wrong_version_saves_are_rejected(key):
    save = dict(version=1, created=int(time.time()), seed=42, history=[])
    token = encode_save(save, key)
    assert decode_save(token, key) == save
    with pytest.raises(InvalidSave):
        decode_save(token[:-1] + ('a' if token[-1] != 'a' else 'b'), key)
    for changes in [dict(created=0), dict(version=99), dict(history=[{}])]:
        with pytest.raises(InvalidSave):
            decode_save(encode_save({**save, **changes}, key), key)


def test_stale_action_does_not_create_another_turn(key):
    state = handle('game', {})
    with pytest.raises(InvalidSave):
        handle('action', dict(save=state['save'], revision=0, action='1'))
    assert handle('state', dict(save=state['save'])) == state


def test_missing_signing_key_fails_closed(monkeypatch):
    monkeypatch.delenv('NOMAD_SAVE_SECRET', raising=False)
    with pytest.raises(RuntimeError, match='NOMAD_SAVE_SECRET'):
        handle('game', {})
