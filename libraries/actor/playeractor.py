# -*- coding: utf-8 -*-

import operator, math

from kaiengine.event import customEvent, callQuery
from kaiengine.keybinds import keyMatches
from kaiengine.resource import toStringPath

from libraries.audio import playSound
from libraries.keyheld import checkKeyHeld

from libraries.config import *

from .baseactor import BaseActor
from .rainbowbubbleactor import RainbowBubble

SCREEN_BOUNDARIES = 8

MOVEMENT_SPEED = 80

PROJECTILE_OFFSET = 8
PROJECTILE_OFFSET_DICT = {DIRECTION_UP: (0,PROJECTILE_OFFSET),
                          DIRECTION_DOWN: (0,-PROJECTILE_OFFSET),
                          DIRECTION_RIGHT: (PROJECTILE_OFFSET,0),
                          DIRECTION_LEFT: (-PROJECTILE_OFFSET,0)}

COPY_SPRITES = {PLAYER_FORM_INDEX: "char.png",
                ENEMY_BAT_INDEX: "bat_pink.png",
                ENEMY_SKELETON_INDEX: "skeleton_pink.png",
                ENEMY_MINOTAUR_INDEX: "minotaur_pink.png"}

PLAYER_HURT_TIME = 90
HURT_KNOCKBACK_VEL = 160
HURT_CONTROL_LOSS_TIME = 10

PLAYER_SKELETON_BACKSWING_TIME = 2
PLAYER_SWING_FOLLOW_THROUGH_TIME = 20

PLAYER_SWORD_HITBOX_WIDE = 32
PLAYER_SWORD_HITBOX_FAR = 24

PLAYER_CHARGE_WINDUP_TIME = 30
PLAYER_CHARGE_VELOCITY = 160

PLAYER_CHARGING_ENEMY_COLLISION = 24

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

