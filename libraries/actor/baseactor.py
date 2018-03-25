# -*- coding: utf-8 -*-

from kaiengine.resource import toStringPath
from kaiengine.weakrefhelper import unWeakRef, weakRef
from kaiengine.debug import debugMessage
from kaiengine.objectinterface import SchedulerInterface, MovementInterfaceFrames, GraphicInterface, EventInterface

from libraries.gamestate import getMapTileAtPos

from libraries.config import *

import operator, math

ACTOR_Y_OFFSET = "actor_y_offset"


class BaseActor( GraphicInterface, MovementInterfaceFrames,SchedulerInterface, EventInterface):
    
    
    def __init__(self, mappe, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shadow = GraphicInterface()
        self.shadow.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["playershadow.png"]))
        self.shadow.setSpriteCenter(True, True)
        self.shadow.setSpriteLayer(SHADOW_LAYER)
        self.actor_id = -1
        self.paused = False
        self._mappe = weakRef(mappe)
        self.facing = DIRECTION_DOWN
        self.moving = False
        self.collision = True
        self.flying = False
        self.base_layer = ACTOR_LAYER
        self.z_pos = 0
        self.enemy = False
        self.player = False
        self.room_index = (0,0)
        self.hurt = False
        self.event_flag = None #used for some enemies
        
        self.updateActorLayer(0)
        self.setSpriteCenter(x=True)
        
        self.Schedule(self.updateAnimation, 1, True)
        
    @property
    def mappe(self):
        return unWeakRef(self._mappe)
    @mappe.setter
    def mappe(self, val):
        debugMessage("Cannot set map directly")
        
    def setActorId(self, actor_id):
        self.actor_id = actor_id
        
    def getActorId(self):
        return self.actor_id
    
    def setBaseLayer(self, val):
        self.base_layer = val
        
    def getBaseLayer(self):
        return self.base_layer
    
    def updateActorLayer(self, offset):
        self.setSpriteLayer(self.base_layer + offset)
        
    def setRoomIndex(self, val):
        self.room_index = val
        
    def getRoomIndex(self):
        return self.room_index
    
    def checkCollision(self, x = None, y = None):
        if x is None: x = self.getPos()[0]
        if y is None: y = self.getPos()[1]
        tile = getMapTileAtPos(x,y)
        return tile is None or tile.getCollision()
    
    def checkOverPit(self, x = None, y = None):
        if x is None: x = self.getPos()[0]
        if y is None: y = self.getPos()[1]
        tile = getMapTileAtPos(x,y)
        return tile is not None and tile.getPit()
    
    def updateAnimation(self):
        #check state
        self.updateMoving()
        self.updateMovementAnimation()
        
    def updateMovementAnimation(self):
        ani, flip = ACTOR_MOVEMENT_ANIMATION_DICT[self.facing][self.moving]
        self.setSpriteAnimation(ani, False, "DEFAULT")
        self.setSpriteFlip(flip)
        
    def updateMoving(self):
        if abs(self.velocity[1]) + abs(self.velocity[0]) != 0:
            self.moving = True
        else:
            self.moving = False
            
    def cleanupSelf(self):
        if not self.destroyed:
            self.mappe.removeActor(self.getActorId())
            
    def isEnemy(self):
        return self.enemy
    
    def isFlying(self):
        return self.flying
    
    def isPlayer(self):
        return self.player
    
    
    def pauseActor(self):
        if not self.paused:
            self.pauseMovement()
            self.pauseSpriteAnimations()
            self.pauseAllScheduledListeners()
            self.paused = True
        
    def unpauseActor(self):
        if self.paused:
            self.unpauseMovement()
            self.unpauseSpriteAnimations()
            self.unpauseAllScheduledListeners()
            self.paused = False
            
    def removeShadow(self):
        if self.shadow:
            self.shadow.destroy()
        self.shadow = None
        
    def setHurt(self, time):
        self.hurt = True
        self.Unschedule(self._hurtFlash)
        self.Schedule(self._hurtFlash, 2, True)
        self.Unschedule(self._endHurt)
        self.Schedule(self._endHurt, time)
        
    def _hurtFlash(self):
        self.setSpriteAlpha(abs(self.getSpriteAlpha() - 1.0))
        
    def _endHurt(self):
        self.Unschedule(self._hurtFlash)
        self.setSpriteAlpha(1.0)
        self.hurt = False
        
    def isHurt(self):
        return self.hurt
    
    def updateFacing(self):
        if abs(self.velocity[1]) > abs(self.velocity[0]):
            if self.velocity[1] > 0:
                self.facing = DIRECTION_UP
            else:
                self.facing = DIRECTION_DOWN
        elif abs(self.velocity[1]) != abs(self.velocity[0]):
            if self.velocity[0] > 0:
                self.facing = DIRECTION_RIGHT
            elif self.velocity[0] < 0:
                self.facing = DIRECTION_LEFT
        if self.velocity[0] > 0 and self.facing == DIRECTION_LEFT:
            self.facing = DIRECTION_RIGHT
        elif self.velocity[0] < 0 and self.facing == DIRECTION_RIGHT:
            self.facing = DIRECTION_LEFT
        elif self.velocity[1] > 0 and self.facing == DIRECTION_DOWN:
            self.facing = DIRECTION_UP
        elif self.velocity[1] < 0 and self.facing == DIRECTION_UP:
            self.facing = DIRECTION_DOWN
            
    def setKnockbackVel(self, x, y, vel):
        xoffset, yoffset = map(operator.sub, self.getPos(), (x,y))
        hypot = math.sqrt(xoffset**2 + yoffset**2)
        if hypot == 0: #avoid divide by 0
            hypot = 1
            xoffset = 1
            yoffset = 0
        self.setVelocity(vel*xoffset / hypot, vel*yoffset / hypot)
        
    def setEventFlag(self, val):
        self.event_flag = val
    
    #overwritten stuff
    
    def setSprite(self, *args, **kwargs):
        super().setSprite(*args, **kwargs)
        self.setSpriteOtherOffset(ACTOR_Y_OFFSET, y = -self.getSpriteHeight()/6)
    
    def _updateSpritePos(self): 
        x, y = self.getPos()
        try: self.sprite.setPos(x, y + self.z_pos)
        except AttributeError: pass
        if self.shadow:
            self.shadow.setPos(x, y-2)
    
    def runMovement(self, *args, **kwargs):
        super().runMovement(*args, **kwargs)
        self.updateFacing()
        self.updateAnimation()
    
    def setPos(self, x = None, y = None):
        if not self.collision or self.checkCollision() or (not self.isFlying() and self.checkOverPit()): #failsafe if already in a wall
            super().setPos(x,y)
        else:
            oldpos = self.getPos()
            if x is None: x = oldpos[0]
            if y is None: y = oldpos[1]
            if not self.checkCollision(x) and (self.isFlying() or not self.checkOverPit(x)): #extremely simple collision
                super().setPos(x)
            if not self.checkCollision(y=y) and (self.isFlying() or not self.checkOverPit(y=y)):
                super().setPos(y=y)
                
    def destroy(self):
        super().destroy()
        self.removeShadow()