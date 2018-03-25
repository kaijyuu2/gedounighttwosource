# -*- coding: utf-8 -*-

import copy

from kaiengine import savegame
from kaiengine.audio import playMusic, stopMusic
from kaiengine.display import getWindowDimensionsScaled, createLabel
from kaiengine.objectinterface import SchedulerInterface, GraphicInterface, EventInterface
from kaiengine.resource import toStringPath, ResourceUnavailableError
from kaiengine.event import callQuery
from kaiengine.gameframehandler import resetLag

from libraries.objects import createMap
from libraries.darkener import Darkener

from libraries.config import *

HEALTH_Y_OFFSET = -24
HEALTH_X_OFFSET = 8
HEALTH_X_STEP = 16

SQUID_Y_OFFSET = -24
SQUID_X_STEP = 16
SQUID_X_OFFSET = 256 - SQUID_X_STEP*4

SQUID_ENUM = {SQUID_TROPHY_RED_INDEX: 0,
              SQUID_TROPHY_GREEN_INDEX: 1,
              SQUID_TROPHY_BLUE_INDEX:2}
SQUID_GRAPHICS = {SQUID_TROPHY_RED_INDEX: "squid_trophy_red.png",
              SQUID_TROPHY_GREEN_INDEX: "squid_trophy_green.png",
              SQUID_TROPHY_BLUE_INDEX:"squid_trophy_blue.png",
              SQUID_TROPHY_GOLD_INDEX:"squid_trophy_gold.png"}

MAP_NAME = "test"

ENDING_SQUID_X_SPACING = 32

glob = None

def initGamestate():
    global glob
    glob = Gamestate()


def getMapTileAtPos(*args, **kwargs):
    if glob:
        return glob.getMapTileAtPos(*args, **kwargs)
    return None

def setEventFlag(*args, **kwargs):
    if glob:
        glob.setEventFlag(*args, **kwargs)
        
def getEventFlag(*args, **kwargs):
    if glob:
        return glob.getEventFlag(*args, **kwargs)
    return None

