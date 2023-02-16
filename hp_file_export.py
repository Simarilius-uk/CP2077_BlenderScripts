#  hair profile export code as requested by IslandDancer
#  by Simarilius Feb 2023
#
#  Writes the gradient stops on a material back to an hp json file for import to wkit
#  You need to add a custom string property named hp_file to the material with the path to the original hp in the depot
#  for instance mine was set to F:\MaterialDepot\base\characters\common\hair\textures\hair_profiles\blue_sapphire.hp.json
#  it will create/overwrite the json for this hp file within the project folder specified.
#  prints the stop info to the System Console window too.

import bpy
import os
import json
from bpy import context as C

D = bpy.data

# Input the slot number of the material here ( its -1 from the number shown in the top of the node editor helpfully
Slot_no=4

# path of the raw folder of the project to save the hp to.
project_path = 'F:\\CPMod\\IslandDancer\\source\\raw'

#  You need to have the object selected in the viewport
obj=C.selected_objects[0]

mat=obj.material_slots[ obj.material_slots.keys()[Slot_no]]
hp=  D.materials[mat.name]['hp_file']

with open(hp,'r') as f: 
    j=json.load(f)

crs=['ColorRamp','ColorRamp.001']

nodes = obj.material_slots[ obj.material_slots.keys()[Slot_no]].material.node_tree.nodes
print(' ')
print('Gradient Stops for ',obj.material_slots.keys()[Slot_no])

for crname in crs:
    cr=nodes[crname]
    print(' ')
    print('Stop info for ',cr.label)
    grad=''
    if cr.label=='GradientEntriesRootToTip':
        grad='gradientEntriesRootToTip'
    elif cr.label=='GradientEntriesID':
        grad='gradientEntriesID'
    else:
        break        

    for i,stop in enumerate(cr.color_ramp.elements):
        print('Stop # ',i)
        print('Position - ',stop.position)
        print('Color - ',int(stop.color[0]*255),int(stop.color[1]*255),int(stop.color[2]*255))
        print(' ')
        j['Data']['RootChunk'][grad][i]['color']['Red'] = int(stop.color[0]*255)
        j['Data']['RootChunk'][grad][i]['color']['Green'] = int(stop.color[1]*255)
        j['Data']['RootChunk'][grad][i]['color']['Blue'] =int(stop.color[2]*255)
        j['Data']['RootChunk'][grad][i]['color']['Alpha'] =int(stop.color[3]*255)
        j['Data']['RootChunk'][grad][i]['value']=stop.position

outpath = os.path.join(project_path,hp[hp.index('base'):])


if not os.path.exists( os.path.dirname(outpath)):
    os.makedirs(os.path.dirname(outpath))
    

with open(outpath, 'w') as outfile:
    json.dump(j, outfile,indent=2)