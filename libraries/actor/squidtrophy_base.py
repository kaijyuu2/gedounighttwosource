# -*- coding: utf-8 -*-

from kaiengine.sDict import sDict
from kaiengine.objectinterface import GraphicInterface
from kaiengine.resource import toStringPath
from kaiengine.event import customEvent, callQuery

from libraries.audio import playSound

from libraries.config import *

from .baseenemy import BaseEnemy

from functools import reduce
import random, operator

SPARKLE_TIME = 30
SPARKLE_VARIANCE = .75
SPARKLE_INIT_RANGE = 90
SPARKLE_NUMBER = 2

COLLISION_DISTANCE = 8

class SquidTrophyBase(BaseEnemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparkle_graphic_list = []
        self.squid_trophy_index = None
        
        self.sparkle_graphics = sDict()
        
        for i in range(SPARKLE_NUMBER):
            self.Schedule(self._createSparkle, random.randint(0, SPARKLE_INIT_RANGE)+1)
            
        self.Schedule(self.checkSpawn, 1)
        self.Schedule(self.checkPlayerCollision, 1, True)
        
    def checkSpawn(self):
        if callQuery(SQUID_TROPHY_OBTAINED_QUERY, self.squid_trophy_index):
            self.cleanupSelf()
            
    def _createSparkle(self):
        if self.sparkle_graphic_list:
            sparkle_id = self.sparkle_graphics.append(GraphicInterface())
            sparkle = self.sparkle_graphics[sparkle_id]
            sparkle.setSprite(toStringPath(EFFECTS_GRAPHICS_FULL_PATH + [random.choice(self.sparkle_graphic_list)]))
            x, y = self.getBottomLeftCorner()
            sparkle.setPos(x + random.random()*self.getSpriteWidth(), y+random.random()*self.getSpriteHeight())
            sparkle.sprite.addAniFinishListener(None, sparkle.destroy)
            sparkle.setSpriteLayer(SPARKLE_LAYER)
        self.Schedule(self._createSparkle, int(random.random()*SPARKLE_TIME*SPARKLE_VARIANCE*2 + SPARKLE_TIME*(1.0-SPARKLE_VARIANCE)))
        
    def removeSparkle(self, sparkle_id):
        sparkle = self.sparkle_graphics.pop(sparkle_id, None)
        if sparkle:
            sparkle.destroy()
            
    def getSquidTrophyIndex(self):
        return self.squid_trophy_index
    
    
    def checkPlayerCollision(self):
        distance = reduce(lambda x, y: abs(x) + abs(y), map(operator.sub, self.getPos(), self.mappe.getPlayerActor().getPos()))
        if distance <= COLLISION_DISTANCE:
            self.collectSquid()
            
    def collectSquid(self):
        playSound(SOUND_COLLECT_SQUID, True)
        customEvent(SQUID_TROPHY_OBTAINED_EVENT, self.getSquidTrophyIndex())
        self.cleanupSelf()
            
    #overwritten stuff
    
    def stunEnemy(self, *args, **kwargs):
        pass
            
    def setHurt(self, *args, **kwargs):
        pass
            
    def destroy(self):
        super().destroy()
        for sparkle in self.sparkle_graphics.values():
            sparkle.destroy()
        self.sparkle_graphics.clear()