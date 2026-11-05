"""Exercise browser buttons through the real isolated game worker and HTTP API."""
import json
import threading
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

import pytest
from web_server import GameServer


@pytest.fixture
def server():
    server = GameServer(('127.0.0.1', 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


class Browser:
    def __init__(self, server):
        self.base = f'http://127.0.0.1:{server.server_port}'
        self.client = build_opener(HTTPCookieProcessor(CookieJar()))
        self.state = None

    def request(self, path, body=None):
        request = Request(self.base + path,
                          data=None if body is None else json.dumps(body).encode(),
                          headers={} if body is None else {'Content-Type': 'application/json'})
        with self.client.open(request, timeout=15) as response:
            return json.load(response)

    def start(self):
        self.state = self.request('/api/game', {})
        return self.state

    def click(self, label):
        choice = next(option for option in self.state['options'] if label in option['label'])
        self.state = self.request('/api/action', {'revision': self.state['revision'], 'action': choice['id']})
        return self.state


def test_buttons_drive_tavern_inventory_and_exit(server):
    browser = Browser(server)
    initial = browser.start()
    assert initial['player']['health'] == 100
    assert any(o['label'] == 'enter tavern' for o in initial['options'])
    browser.click('enter tavern')
    browser.click('take a beer')
    assert browser.state['player']['gold'] == 5
    assert browser.state['player']['drunk'] == 10
    browser.click('inventory')
    assert any('Broken Spear' in o['label'] for o in browser.state['options'])
    browser.click('Cancel')
    browser.click('exit game')
    browser.click('No')
    assert browser.state['status'] == 'playing'
    browser.click('exit game')
    browser.click('Yes')
    assert browser.state['status'] == 'finished'
    assert browser.state['options'] == []


def test_sessions_and_refresh_are_isolated(server):
    first, second = Browser(server), Browser(server)
    first.start()
    second.start()
    first.click('enter tavern')
    first.click('take a beer')
    assert first.request('/api/state')['player']['gold'] == 5
    assert second.request('/api/state')['player']['gold'] == 10
    first.start()
    assert first.state['player']['gold'] == 10
    assert len(server.games) == 2


def test_stale_and_forged_actions_do_not_advance_game(server):
    browser = Browser(server)
    initial = browser.start()
    browser.click('enter tavern')
    for body in [{'revision': initial['revision'], 'action': '2'},
                 {'revision': browser.state['revision'], 'action': 'hesoyam'}]:
        with pytest.raises(HTTPError) as error:
            browser.request('/api/action', body)
        assert error.value.code == 400
    assert browser.request('/api/state') == browser.state


def test_quest_and_shop_dialogs_have_named_buttons(server):
    browser = Browser(server)
    browser.start()
    browser.click('enter tavern')
    browser.click('talk with Aleg')
    assert {o['label'] for o in browser.state['options']} == {'Yes', 'No'}
    browser.click('Yes')
    assert any('Quest has been taken' in line for line in browser.state['lines'])
    browser.click('merchant')
    browser.click('buy')
    assert any('Iron sword' in o['label'] for o in browser.state['options'])
    browser.click('Broken Spear')
    browser.click('Yes')
    assert browser.state['player']['gold'] == 7
    browser.click('Cancel')