class Gamestate(SchedulerInterface, EventInterface):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_starting_pos = (128, 48)
        self.game_flags = {}
        self.trophies_obtained = {}
        self.player_health = 3
        self.fade_darkener = Darkener()
        self.bg = GraphicInterface()
        self.bg.setSprite(toStringPath(BG_GRAPHICS_FULL_PATH + ["loading.png"]))
        self.bg.setSpriteLayer(LOADING_LAYER)
        self.mappe = None
        
        self.ending_player = None
        self.ending_text = None
        self.ending_text2 = None
        self.ending_text3 = None
        self.ending_squids = []
        
        self.player_health_sprites = []
        for i in range(3):
            self.player_health_sprites.append(GraphicInterface())
            self.player_health_sprites[-1].setSprite(toStringPath(UI_GRAPHICS_FULL_PATH  + ["health.png"]))
            self.player_health_sprites[-1].setPos(HEALTH_X_OFFSET + HEALTH_X_STEP*i, getWindowDimensionsScaled()[1] + HEALTH_Y_OFFSET)
            self.player_health_sprites[-1].setSpriteFollowCamera(True)
            self.player_health_sprites[-1].setSpriteLayer(UI_LAYER)
            
        self.squid_trophy_sprites = []
        for i in range(3):
            self.squid_trophy_sprites.append(GraphicInterface())
            self.squid_trophy_sprites[-1].setSpriteFollowCamera(True)
            self.squid_trophy_sprites[-1].setPos(SQUID_X_OFFSET + SQUID_X_STEP*i, getWindowDimensionsScaled()[1] + SQUID_Y_OFFSET)
            self.squid_trophy_sprites[-1].setSpriteLayer(UI_LAYER)
            
        
        self.Schedule(self.createStartingMap, 2)
        
        self.addCustomListener(SQUID_TROPHY_OBTAINED_EVENT, self.squidTrophyObtained)
        self.addQueryListener(SQUID_TROPHY_OBTAINED_QUERY, self.checkTrophyObtained)
        self.addQueryListener(ALL_SQUID_TROPHIES_OBTAINED_QUERY, self.hasAllTrophies)
        self.addCustomListener(PLAYER_REDUCE_HP_EVENT, self.reduceHP)
        self.addCustomListener(PLAYER_MAX_HP_EVENT, self.maxHP)
        self.addQueryListener(CHECK_PLAYER_DEAD_QUERY, self.checkPlayerDead)
        self.addCustomListener(PUSH_SAVE_EVENT, self.pushSave)
        self.addCustomListener(FINAL_SQUID_OBTAINED_EVENT , self.finalSquidObtained)
        self.addCustomListener(GAME_LOST_EVENT, self.gameLost)
        
        self.loadSave()
        
    def createStartingMap(self):
        self.mappe = createMap(MAP_NAME, self.player_starting_pos) #just one map for now
        self.fade_darkener.fadeIn(60)
        if self.bg:
            self.bg.destroy()
        self.bg = None
        playMusic(toStringPath(FULL_MUSIC_PATH + ["bgmusic.ogg"]))
        
        
    def getMapTileAtPos(self, *args, **kwargs):
        if self.mappe:
            return self.mappe.getMapTileAtPos(*args, **kwargs)
        return None
    
    def squidTrophyObtained(self, trophy_index):
        self.trophies_obtained[trophy_index] = True
        self.updateTrophyGraphics()
        
    def updateTrophyGraphics(self):
        for trophy in self.squid_trophy_sprites:
            trophy.setSpriteAlpha(0.0)
        for trophy_index in self.trophies_obtained.keys():
            index = SQUID_ENUM.get(trophy_index, 999)
            try:
                self.squid_trophy_sprites[index].setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + [SQUID_GRAPHICS[trophy_index]]))
                self.squid_trophy_sprites[index].setSpriteAlpha(1.0)
            except (KeyError, IndexError):
                pass
        
    def checkTrophyObtained(self, trophy_index):
        return self.trophies_obtained.get(trophy_index, False)
    
    def hasAllTrophies(self):
        for i in {SQUID_TROPHY_BLUE_INDEX, SQUID_TROPHY_RED_INDEX, SQUID_TROPHY_GREEN_INDEX}:
            if not self.checkTrophyObtained(i):
                return False
        return True
    
    def maxHP(self):
        self.player_health = 3
        self.updateHealth()
        
    def reduceHP(self):
        self.player_health -= 1
        self.updateHealth()
        
    def updateHealth(self):
        for i in range(3):
            if i < self.player_health:
                self.player_health_sprites[i].setSpriteAnimation("FULL")
            else:
                self.player_health_sprites[i].setSpriteAnimation("EMPTY")
                
    def checkPlayerDead(self):
        return self.player_health <= 0
    
    def setEventFlag(self, key, val):
        self.game_flags[key] = val
        
    def getEventFlag(self, key, default = "asdfadsgiangiang"):
        try:
            return self.game_flags[key] 
        except KeyError:
            if default != "asdfadsgiangiang":
                return default
            raise
            
    def pushSave(self):
        savegame.setValue(SAVE_TROPHIES, copy.deepcopy(self.trophies_obtained))
        savegame.setValue(SAVE_EVENT_FLAGS, copy.deepcopy(self.game_flags))
        savegame.setValue(SAVE_PLAYER_POS, callQuery(PLAYER_GET_POS_QUERY))
        savegame.commitSave(SAVE_GAME_NAME)
        
    def loadSave(self):
        try:
            savegame.loadSave(SAVE_GAME_NAME)
        except ResourceUnavailableError:
            pass
        self.game_flags = copy.deepcopy(savegame.getValue(SAVE_EVENT_FLAGS, {}))
        self.trophies_obtained = copy.deepcopy(savegame.getValue(SAVE_TROPHIES, {}))
        playerpos = savegame.getValue(SAVE_PLAYER_POS, None)
        if playerpos is None:
            playerpos = (128, 48)
        self.player_starting_pos = playerpos
        self.updateTrophyGraphics()
        
    def finalSquidObtained(self):
        for actor in self.mappe.getAllActors():
            actor.pauseActor()
        self.fade_darkener.fadeOut(60)
        self.Schedule(self.startCredits, 60)
        
        
    def startCredits(self):
        self.removeMapData()
        resetLag()
        self.fade_darkener.fadeIn(60)
        playMusic(toStringPath(FULL_MUSIC_PATH + ["ending.ogg"]))
        self.removeEndingData()
        self.ending_player = GraphicInterface()
        self.ending_player.setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + ["char.png"]))
        self.ending_player.setPos(128,128)
        self.ending_player.setSpriteCenter(True, True)
        self.ending_player.setSpriteFollowCamera(True)
        self.ending_player.setSpriteAnimation("WALK_DOWN")
        self.ending_text = createLabel("Thanks for playing!", font = "kaimono3.gfont2")
        self.ending_text.setPos(128, 64)
        self.ending_text.follow_camera = True
        self.ending_text.setCenter(True,True)
        self.ending_text2 = createLabel("You got the", font = "kaimono3.gfont2")
        self.ending_text2.setPos(128, 192)
        self.ending_text2.follow_camera = True
        self.ending_text2.setCenter(True,True)
        self.ending_text3 = createLabel("Golden Squid!", font = "kaimono3.gfont2")
        self.ending_text3.setPos(128, 176)
        self.ending_text3.follow_camera = True
        self.ending_text3.setCenter(True,True)
        xoffset = getWindowDimensionsScaled()[0]/2 - (len(SQUID_GRAPHICS)-1)*ENDING_SQUID_X_SPACING/2
        for i, val in enumerate(SQUID_GRAPHICS.values()):
            self.ending_squids.append(GraphicInterface())
            self.ending_squids[-1].setSprite(toStringPath(CHAR_GRAPHICS_FULL_PATH + [val]))
            self.ending_squids[-1].setSpriteCenter(True, True)
            self.ending_squids[-1].setSpriteFollowCamera(True)
            self.ending_squids[-1].setPos(xoffset + i*ENDING_SQUID_X_SPACING, 96)
        
    def removeMapData(self):
        if self.mappe:
            self.mappe.destroy()
        self.mappe = None
        if self.bg:
            self.bg.destroy()
        self.bg = None
        for sprite in self.player_health_sprites:
            sprite.destroy()
        self.player_health_sprites.clear()
        for sprite in self.squid_trophy_sprites:
            sprite.destroy()
        self.squid_trophy_sprites.clear()
        
    def removeEndingData(self):
        if self.ending_player:
            self.ending_player.destroy()
        self.ending_player = None
        if self.ending_text:
            self.ending_text.destroy()
        self.ending_text = None
        if self.ending_text2:
            self.ending_text2.destroy()
        self.ending_text2 = None
        if self.ending_text3:
            self.ending_text3.destroy()
        self.ending_text3 = None
        for squid in self.ending_squids:
            squid.destroy()
        self.ending_squids.clear()
        
    def gameLost(self):
        self.fade_darkener.fadeOut(60)
        self.Schedule(self.resetToSave, 60)
        
    def resetToSave(self):
        stopMusic()
        if self.mappe:
            self.mappe.destroy()
        self.loadSave()
        if self.bg:
            self.bg.destroy()
        self.fade_darkener.fadeIn(1)
        self.bg = GraphicInterface()
        self.bg.setSprite(toStringPath(BG_GRAPHICS_FULL_PATH + ["loading.png"]))
        self.bg.setSpriteLayer(LOADING_LAYER)
        self.bg.setSpriteFollowCamera(True)
        self.Schedule(self.createStartingMap, 2)
        
        
    def destroy(self):
        super().destroy()
        self.removeMapData()
        self.removeEndingData()
        if self.fade_darkener:
            self.fade_darkener.destroy()
        self.fade_darkener = None
        