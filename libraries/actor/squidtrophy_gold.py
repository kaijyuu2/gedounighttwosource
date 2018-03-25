# -*- coding: utf-8 -*-

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .squidtrophy_base import SquidTrophyBase

from libraries.audio import playSound

from libraries.config import *


class SquidTrophyGold(SquidTrophyBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparkle_graphic_list = ["sparkle1_gold.png","sparkle2_gold.png"]
        self.squid_trophy_index = SQUID_TROPHY_GOLD_INDEX
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["squid_trophy_gold.png"]))
        
    def collectSquid(self):
        playSound(SOUND_COLLECT_SQUID, True)
        customEvent(FINAL_SQUID_OBTAINED_EVENT )
        self.cleanupSelf()