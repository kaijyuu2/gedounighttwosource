# -*- coding: utf-8 -*-

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from libraries.audio import playSound

from libraries.config import *

from .baseactor import BaseActor

from functools import reduce
import operator

RAINBOW_BUBBLE_SPEED = 160

RAINBOW_BUBBLE_SPEED_DICT = {DIRECTION_UP: (0,RAINBOW_BUBBLE_SPEED),
                             DIRECTION_DOWN: (0,-RAINBOW_BUBBLE_SPEED),
                             DIRECTION_RIGHT: (RAINBOW_BUBBLE_SPEED,0),
                             DIRECTION_LEFT: (-RAINBOW_BUBBLE_SPEED,0)}

COLLISION_DISTANCE = 12

class RainbowBubble(BaseActor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collision = False #manually checks its own collision
        self.removeShadow()
        
        self.hit_something = False
        
        self.setSprite(toStringPath(EFFECTS_GRAPHICS_FULL_PATH + ["rainbowbubble.png"]))
        
        self.Schedule(self.updateHitSomething, 1, True)
        
    def setBubbleDirection(self, direction):
        self.setVelocity(*RAINBOW_BUBBLE_SPEED_DICT.get(direction, (0,0)))
        
        
    def updateHitSomething(self):
        if not self.hit_something:
            for enemy in self.mappe.getEnemyActors():
                distance = reduce(lambda x, y: abs(x) + abs(y), map(operator.sub, self.getPos(), enemy.getPos()))
                if distance <= COLLISION_DISTANCE:
                    enemy_index = enemy.getEnemyIndex()
                    if enemy_index:
                        customEvent(PLAYER_FORM_CHANGE_EVENT, enemy.getEnemyIndex())
                        playSound(SOUND_POWERUP, True)
                        self._hitSomething()
                        return
            if self.checkCollision():
                playSound(SOUND_POP, True)
                self._hitSomething()
                return
            if self.checkSpriteOffscreen():
                playSound(SOUND_POP, True)
                self._hitSomething()
                return
                
                
    def _hitSomething(self):
            self.setSpriteAnimation("POP")
            self.hit_something = True
            self.sprite.addAniFinishListener(None, self.cleanupSelf)
            self.setVelocity(0,0)
                
    #overwritten stuff
    
    def updateMovementAnimation(self):
        pass #do nothing
                
    def cleanupSelf(self):
        self.mappe.setPlayerBubbleExists(False)
        super().cleanupSelf()