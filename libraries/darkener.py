# -*- coding: utf-8 -*-

from kaiengine.objectinterface import GraphicInterface, SchedulerInterface
from kaiengine.display import getWindowDimensionsScaled
from kaiengine.debug import debugMessage

from libraries.config import *

class Darkener(GraphicInterface, SchedulerInterface):

    vars()[GPATH] = MISC_GRAPHICS_FULL_PATH

    def __init__(self, color = COLOR_BLACK, *args, **kwargs):
        super(Darkener, self).__init__(*args, **kwargs)
        self.fade_total_time = 0
        self.fade_time = 0
        self.done_fading = True

        self.setSprite(WHITE_PIXEL_FILENAME)
        self.setSpriteLayer(DARKENER_LAYER)
        self.setSpriteDimensions(*getWindowDimensionsScaled())
        self.setSpriteColor(*color)
        self.setSpriteAlpha(0.0)
        self.setSpriteFollowCamera(True)



    def fadeIn(self, time):
        self._fadeStart(time)
        self.setSpriteAlpha(1.0)
        self.Schedule(self._fadeIn, 0, True)

    def fadeOut(self, time):
        self._fadeStart(time)
        self.setSpriteAlpha(0.0)
        self.Schedule(self._fadeOut, 0, True)

    def checkDoneFading(self):
        return self.done_fading


    def _fadeStart(self, time):
        self.Unschedule(self._fadeIn)
        self.Unschedule(self._fadeOut)
        time = max(0.0, float(time))
        self.fade_total_time = time
        self.fade_time = time
        self.done_fading = False

    def _fadeIn(self):
        self.fade_time -= 1
        self.setSpriteAlpha(round(max(0.0, self.fade_time) * 16 / self.fade_total_time) / 16)
        if self.fade_time <= 0:
            self.done_fading = True
            self.Unschedule(self._fadeIn)

    def _fadeOut(self):
        self.fade_time -= 1
        self.setSpriteAlpha(1.0 - round(max(0.0, self.fade_time) * 16 / self.fade_total_time) / 16)
        if self.fade_time <= 0:
            self.done_fading = True
            self.Unschedule(self._fadeOut)