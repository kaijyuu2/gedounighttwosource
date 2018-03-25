# -*- coding: utf-8 -*-


from kaiengine.audio import *
from kaiengine import audio
from kaiengine.resource import toStringPath

from libraries.config import *

def playSound(path, *args, **kwargs):
    return audio.playSound(toStringPath(FULL_SFX_PATH + [path]), *args, **kwargs)