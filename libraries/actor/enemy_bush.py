# -*- coding: utf-8 -*-

import operator
from functools import reduce

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .baseenemy import BaseEnemy
from .baseactor import ACTOR_Y_OFFSET

from libraries.config import *


class BushEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["bush.png"]))
        self.setSpriteCenter(False, False)
        self.setSpriteOtherOffset(ACTOR_Y_OFFSET, y = 0)
        self.Schedule(self.updateBushCollision, 1)
        self.base_layer = BUSH_LAYER
        self.removeShadow()
        
    def updateBushCollision(self):
        tile = self.mappe.getMapTileAtPos(*self.getPos())
        if tile:
            tile.setCollision(True)
        
    #overwritten stuff
    
    def stunEnemy(self, *args, **kwargs):
        pass #skip this
    
    def setHurt(self, *args, **kwargs):
        super().setHurt(*args, **kwargs)
        tile = self.mappe.getMapTileAtPos(*self.getPos())
        if tile:
            tile.setCollision(False)
        
        