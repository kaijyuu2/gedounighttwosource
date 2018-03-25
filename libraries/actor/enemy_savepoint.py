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


SAVE_DISTANCE = 16

class SaveEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemy_index = ENEMY_SAVE_INDEX
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["save.png"]))
        self.setSpriteCenter(True, True)
        self.setSpriteOtherOffset(ACTOR_Y_OFFSET, y = 0)
        self.base_layer = SAVE_LAYER
        self.removeShadow()
        
        self.Schedule(self.checkForPlayerToSave, 1, True)
        
        
    def checkForPlayerToSave(self):
        pactor = self.mappe.getPlayerActor()
        x, y = map(operator.sub, pactor.getPos(), self.getPos())
        if abs(x) + abs(y) <= SAVE_DISTANCE:
            self.Unschedule(self.checkForPlayerToSave)
            playSound(SOUND_SAVE, True)
            customEvent(PUSH_SAVE_EVENT)
            customEvent(PLAYER_MAX_HP_EVENT)
                
    #overwritten stuff
    
    def updateMovementAnimation(self):
        pass
              
    def stunEnemy(self, *args, **kwargs):
        pass

    def setHurt(self, *args, **kwargs):
        pass