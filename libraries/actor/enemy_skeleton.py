# -*- coding: utf-8 -*-

import operator
from functools import reduce

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .baseenemy import BaseEnemy

from libraries.config import *

COLLISION_DISTANCE = 6

SKELETON_MOVEMENT_SPEED = 20
SWING_DISTANCE = 16

SKELETON_BACKSWING_TIME = 40
SKELETON_SWING_FOLLOW_THROUGH_TIME = 40

SKELETON_SWING_HITBOX_WIDE = 24
SKELETON_SWING_HITBOX_FAR = 16

class SkeletonEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swinging_sword = False
        
        self.enemy_index = ENEMY_SKELETON_INDEX
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["skeleton.png"]))
        
        self.Schedule(self.moveTowardPlayer, 30, True)
        
        self.Schedule(self.checkPlayerCollision, 1, True)
        
        
    def checkPlayerCollision(self):
        if not self.isHurt() and not self.mappe.getPlayerActor().isCharging() and not self.isStunned():
            distance = reduce(lambda x, y: abs(x) + abs(y), map(operator.sub, self.getPos(), self.mappe.getPlayerActor().getPos()))
            if distance <= COLLISION_DISTANCE:
                customEvent(PLAYER_HURT_PLAYER_EVENT, *self.getPos())
                
                
    def moveTowardPlayer(self):
        if not self.swinging_sword and not self.isHurt() and not self.isStunned():
            x, y = map(operator.sub, self.mappe.getPlayerActor().getPos(), self.getPos())
            if abs(y) > abs(x):
                if y > 0:
                    self.setVelocity(0, SKELETON_MOVEMENT_SPEED)
                else:
                    self.setVelocity(0, -SKELETON_MOVEMENT_SPEED)
            else:
                if x > 0:
                    self.setVelocity(SKELETON_MOVEMENT_SPEED, 0)
                else:
                    self.setVelocity(-SKELETON_MOVEMENT_SPEED, 0)
            self.updateFacing()
            if abs(x) + abs(y) <= SWING_DISTANCE:
                self.setVelocity(0,0)
                self.swinging_sword = True
                self.setSpriteAnimation(SKELETON_ANI_DICT[self.facing][0][0])
                self.setSpriteFlip(SKELETON_ANI_DICT[self.facing][1])
                self.Schedule(self._swingSword, SKELETON_BACKSWING_TIME)
                
    def _swingSword(self):
        self.setSpriteAnimation(SKELETON_ANI_DICT[self.facing][0][1])
        self.Schedule(self._finishSwordSwing, SKELETON_SWING_FOLLOW_THROUGH_TIME)
        if self.facing in {DIRECTION_UP, DIRECTION_DOWN}:
            hitbox_x_left = self.getPos()[0] - SKELETON_SWING_HITBOX_WIDE/2
            hitbox_x_right = hitbox_x_left + SKELETON_SWING_HITBOX_WIDE
            if self.facing == DIRECTION_UP:
                hitbox_y_top = self.getPos()[1] + SKELETON_SWING_HITBOX_FAR
                hitbox_y_bottom = self.getPos()[1]
            else:
                hitbox_y_top = self.getPos()[1] 
                hitbox_y_bottom = self.getPos()[1] - SKELETON_SWING_HITBOX_FAR
        else:
            hitbox_y_bottom = self.getPos()[1] - SKELETON_SWING_HITBOX_WIDE/2
            hitbox_y_top = hitbox_y_bottom + SKELETON_SWING_HITBOX_WIDE
            if self.facing == DIRECTION_RIGHT:
                hitbox_x_left = self.getPos()[0]
                hitbox_x_right = self.getPos()[0] + SKELETON_SWING_HITBOX_FAR
            else:
                hitbox_x_left = self.getPos()[0] - SKELETON_SWING_HITBOX_FAR
                hitbox_x_right = self.getPos()[0]
        x, y = self.mappe.getPlayerActor().getPos()
        if x >= hitbox_x_left and x <= hitbox_x_right and y >= hitbox_y_bottom and y <= hitbox_y_top:
            customEvent(PLAYER_HURT_PLAYER_EVENT, *self.getPos())
            
            
    def _finishSwordSwing(self):
        self.swinging_sword = False
        self.updateMovementAnimation()
        
    #overwritten stuff
    
    def stunEnemy(self, *args, **kwargs):
        self._finishSwordSwing()
        super().stunEnemy(*args, **kwargs)
    
    def setHurt(self, *args, **kwargs):
        self._finishSwordSwing()
        super().setHurt(*args, **kwargs)
        
    def updateMovementAnimation(self, *args, **kwargs):
        if not self.swinging_sword:
            super().updateMovementAnimation(*args, **kwargs)