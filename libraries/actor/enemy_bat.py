# -*- coding: utf-8 -*-

import operator
from functools import reduce

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .baseenemy import BaseEnemy

from libraries.config import *

COLLISION_DISTANCE = 4

class BatEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flying = True
        self.enemy_index = ENEMY_BAT_INDEX
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["bat.png"]))
        
        self.startWander()
        
        self.Schedule(self.checkPlayerCollision, 1, True)
        
        
    def checkPlayerCollision(self):
        if not self.isHurt() and not self.mappe.getPlayerActor().isCharging() and not self.isStunned():
            distance = reduce(lambda x, y: abs(x) + abs(y), map(operator.sub, self.getPos(), self.mappe.getPlayerActor().getPos()))
            if distance <= COLLISION_DISTANCE:
                customEvent(PLAYER_HURT_PLAYER_EVENT, *self.getPos())