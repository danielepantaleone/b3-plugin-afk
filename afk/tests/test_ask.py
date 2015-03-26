# -*- encoding: utf-8 -*-
from textwrap import dedent
from time import sleep
from afk.tests import *
from mock import call, Mock

# This test suite makes sure `kick_client` is called appropriately when `ask_client` is run


@pytest.yield_fixture
def plugin(console):
    p = None
    with logging_disabled():
        p = plugin_maker_ini(console, dedent("""
            [settings]
            consecutive_deaths_threshold: 3
            inactivity_threshold: 30s
            kick_reason: AFK for too long on this server
            are_you_afk: Are you AFK?
        """))
        plugin.inactivity_threshold_second = 0
        p.MIN_INGAME_PLAYERS = 0  # disable this check by default
        p.kick_client = Mock()
        p.onLoadConfig()
        p.onStartup()
    yield p
    p.disable()


def test_ask(plugin, joe):
    # GIVEN
    joe.message = Mock()
    # WHEN
    plugin.ask_client(joe)
    # THEN
    assert [call('Are you AFK?')] == joe.message.mock_calls
    assert joe in plugin.kick_timers


def test_no_response(plugin, joe):
    # GIVEN
    plugin.last_chance_delay = .005
    joe.message = Mock()
    joe.connects(1)
    # WHEN
    plugin.ask_client(joe)
    # THEN
    assert [call('Are you AFK?')] == joe.message.mock_calls
    # WHEN
    sleep(.01)
    # THEN
    assert [call(joe)] == plugin.kick_client.mock_calls


def test_response(plugin, joe):
    # GIVEN
    plugin.last_chance_delay = .005
    joe.message = Mock()
    joe.connects(1)
    # WHEN
    plugin.ask_client(joe)
    # THEN
    assert [call('Are you AFK?')] == joe.message.mock_calls
    # WHEN
    joe.says("hi")
    assert joe not in plugin.kick_timers
    sleep(.01)
    # THEN
    assert [] == plugin.kick_client.mock_calls
    assert joe not in plugin.kick_timers


def test_make_kill(plugin, joe):
    # GIVEN
    plugin.last_chance_delay = .005
    joe.message = Mock()
    joe.connects(1)
    # WHEN
    plugin.ask_client(joe)
    # THEN
    assert [call('Are you AFK?')] == joe.message.mock_calls
    # WHEN
    joe.kills(joe)
    assert joe not in plugin.kick_timers
    sleep(.01)
    assert [] == plugin.kick_client.mock_calls
