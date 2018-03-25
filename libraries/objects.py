# -*- coding: utf-8 -*-


from kaiengine.objects import *
from .config import *
from . import classes
import os



def createMap(filepath, *args, **kwargs):
    return createObject(filepath, MAP_FULL_PATH, MAP_EXTENSION, classes.getCustMaps, *args, **kwargs)
