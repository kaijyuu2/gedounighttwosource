# -*- coding: utf-8 -*-

import copy, math, operator

from kaiengine.camera import moveX, moveY, setCameraXY, getCameraXY
from kaiengine.sDict import sDict
from kaiengine.baseobject import BaseObject
from kaiengine.objectinterface import SchedulerInterface, EventInterface
from kaiengine.gameframehandler import resetLag

from libraries.maptile import MapTile
from libraries.actor import *

from libraries.config import *

PAN_SPEED = 60
PLAYER_PAN_DISTANCE = 32
PLAYER_DX = PLAYER_PAN_DISTANCE / PAN_SPEED

SPRITE_DATA_SET = {(MAPTILE_DATA_LOWER, 0), (MAPTILE_DATA_UPPER, 1)}


ENEMY_TYPES_DICT= {ENEMY_BAT_INDEX: BatEnemy,
                   ENEMY_MINOTAUR_INDEX: MinotaurEnemy,
                   ENEMY_SKELETON_INDEX: SkeletonEnemy,
                   SQUID_TROPHY_BLUE_INDEX: SquidTrophyBlue,
                   SQUID_TROPHY_GREEN_INDEX: SquidTrophyGreen,
                   SQUID_TROPHY_RED_INDEX: SquidTrophyRed,
                   SQUID_TROPHY_GOLD_INDEX: SquidTrophyGold,
                   ENEMY_BUSH_INDEX: BushEnemy,
                   ENEMY_BARRICADE_INDEX: BarricadeEnemy,
                   ENEMY_SQUID_DOOR_INDEX: SquidDoorEnemy,
                   ENEMY_SAVE_INDEX: SaveEnemy}

