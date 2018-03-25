# -*- coding: utf-8 -*-

from kaiengine.event import addKeyPressListener, addKeyReleaseListener
from kaiengine.keybinds import keyMatches

from libraries.config import *

KEY_LIST = [MOVE_UP, MOVE_DOWN, MOVE_RIGHT, MOVE_LEFT]

keys_held = set()

def _registerHeld(symbol, modifiers):
    for key in KEY_LIST:
        try:
            if keyMatches(key, symbol):
                keys_held.add(key)
                break
        except NotImplementedError:
            pass
    return False

def _registerReleased(symbol, modifiers):
    for key in KEY_LIST:
        try:
            if keyMatches(key, symbol):
                try: keys_held.remove(key)
                except KeyError: pass
                break
        except NotImplementedError:
            pass
    return False


addKeyPressListener(_registerHeld, 99999999999999)
addKeyReleaseListener(_registerReleased, 999999999999999)


def checkKeyHeld(key):
    return key in keys_held

def checkRawKeyHeld(symbol):
    for key in KEY_LIST:
        try:
            if keyMatches(key, symbol):
                if checkKeyHeld(key):
                    return True
        except NotImplementedError:
            pass
    return False