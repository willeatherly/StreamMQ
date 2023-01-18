#!/usr/bin/env python3
from contextlib import contextmanager
import obspython as obs
import time

print("Loading")

# auto release context managers
# fantastically helpful, from upgradeQ
# https://github.com/upgradeQ/Scripted-text/blob/master/scripted_text.py
@contextmanager
def source_ar(source_name):
    source = obs.obs_get_source_by_name(source_name)
    try:
        yield source
    finally:
        obs.obs_source_release(source)


@contextmanager
def p_source_ar(id, source_name, settings):
    try:
        _source = obs.obs_source_create_private(id, source_name, settings)
        yield _source
    finally:
        obs.obs_source_release(_source)


@contextmanager
def data_ar(source_settings=None):
    if not source_settings:
        settings = obs.obs_data_create()
    if source_settings:
        settings = obs.obs_source_get_settings(source_settings)
    try:
        yield settings
    finally:
        obs.obs_data_release(settings)


@contextmanager
def scene_ar(scene):
    scene = obs.obs_scene_from_source(scene)
    try:
        yield scene
    finally:
        obs.obs_scene_release(scene)


@contextmanager
def filter_ar(source, name):
    source = obs.obs_source_get_filter_by_name(source, name)
    try:
        yield source
    finally:
        obs.obs_source_release(source)


# Description displayed in the Scripts dialog window
def script_description():
    return """Hack Fortress OBS Update with purchased upgrades"""


class HackEffectRequest:
    """
    #Hack Effect Request
    #routing key: purchase.effect.tf2
    {
        "from_team": <"1" if red | "2" if blue>, # Requesting team
        "to_team": <"1" if red | "2" if blue>, # Affected team
        "num_players": <value between 1 - 6>, # Number of player affected
        "value": <effect value>,
        "effect_name": <effect name>, # Pre-negotiated name of effect
                                      # List in purchase.rb in hack scoreboard
                                      # list in <??> in tf2 scoreboard
        "delay": <amount of seconds to delay effect from occurring>
    }
    """

    def __init__(self, event) -> None:
        self.from_team = event["from_team"]
        self.to_team = event["to_team"]
        self.num_players = event["num_players"]
        self.value = event["value"]
        self.effect_name = event["effect_name"]
        self.delay = event["delay"]

    def __str__(self) -> str:
        if self.to_team == self.from_team:
            return f'{"Red" if self.from_team == "1" else "Blue"} team hackers granted {self.effect_name} to {self.num_players} gamer{"s" if self.num_players > 1 else ""}'
        else:
            return f'{"Red" if self.from_team == "1" else "Blue"} team hackers used {self.effect_name} against {self.num_players} rival gamer{"" if self.num_players == "1" else "s"}'


class HackFortressPurchaseText:
    source_name = None

    def __init__(self, source_name):
        self.source_name = source_name

    def update_text(self, text):
        with source_ar(self.source_name) as source, data_ar() as settings:
            obs.obs_data_set_string(settings, "text", text)
            obs.obs_source_update(source, settings)

    def update_lines(self, lines):
        text = "\n".join(lines)
        self.update_text(text)


def script_load(settings):
    test_events = [
        str(
            HackEffectRequest(
                {
                    "from_team": "1",
                    "to_team": "2",
                    "num_players": "6",
                    "value": "400",
                    "effect_name": "fire",
                    "delay": "5",
                }
            )
        )
    ]
    hf = HackFortressPurchaseText("HackFortressPurchaseUpdates")
    hf.update_text("hello world")
    time.sleep(5)
    hf.update_lines(test_events)
