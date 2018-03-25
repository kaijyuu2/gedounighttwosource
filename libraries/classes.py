# -*- coding: utf-8 -*-

from kaiengine.classes import *
from .config.paths import *


#included customn classes
def getCustMaps(directory = MAP_DIR):
    from . import mappe
    return findClasses(getClassDict(directory), directory, mappe.Mappe)