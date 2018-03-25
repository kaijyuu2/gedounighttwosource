# -*- coding: utf-8 -*-

from kaiengine.gconfig import *

from .local_keybinds import *
from .datakeys import *
from .paths import *
from .layers import *
from .customevents import *
from .soundeffects import *
from .savekeys import *

DYNAMIC_SETTINGS_DEFAULTS = {DYNAMIC_SETTINGS_GAME_CAPTION: "Gedou Night 2", #overwrite defaults here
                    DYNAMIC_SETTINGS_KEY_BINDS: KEY_BINDS,
                    DYNAMIC_SETTINGS_WINDOW_DIMENSIONS: [256,224],
                    DYNAMIC_SETTINGS_GLOBAL_SCALING:3,
                    DYNAMIC_SETTINGS_DEBUG_ON: True,
                    DYNAMIC_SETTINGS_FPS_ON: False}


MAP_TILE_SIZE = 16
MAP_SIZE = (256, 224)
MAP_SIZE_TILES = (int(MAP_SIZE[0]/MAP_TILE_SIZE), int(MAP_SIZE[1]/MAP_TILE_SIZE))

DIRECTION_UP = 0 #enum for directions
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3


#enemy enum
PLAYER_FORM_INDEX = "char"
ENEMY_BAT_INDEX = "bat"
ENEMY_MINOTAUR_INDEX = "minotaur"
ENEMY_SKELETON_INDEX = "skeleton"
ENEMY_BUSH_INDEX = "bush"
ENEMY_BARRICADE_INDEX = "barricade"
ENEMY_SQUID_DOOR_INDEX = "squiddoor"
ENEMY_SAVE_INDEX = "save"

#squid trophy enum
SQUID_TROPHY_GOLD_INDEX = "gold"
SQUID_TROPHY_RED_INDEX = "red"
SQUID_TROPHY_BLUE_INDEX = "blue"
SQUID_TROPHY_GREEN_INDEX = "green"


SKELETON_ANI_DICT = {DIRECTION_UP:(("SLASH_WINDUP_UP", "SLASH_UP"), False),
                     DIRECTION_DOWN:(("SLASH_WINDUP_DOWN", "SLASH_DOWN"), False),
                     DIRECTION_LEFT:(("SLASH_WINDUP_SIDE", "SLASH_SIDE"), True),
                     DIRECTION_RIGHT:(("SLASH_WINDUP_SIDE", "SLASH_SIDE"), False)}

ACTOR_MOVEMENT_ANIMATION_DICT = {
        DIRECTION_UP: {True:("WALK_UP", False), False:("IDLE_UP", False)},
        DIRECTION_DOWN: {True:("WALK_DOWN", False), False:("IDLE_DOWN", False)},
        DIRECTION_RIGHT: {True:("WALK_SIDE", False), False:("IDLE_SIDE", False)},
        DIRECTION_LEFT: {True:("WALK_SIDE", True), False:("IDLE_SIDE", True)}}
