# -*- coding: utf-8 -*-

import operator
from functools import reduce

from libraries.audio import playSound

from kaiengine.event import customEvent
from kaiengine.resource import toStringPath

from .baseenemy import BaseEnemy

from libraries.config import *

COLLISION_DISTANCE = 8

MINOTAUR_CHARGING_COLLISION_DISTANCE = 24
MINOTAUR_CHARGE_LINE_OF_SIGHT = 16

#actually minotaur stuff but too lazy to change
PLAYER_CHARGE_WINDUP_TIME = 40
PLAYER_CHARGE_VELOCITY = 160

PLAYER_CHARGING_COLLISION_OFFSET = 4
PLAYER_CHARGE_COLLISION_DICT = {DIRECTION_UP: (0, PLAYER_CHARGING_COLLISION_OFFSET),
                                DIRECTION_DOWN: (0, -PLAYER_CHARGING_COLLISION_OFFSET),
                                DIRECTION_LEFT: (-PLAYER_CHARGING_COLLISION_OFFSET, 0),
                                DIRECTION_RIGHT: (PLAYER_CHARGING_COLLISION_OFFSET, 0)}
PLAYER_CHARGE_KNOCKBACK_VEL = 40
PLAYER_CHARGE_KNOCKBACK_Z_VEL = 80
PLAYER_CHARGE_KNOCKBACK_GRAVITY = PLAYER_CHARGE_KNOCKBACK_Z_VEL/25
PLAYER_CHARGE_KNOCKBACK_DICT = {DIRECTION_UP: (0, -PLAYER_CHARGE_KNOCKBACK_VEL),
                                DIRECTION_DOWN: (0, PLAYER_CHARGE_KNOCKBACK_VEL),
                                DIRECTION_LEFT: (PLAYER_CHARGE_KNOCKBACK_VEL, 0),
                                DIRECTION_RIGHT: (-PLAYER_CHARGE_KNOCKBACK_VEL, 0)}


class MinotaurEnemy(BaseEnemy):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.charging = False
        self.charging_windup = False
        self.charging_forward = False
        self.charging_knockback = False
        self.knockback_z_vel = 0
        
        self.enemy_index = ENEMY_MINOTAUR_INDEX
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["minotaur.png"]))
        
        self.startWander()
        self.Schedule(self.checkForPlayer, 90, True)
        
        self.Schedule(self.checkPlayerCollision, 1, True)
        
    def checkForPlayer(self):
        if not self.charging and not self.isStunned() and not self.isHurt():
            x, y = map(operator.sub, self.mappe.getPlayerActor().getPos(), self.getPos())
            if abs(x) <= MINOTAUR_CHARGE_LINE_OF_SIGHT or abs(y) <= MINOTAUR_CHARGE_LINE_OF_SIGHT:
                if abs(x) < abs(y):
                    if y > 0:
                        self.facing = DIRECTION_UP
                    else:
                        self.facing = DIRECTION_DOWN
                else:
                    if x > 0:
                        self.facing = DIRECTION_RIGHT
                    else:
                        self.facing = DIRECTION_LEFT
                self.beginCharge()
        
        
    def checkPlayerCollision(self):
        if not self.isHurt() and not self.mappe.getPlayerActor().charging_forward and not self.isStunned():
            distance = reduce(lambda x, y: abs(x) + abs(y), map(operator.sub, self.getPos(), self.mappe.getPlayerActor().getPos()))
            if self.charging_forward:
                col_distance = MINOTAUR_CHARGING_COLLISION_DISTANCE
            else:
                col_distance = COLLISION_DISTANCE
            if distance <= col_distance:
                customEvent(PLAYER_HURT_PLAYER_EVENT, *self.getPos())
            
    def beginCharge(self):
        self.charging = True
        self.charging_windup = True
        self.setVelocity(0,0)
        ani, flip = ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][True]
        self.setSpriteAnimation(ani)
        self.setSpriteFlip(flip)
        self.setSpriteAnimationSpeed(2.0)
        playSound(SOUND_RUNNING, True)
        self.Schedule(self._startCharge, PLAYER_CHARGE_WINDUP_TIME)
        
    def _startCharge(self):
        self.charging_windup = False
        self.charging_forward = True
        if self.facing == DIRECTION_UP:
            self.setVelocity(0, PLAYER_CHARGE_VELOCITY)
        elif self.facing == DIRECTION_DOWN:
            self.setVelocity(0, -PLAYER_CHARGE_VELOCITY)
        elif self.facing == DIRECTION_RIGHT:
            self.setVelocity(PLAYER_CHARGE_VELOCITY, 0)
        else:
            self.setVelocity(-PLAYER_CHARGE_VELOCITY, 0)
        self.Schedule(self._chargeCollision, 1, True)
        
    def _chargeCollision(self):
        offset = list(map(operator.add, self.getPos(), PLAYER_CHARGE_COLLISION_DICT[self.facing]))
        if self.checkCollision(*offset):
            playSound(SOUND_CRASH, True)
            self._chargeKnockback()
            self.Unschedule(self._chargeCollision)
        elif self.checkOverPit(*offset):
            self._chargeFinish()
            self.Unschedule(self._chargeCollision)
            
    def _chargeKnockback(self):
        self.charging_forward = False
        self.charging_knockback = True
        ani, flip = ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][False]
        self.setSpriteAnimation(ani)
        self.setSpriteFlip(flip)
        self.setVelocity(*PLAYER_CHARGE_KNOCKBACK_DICT[self.facing])
        self.knockback_z_vel = PLAYER_CHARGE_KNOCKBACK_Z_VEL
        self.Schedule(self._chargeKnockbackMovement, 1, True)
        
    def _chargeKnockbackMovement(self):
        self.z_pos += self.knockback_z_vel/60
        self.knockback_z_vel -= PLAYER_CHARGE_KNOCKBACK_GRAVITY
        if self.z_pos <= 0:
            self.charging_knockback = False
            self.z_pos = 0
            self.Unschedule(self._chargeKnockbackMovement)
            self.setVelocity(0,0)
            self._chargeFinish()
        self._updateSpritePos()
        
    def _chargeFinish(self):
        self.Unschedule(self._startCharge)
        self.Unschedule(self._chargeKnockbackMovement)
        self.Unschedule(self._chargeCollision)
        self.z_pos = 0
        self._updateSpritePos()
        self.charging = False
        self.charging_forward = False
        self.charging_windup = False
        self.charging_knockback = False
        self.setSpriteAnimationSpeed(1.0)
        
    #overwritten stuff
    
    def stunEnemy(self, *args, **kwargs):
        if self.charging_forward:
            self._chargeKnockback()
            self.Unschedule(self._chargeCollision)
            return True
        self._chargeFinish()
        return super().stunEnemy(*args, **kwargs)
    
    def updateMovementAnimation(self, *args, **kwargs):
        if not self.charging:
            super().updateMovementAnimation(*args, **kwargs)
            
    def checkWanderAction(self):
        return super().checkWanderAction() and not self.charging
        
    def setHurt(self, *args, **kwargs):
        self._chargeFinish()
        super().setHurt(*args, **kwargs)
        