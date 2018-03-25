# -*- coding: utf-8 -*-

from kaiengine.resource import toStringPath

from .squidtrophy_base import SquidTrophyBase

from libraries.config import *

class SquidTrophyGreen(SquidTrophyBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparkle_graphic_list = ["sparkle1_green.png","sparkle2_green.png"]
        self.squid_trophy_index = SQUID_TROPHY_GREEN_INDEX
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["squid_trophy_green.png"]))