class PlayerActor(BaseActor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = True
        
        self.charging = False
        self.charging_windup = False
        self.charging_forward = False
        self.charging_knockback = False
        self.knockback_z_vel = 0
        self.swinging_sword = False
        self.hurt_control_loss = False
        self.bubble_exists = False
        self.form = PLAYER_FORM_INDEX
        
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["char.png"]))
        
        self.Schedule(self.updatePlayerStuff, 1, True)
        
        self.addKeyPressListener(self.keyPressed)
        self.addCustomListener(PLAYER_FORM_CHANGE_EVENT, self.setPlayerForm)
        self.addCustomListener(PLAYER_HURT_PLAYER_EVENT, self.hurtPlayer)
        self.addQueryListener(PLAYER_GET_POS_QUERY, self.getPos)
        
    def setBubbleExists(self, val):
        self.bubble_exists = val
        
    def keyPressed(self, symbol, modifiers):
        if not self.mappe.getScreenTransitioning() and not self.hurt_control_loss and not self.swinging_sword and not self.charging and not self.paused:
            if keyMatches(CANCEL, symbol):
                if self.form != PLAYER_FORM_INDEX:
                    if not self.checkOverPit(): #don't allow this if flying over a pit
                        self.setPlayerForm(PLAYER_FORM_INDEX)
                        playSound(SOUND_BLOORP, True)
                else:
                    if not self.bubble_exists:
                        self.setBubbleExists(True)
                        bubble = self.mappe.getActor(self.mappe.addActor(RainbowBubble))
                        bubble.setPos(*map(operator.add, self.getPos(), PROJECTILE_OFFSET_DICT.get(self.facing, (0,0))))
                        bubble.setBubbleDirection(self.facing)
                        playSound(SOUND_SHOOT, True)
            elif keyMatches(CONFIRM, symbol):
                if self.form == ENEMY_SKELETON_INDEX and not self.swinging_sword:
                    self.setVelocity(0,0)
                    self.swinging_sword = True
                    self.setSpriteAnimation(SKELETON_ANI_DICT[self.facing][0][0])
                    self.setSpriteFlip(SKELETON_ANI_DICT[self.facing][1])
                    self.Schedule(self._swingSword, PLAYER_SKELETON_BACKSWING_TIME)
                elif self.form == ENEMY_MINOTAUR_INDEX and not self.charging:
                    self.charging = True
                    self.charging_windup = True
                    self.setVelocity(0,0)
                    self.setSpriteAnimation(ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][True][0])
                    self.setSpriteAnimationSpeed(2.0)
                    playSound(SOUND_RUNNING, True)
                    self.Schedule(self._startCharge, PLAYER_CHARGE_WINDUP_TIME)
                    
                    
    def _swingSword(self):
        self.setSpriteAnimation(SKELETON_ANI_DICT[self.facing][0][1])
        self.Schedule(self._finishSwordSwing, PLAYER_SWING_FOLLOW_THROUGH_TIME)
        if self.facing in {DIRECTION_UP, DIRECTION_DOWN}:
            hitbox_x_left = self.getPos()[0] - PLAYER_SWORD_HITBOX_WIDE/2
            hitbox_x_right = hitbox_x_left + PLAYER_SWORD_HITBOX_WIDE
            if self.facing == DIRECTION_UP:
                hitbox_y_top = self.getPos()[1] + PLAYER_SWORD_HITBOX_FAR
                hitbox_y_bottom = self.getPos()[1]
            else:
                hitbox_y_top = self.getPos()[1] 
                hitbox_y_bottom = self.getPos()[1] - PLAYER_SWORD_HITBOX_FAR
        else:
            hitbox_y_bottom = self.getPos()[1] - PLAYER_SWORD_HITBOX_WIDE/2
            hitbox_y_top = hitbox_y_bottom + PLAYER_SWORD_HITBOX_WIDE
            if self.facing == DIRECTION_RIGHT:
                hitbox_x_left = self.getPos()[0]
                hitbox_x_right = self.getPos()[0] + PLAYER_SWORD_HITBOX_FAR
            else:
                hitbox_x_left = self.getPos()[0] - PLAYER_SWORD_HITBOX_FAR
                hitbox_x_right = self.getPos()[0]
        for enemy in self.mappe.getEnemyActors():
            if not enemy.isHurt():
                x, y = enemy.getPos()
                if x >= hitbox_x_left and x <= hitbox_x_right and y >= hitbox_y_bottom and y <= hitbox_y_top:
                    enemy.setHurt(60)
                    if enemy.isHurt(): #hack for doors/etc
                        enemy.setVelocity(0,0)
                        playSound(SOUND_HIT_ENEMY, True)
        
    def _finishSwordSwing(self):
        self.swinging_sword = False
        self.updateMovementAnimation()
        
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
        for enemy in self.mappe.getEnemyActors():
            if not enemy.isStunned() and not enemy.isHurt():
                x, y = map(operator.sub, enemy.getPos(), self.getPos())
                if abs(x) + abs(y) <= PLAYER_CHARGING_ENEMY_COLLISION:
                    if enemy.stunEnemy(*self.getPos()):
                        self._chargeKnockback()
                        playSound(SOUND_CRASH, True)
                        self.Unschedule(self._chargeCollision)
                        return #hit a minotaur that was charging; skip everything after this
                    else:
                        if enemy.isStunned(): #hack for bushes
                            playSound(SOUND_HIT_ENEMY, True)
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
        self.setSpriteAnimation(ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][False][0])
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
        
                    
    def updatePlayerStuff(self):
        self.updatePlayerMovementInput()
        self.updateScreenTransitions()
        
    def updatePlayerMovementInput(self):
        if not self.mappe.getScreenTransitioning() and not self.hurt_control_loss and not self.charging:
            if self.swinging_sword:
                self.setVelocity(0,0)
            else:
                if checkKeyHeld(MOVE_UP):
                    self.setVelocity(y = MOVEMENT_SPEED)
                elif checkKeyHeld(MOVE_DOWN):
                    self.setVelocity(y = -MOVEMENT_SPEED)
                else:
                    self.setVelocity(y = 0)
                if checkKeyHeld(MOVE_LEFT):
                    self.setVelocity(-MOVEMENT_SPEED)
                elif checkKeyHeld(MOVE_RIGHT):
                    self.setVelocity(MOVEMENT_SPEED)
                else:
                    self.setVelocity(0)
            
    def updateScreenTransitions(self):
        if not self.mappe.getScreenTransitioning():
            x, y = self.getSpriteScreenPosition()
            if x < SCREEN_BOUNDARIES:
                customEvent(START_SCREEN_TRANSITION_EVENT, DIRECTION_LEFT)
            elif x > MAP_SIZE[0] - SCREEN_BOUNDARIES:
                customEvent(START_SCREEN_TRANSITION_EVENT, DIRECTION_RIGHT)
            elif y > MAP_SIZE[1] - SCREEN_BOUNDARIES:
                customEvent(START_SCREEN_TRANSITION_EVENT, DIRECTION_UP)
            elif y < SCREEN_BOUNDARIES:
                customEvent(START_SCREEN_TRANSITION_EVENT, DIRECTION_DOWN)
                
            
    def setPlayerForm(self, form_index):
        self.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + [COPY_SPRITES.get(form_index, "char.png")]))
        self.form = form_index
        
    def hurtPlayer(self, x, y):
        if not self.hurt:
            self._chargeFinish() #just in case
            self._finishSwordSwing()
            self.setHurt(90)
            self.setKnockbackVel(x, y, HURT_KNOCKBACK_VEL)
            self.hurt_control_loss = True
            playSound(SOUND_HIT_PLAYER, True)
            customEvent(PLAYER_REDUCE_HP_EVENT)
            if callQuery(CHECK_PLAYER_DEAD_QUERY):
                self.setVelocity(0,0)
                self.Schedule(self._vanishForever, 91)
                self.Unschedule(self._endHurt)
            else:
                self.Schedule(self._regainHurtControl, HURT_CONTROL_LOSS_TIME)
                
    def _regainHurtControl(self):
        self.hurt_control_loss = False
        self.setVelocity(0,0)
        
    def _vanishForever(self):
        self.setSpriteAlpha(0.0)
        self.Unschedule(self._hurtFlash)
        customEvent(GAME_LOST_EVENT)
        
    def isCharging(self):
        return self.charging
        
        
    #overwritten stuff
    
    def updateMovementAnimation(self, *args, **kwargs):
        if not self.swinging_sword and not self.charging:
            super().updateMovementAnimation(*args, **kwargs)
    
    def isFlying(self):
        if self.form == ENEMY_BAT_INDEX:
            return True
        return super().isFlying()
    
    def updateFacing(self):
        if not self.charging:
            super().updateFacing()
            
        