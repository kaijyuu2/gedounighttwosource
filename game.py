# -*- coding: utf-8 -*-

from sys import path as syspath
from os import path as ospath

from pyglet.app import run
from libraries.config import *

def _main():

    #initialize main game

    from libraries.main import init, close

    init()

    try:
        run()
    finally:
        close()

if __name__ == '__main__':
    _main()

