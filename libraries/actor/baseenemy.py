# -*- coding: utf-8 -*-

import random

from .baseactor import BaseActor

from kaiengine.resource import toStringPath
from kaiengine.objectinterface import GraphicInterface

from libraries.config import *

WANDER_VELOCITY = 20
WANDER_VELS = [(WANDER_VELOCITY,0),(-WANDER_VELOCITY,0),
               (0,WANDER_VELOCITY),(0,-WANDER_VELOCITY)]

WANDER_FREQUENCY = 120

STUN_VEL = 120
STUN_KNOCKBACK_TIME = 20
STUN_STAR_HEIGHT = 24

class BaseEnemy(BaseActor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemy = True
        self.enemy_index = None
        self.stunned = False
        self.stun_knockback = False
        self.stun_stars = None
        
        self.Schedule(self.updateOffscreen, 10, True)
        
    def getEnemyIndex(self):
        return self.enemy_index
        
    def startWander(self):
        if self.checkWanderAction():
            self.setVelocity(*random.choice(WANDER_VELS))
        self.Schedule(self._wanderWait, WANDER_FREQUENCY)
        
    def _wanderWait(self):
        if self.checkWanderAction():
            self.setVelocity(0,0)
        self.Schedule(self.startWander, WANDER_FREQUENCY)
        
    def checkWanderAction(self):
        return not self.isHurt() and not self.isStunned()
        
    def updateOffscreen(self):
        if self.checkSpriteOffscreen():
            self.cleanupSelf()
            
    def stunEnemy(self, x, y):
        self.setStunned(True)
        self.setSpriteAnimation(ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][False][0])
        self.setKnockbackVel(x, y, STUN_VEL)
        self.Schedule(self._finishStunKnockback, STUN_KNOCKBACK_TIME)
        self.stun_knockback = True
        self.removeStunStars()
        self.stun_stars = GraphicInterface()
        self.stun_stars.setSprite(toStringPath(EFFECTS_GRAPHICS_FULL_PATH + ["stun_stars.png"]))
        self.stun_stars.setSpriteOffset(y=STUN_STAR_HEIGHT)
        self.stun_stars.setSpriteLayer(STUN_STAR_LAYER)
        self.stun_stars.setSpriteCenter(True, True)
        self._updateSpritePos()
        return False #for minotaur charge
        
    def _finishStunKnockback(self):
        self.stun_knockback = False
        self.setVelocity(0,0)
            
    def isStunned(self):
        return self.stunned
    
    def setStunned(self, val):
        self.stunned = val
        
    def removeStunStars(self):
        if self.stun_stars:
            self.stun_stars.destroy()
        self.stun_stars = None
        
    #overwritten stuff
    
    def _updateSpritePos(self): 
        super()._updateSpritePos()
        if self.stun_stars:
            self.stun_stars.setPos(*self.getPos())
    
    def updateMovementAnimation(self):
        if not self.isStunned():
            super().updateMovementAnimation()
    
    def _endHurt(self):
        super()._endHurt()
        self.cleanupSelf()
        
    def destroy(self):
        super().destroy()
        self.removeStunStars()