# -*- coding: utf-8 -*-

from libraries.config import *

from kaiengine import settings
settings.initialize(DYNAMIC_SETTINGS_DEFAULTS) #can change in config's __init__
#done very early here to allow access to settings in initialization of imported modules

from kaiengine import event
from kaiengine.gameframehandler import  initializeGameFrames, closeGameFrames
from kaiengine.setup import *
from kaiengine.debug import debugMessage, checkDebugOn

from libraries.gamestate import initGamestate

#main game init
def init():
    event.addGameCloseListener(close)

    if checkDebugOn():
        debugMessage("WARNING: Launching in debug mode")

    #setup main window and initialize drivers
    setupWindowBasic("logo.png")

    setupDrivers()
    
    initGamestate()

    initializeGameFrames(main_loop)

#main game loop
def main_loop(dt):
    pass




#game closed
def close():
    closeGameFrames()
    settings.saveToFile()
    closeDrivers()

