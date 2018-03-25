# -*- coding: utf-8 -*-

from kaiengine.weakrefhelper import weakRef, unWeakRef
from kaiengine.objectinterface import GraphicInterface
from kaiengine.sprite import SpriteMulti
import copy, weakref

from libraries.config import *

class MapTile(GraphicInterface):


    #graphics directory
    vars()[GPATH] = copy.copy(MAP_TILE_GRAPHICS_FULL_PATH)

    def __init__(self, mappe, *args, **kwargs):
        super(MapTile, self).__init__(None, *args, **kwargs)
        self._mappe = weakRef(mappe)
        self._priorities = [False, False]
        self._xflips = [False, False]
        self._yflips = [False, False]
        self.collision = False
        self.pit = False #is a pit
        self.maptile_pos = [0,0]
        self.claims = {}
        self.setSprite(SpriteMulti())
        
    @property
    def mappe(self):
        return unWeakRef(self._mappe)
    @mappe.setter
    def mappe(self, val):
        debugMessage("Cannot set map directly")

    def SetMaptileGraphics(self, sprite1, sprite2, priority1, priority2, xflip1, xflip2, yflip1, yflip2):
        self._priorities = [priority1, priority2]
        self._xflips = [xflip1, xflip2]
        self._yflips = [yflip1, yflip2]
        if sprite1 != None:
            self._setMaptileMultiSprite(0, sprite1)
        else:
            self.sprite.remove_sprite(0)
        if sprite2 != None:
            self._setMaptileMultiSprite(1, sprite2)
        else:
            self.sprite.remove_sprite(1)

    def setMaptileSprite(self, layer, path):
        self.sprite.setMultiSprite(layer, self.getGraphicPath(path))
        self._setMaptileSprite(layer)

    def _setMaptileMultiSprite(self, layer, path):
        self.sprite.add_sprite(self.getGraphicPath(path), layer)
        self._setMaptileSprite(layer)

    def _setMaptileSprite(self, layer):
        self.sprite.setMultiLayer(layer, MAPTILE_LAYER + (MAPTILE_PRIORITY_LAYER  if self._priorities[layer] else 0) + (MAPTILE_PIT_LAYER  if self.pit else 0))
        self.sprite.setMultiFlip(layer, [self._xflips[layer], self._yflips[layer]])
        self.SetMaptilePos()

    def SetMaptilePos(self, x = None, y = None):
        if x is None: x = self.maptile_pos[0]
        if y is None: y = self.maptile_pos[1]
        self.maptile_pos = [x,y]
        self.setPos(x * MAP_TILE_SIZE, y * MAP_TILE_SIZE)

    def setMaptilePriority(self, layer, val):
        self._priorities[layer] = val
        self._setMaptileSprite(layer)

    def GetMaptilePos(self):
        return self.maptile_pos[:]

    def GetMaptileGraphicalPos(self):
        return self.getPos()

    def GetMaptileGraphicalCenter(self):
        pos = self.GetMaptileGraphicalPos()
        return pos[0] + MAP_TILE_SIZE/2, pos[1] + MAP_TILE_SIZE/2

    def setCollision(self, val):
        self.collision = val

    def getCollision(self):
        return self.collision
    
    def setPit(self, val):
        self.pit = val
        self._setMaptileSprite(0)
        self._setMaptileSprite(1)
        
    def getPit(self):
        return self.pit
    