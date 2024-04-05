# If you ever have a model where you've imported tonnes of sectors trying to work out what you need, 
# then if you drag select the bit you want and run this it will print the list of sectors that the selection are in. 
# for instance if you import a big list of sectors without materials to find what you want and wanted to be able to get a list to do a with materials import.

import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *

objs=C.selected_objects
sector_list=[]
for obj in objs:
    obj_coll=obj.users_collection[0]
    if 'sectorName' in obj_coll.keys():
        sector=obj_coll['sectorName']
        if sector not in sector_list:
            sector_list.append(sector)

print(sector_list)
