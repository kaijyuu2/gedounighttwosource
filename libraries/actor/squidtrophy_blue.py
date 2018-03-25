# -*- coding: utf-8 -*-

from kaiengine.resource import toStringPath

from .squidtrophy_base import SquidTrophyBase

from libraries.config import *


class SquidTrophyBlue(SquidTrophyBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparkle_graphic_list = ["sparkle1_blue.png","sparkle2_blue.png"]
        self.squid_trophy_index = SQUID_TROPHY_BLUE_INDEX
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["squid_trophy_blue.png"]))
        