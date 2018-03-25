# -*- coding: utf-8 -*-

import operator, random
from functools import reduce

from libraries.audio import playSound
from libraries import gamestate

from kaiengine.sDict import sDict
from kaiengine.event import customEvent, callQuery
from kaiengine.resource import toStringPath
from kaiengine.objectinterface import GraphicInterface

from .baseenemy import BaseEnemy
from .baseactor import ACTOR_Y_OFFSET

from libraries.config import *

SPARKLE_TIME = 30
SPARKLE_VARIANCE = .75
SPARKLE_INIT_RANGE = 90
SPARKLE_NUMBER = 2

OPEN_DISTANCE = 32

class SquidDoorEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sparkle_graphic_list = ["sparkle1_gold.png","sparkle2_gold.png"]
        self.sparkle_graphics = sDict()
        
        self.enemy_index = ENEMY_SQUID_DOOR_INDEX
        self.open = False
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["squiddoor.png"]))
        self.setSpriteCenter(True, True)
        self.setSpriteOtherOffset(ACTOR_Y_OFFSET, y = 0)
        self.base_layer = BARRICADE_LAYER
        self.removeShadow()
        
        for i in range(SPARKLE_NUMBER):
            self.Schedule(self._createSparkle, random.randint(0, SPARKLE_INIT_RANGE)+1)
            
        self.Schedule(self.lookForPlayer, 1, True)
        
    def setEventFlag(self, val):
        super().setEventFlag(val)
        if gamestate.getEventFlag(self.event_flag, False):
            self.setSpriteAlpha(0.0)
            self.updateTileCollision(False)
            self.open = True
            self.setStunned(True)
        else:
            self.setSpriteAlpha(1.0)
            self.updateTileCollision(True)
            self.open = False
        
    def updateTileCollision(self, val):
        for offset in ((0,0),(0,-16),(-16,0),(-16,-16)):
            tile = self.mappe.getMapTileAtPos(*map(operator.add, offset, self.getPos()))
            if tile:
                tile.setCollision(val)
                
    def _createSparkle(self):
        if self.sparkle_graphic_list and not self.open:
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
            
    def lookForPlayer(self):
        pactor = self.mappe.getPlayerActor()
        x, y = map(operator.sub, pactor.getPos(), self.getPos())
        if not self.open and abs(x) + abs(y) <= OPEN_DISTANCE and callQuery(ALL_SQUID_TROPHIES_OBTAINED_QUERY):
            self.setSpriteAlpha(0.0)
            self.updateTileCollision(False)
            self.open = True
            self.setStunned(True)
            playSound(SOUND_SQUID_DOOR, True)
                
    #overwritten stuff
    
    def setHurt(self, *args, **kwargs):
        pass
    
    def updateMovementAnimation(self):
        pass
              
    def destroy(self):
        super().destroy()
        for sparkle in self.sparkle_graphics.values():
            sparkle.destroy()
        self.sparkle_graphics.clear()