class Mappe(BaseObject, SchedulerInterface, EventInterface):
    

    #other properties
    default_prop = {MAP_TILE_LIST: [],
                    MAP_WIDTH: 1,
                    MAP_HEIGHT: 1,
                    MAP_ACTORS: []}
    
    
    def __init__(self,junk, playerpos,  *args, **kwargs):
        super().__init__(junk, *args, **kwargs)
        self.screen_transitioning = False
        self.pan_direction = DIRECTION_DOWN
        self.final_player_pan_pos = (0,0)
        self.room_index = (0,0)
        self.tilemap = {}
        self.actor_data = {}
        self.actors = sDict()
        self.player_actor_index = self.addActor(PlayerActor)
        x, y = playerpos
        self.getPlayerActor().setPos(x, y)
        self.room_index = (int(x / MAP_SIZE[0]), int(y / MAP_SIZE[1]))
        setCameraXY(*map(operator.mul, self.room_index, MAP_SIZE))
        
        self.initializeMapTiles()
        self.initializeActors()
        
        self.loadRoom()
        self.Schedule(self.setActorLayers, 1, True)
        
        self.addCustomListener(START_SCREEN_TRANSITION_EVENT, self.startScreenTransition)
        
        resetLag()
        
        
    def setTileCollision(self, index, val):
        tile = self.tilemap.get(index, None)
        if tile:
            tile.setCollision(val)
        
    def setActorLayers(self):
        for i, actor in enumerate(sorted(self.actors.values(), key = lambda x: x.getPos()[1], reverse=True)):
            actor.updateActorLayer(ACTOR_LAYER_INCREMENT*i)
        
    def addActor(self, actor_type):
        actor_id = self.actors.append(actor_type(self))
        self.getActor(actor_id).setActorId(actor_id)
        self.getActor(actor_id).setRoomIndex(self.room_index)
        return actor_id
    
    def getActor(self, index):
        return self.actors.get(index, None)
    
    def getPlayerActor(self):
        return self.getActor(self.player_actor_index)
    
    def getEnemyActors(self):
        return [actor for actor in self.actors.values() if actor.isEnemy()]
    
    def getNonPlayerActors(self):
        return [actor for actor in self.actors.values() if not actor.isPlayer()]
    
    def getAllActors(self):
        return self.actors.values()
    
    def removeActor(self, actor_id):
        actor = self.actors.pop(actor_id, None)
        if actor:
            actor.destroy()
        
    def initializeMapTiles(self):
        for i, tiledata in enumerate(self.tile_list):
            x = i % self.width
            y = self.height - int(i / self.width) - 1
            self.tilemap[(x,y)] = MapTile(self)
            sprites = [None, None]
            priorities = [False, False]
            xflips = [False, False]
            yflips = [False, False]
            for key, index in SPRITE_DATA_SET:
                if key in tiledata:
                    sprites[index] = tiledata[key].get(MAPTILE_SPRITE, None)
                    priorities[index] = tiledata[key].get(MAPTILE_SPRITE_PRIORITY, False)
                    xflips[index] = tiledata[key].get(MAPTILE_SPRITE_XFLIP, False)
                    yflips[index] = tiledata[key].get(MAPTILE_SPRITE_YFLIP, False)
            self.tilemap[(x, y)].SetMaptileGraphics(sprites[0], sprites[1], priorities[0], priorities[1], xflips[0], xflips[1], yflips[0], yflips[1])
            self.tilemap[(x, y)].SetMaptilePos(x, y)
            try: self.tilemap[(x,y)].setCollision(tiledata[MAPTILE_COLLISION])
            except KeyError: pass
            try: self.tilemap[(x,y)].setPit(tiledata[MAPTILE_PIT])
            except KeyError: pass
        
    def initializeActors(self):
        self.actor_data.clear()
        for actor in self.map_actors:
            x, y = map(operator.mul, actor.get("pos", (0,0)), (MAP_TILE_SIZE,MAP_TILE_SIZE))
            room_index = (int(x / MAP_SIZE[0]), int(y/ MAP_SIZE[1]))
            if room_index not in self.actor_data:
                self.actor_data[room_index] = []
            self.actor_data[room_index].append({"pos":(x,y), "type":actor.get("type", None), "y_flip":actor.get("y_flip", False), "event_flag":actor.get("event_flag", "")})
            
    def loadRoom(self):
        for actor_data in self.actor_data.get(self.room_index, []):
            newtype = ENEMY_TYPES_DICT.get(actor_data.get("type", None), None)
            if newtype:
                newactor = self.getActor(self.addActor(newtype))
                newactor.setPos(*actor_data.get("pos", (0,0)))
                newactor.setSpriteFlip(y=actor_data.get("y_flip", False))
                newactor.setEventFlag(actor_data.get("event_flag", ""))
    
    def getMapTileAtPos(self, x, y):
        xpos = int(math.floor(x / MAP_TILE_SIZE))
        ypos = int(math.floor(y / MAP_TILE_SIZE))
        return self.tilemap.get((xpos, ypos), None)
    
    def setPlayerBubbleExists(self, val):
        pactor = self.getPlayerActor()
        if pactor:
            pactor.setBubbleExists(val)
            
    def setScreenTransitioning(self, val):
        self.screen_transitioning = val
        
    def getScreenTransitioning(self):
        return self.screen_transitioning
    
    def startScreenTransition(self, direction):
        x = self.room_index[0]
        y = self.room_index[1]
        if direction == DIRECTION_LEFT:
            x -= 1
        elif direction == DIRECTION_RIGHT:
            x += 1
        elif direction == DIRECTION_UP:
            y += 1
        else:
            y -= 1
        if not self.getScreenTransitioning() and x >= 0 and x < self.width/MAP_SIZE_TILES[0] and y >= 0 and y < self.height/MAP_SIZE_TILES[1] and (x,y) != self.room_index:
            self.pan_direction = direction
            self.setScreenTransitioning(True)
            self.room_index = (x,y)
            self.loadRoom()
            for actor in self.getNonPlayerActors():
                actor.pauseActor()
            self.getPlayerActor().setVelocity(0,0)
            self.getPlayerActor()._chargeFinish()
            self.getPlayerActor().pauseSpriteAnimations()
            resetLag()
            self.startScreenPan()
            
            
    def startScreenPan(self):
        self.Schedule(self._screenPan, 1, True)
        self.Schedule(self._finishScreenPan, PAN_SPEED)
        if self.pan_direction == DIRECTION_LEFT:
            self.final_player_pan_pos = tuple(map(operator.add, self.getPlayerActor().getPos(), [-PLAYER_PAN_DISTANCE, 0]))
        elif self.pan_direction == DIRECTION_RIGHT:
            self.final_player_pan_pos = tuple(map(operator.add, self.getPlayerActor().getPos(), [PLAYER_PAN_DISTANCE, 0]))
        elif self.pan_direction == DIRECTION_UP:
            self.final_player_pan_pos = tuple(map(operator.add, self.getPlayerActor().getPos(), [0, PLAYER_PAN_DISTANCE]))
        else:
            self.final_player_pan_pos = tuple(map(operator.add, self.getPlayerActor().getPos(), [0, -PLAYER_PAN_DISTANCE]))
        
    def _screenPan(self):
        pactor = self.getPlayerActor()
        if self.pan_direction == DIRECTION_LEFT:
            moveX(-MAP_SIZE[0] / PAN_SPEED)
            pactor.setPos(pactor.getPos()[0] - PLAYER_DX)
        elif self.pan_direction == DIRECTION_RIGHT:
            moveX(MAP_SIZE[0] / PAN_SPEED)
            pactor.setPos(pactor.getPos()[0] + PLAYER_DX)
        elif self.pan_direction == DIRECTION_UP:
            moveY(MAP_SIZE[1] / PAN_SPEED)
            pactor.setPos(y = pactor.getPos()[1] + PLAYER_DX)
        else:
            moveY(-MAP_SIZE[1] / PAN_SPEED)
            pactor.setPos(y = pactor.getPos()[1] - PLAYER_DX)
        
    def _finishScreenPan(self):
        self.Unschedule(self._screenPan)
        setCameraXY(*map(operator.mul, self.room_index, MAP_SIZE))
        self.getPlayerActor().setPos(*self.final_player_pan_pos)
        self.getPlayerActor().unpauseSpriteAnimations()
        for actor in [actor for actor in self.getNonPlayerActors() if actor.getRoomIndex() != self.room_index]:
            actor.cleanupSelf()
        for actor in self.getNonPlayerActors():
            actor.unpauseActor()
        self.setScreenTransitioning(False)
        
    
    def destroy(self):
        super().destroy()
        for tile in self.tilemap.values():
            tile.destroy()
        self.tilemap.clear()
        for actor in self.actors.values():
            actor.destroy()
        self.actors.clear()