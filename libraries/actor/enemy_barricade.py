# -*- coding: utf-8 -*-

import operator
from functools import reduce

from libraries.audio import playSound
from libraries import gamestate

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .baseenemy import BaseEnemy
from .baseactor import ACTOR_Y_OFFSET

from libraries.config import *


class BarricadeEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemy_index = ENEMY_BARRICADE_INDEX
        self.open = False
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["barricade.png"]))
        self.setSpriteCenter(True, True)
        self.setSpriteOtherOffset(ACTOR_Y_OFFSET, y = 0)
        self.base_layer = BARRICADE_LAYER
        self.removeShadow()
        
        
    def setEventFlag(self, val):
        super().setEventFlag(val)
        if gamestate.getEventFlag(self.event_flag, False):
            self.setSpriteAnimation("OPEN")
            self.updateTileCollision(False)
            self.open = True
            self.setStunned(True)
        else:
            self.setSpriteAnimation("CLOSED")
            self.updateTileCollision(True)
            self.open = False
        
    def updateTileCollision(self, val):
        for offset in ((0,0),(0,-16),(-16,0),(-16,-16)):
            tile = self.mappe.getMapTileAtPos(*map(operator.add, offset, self.getPos()))
            if tile:
                tile.setCollision(val)
                
    #overwritten stuff
    
    def updateMovementAnimation(self):
        pass
              
    def stunEnemy(self, *args, **kwargs):
        if not self.open:
            self.setStunned(True)
            self.setSpriteAnimation("OPEN")
            playSound(SOUND_CRASH, True)
            self.updateTileCollision(False)
            if self.event_flag != "" and self.event_flag != None:
                gamestate.setEventFlag(self.event_flag, True)
            return True
        return False
    

    def setHurt(self, *args, **kwargs):
        pass