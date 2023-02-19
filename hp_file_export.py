#  hair profile export code as requested by IslandDancer
#  by Simarilius Feb 2023
#
#  Writes the gradient stops on a material back to an hp json file for import to wkit
#  You need to add a custom string property named hp_file to the material with the path to the original hp in the depot
#  for instance mine was set to F:\MaterialDepot\base\characters\common\hair\textures\hair_profiles\blue_sapphire.hp.json
#  it will create/overwrite the json for this hp file within the project folder specified.
#  prints the stop info to the System Console window too.
import math 
import bpy
import os
import json
from bpy import context as C

def to_gam(c):
     if c < 0.0031308:
         srgb = 0.0 if c < 0.0 else c * 12.92
     else:
         srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
     return max(min(int(srgb * 255 + 0.5), 255), 0)



D = bpy.data

# Input the slot number of the material here ( its -1 from the number shown in the top of the node editor helpfully
Slot_no=0

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
        print('Color - ',int(to_gam(stop.color[0])),int(to_gam(stop.color[1])),int(to_gam(stop.color[2])))
        print(' ')
        if i<len(j['Data']['RootChunk'][grad]):
            j['Data']['RootChunk'][grad][i]['color']['Red'] = int(to_gam(stop.color[0]))
            j['Data']['RootChunk'][grad][i]['color']['Green'] = int(to_gam(stop.color[1]))
            j['Data']['RootChunk'][grad][i]['color']['Blue'] =int(to_gam(stop.color[2]))
            j['Data']['RootChunk'][grad][i]['color']['Alpha'] =int(stop.color[3]*255)
            j['Data']['RootChunk'][grad][i]['value']=stop.position
        else:
            new_col={'Red':int(to_gam(stop.color[0])),'Green':int(to_gam(stop.color[1])),'Blue':int(to_gam(stop.color[2])),'Alpha':int(stop.color[3]*255)}
            new_stop={'color':new_col, 'value':stop.position}
            j['Data']['RootChunk'][grad].append(new_stop)
            
outpath = os.path.join(project_path,hp[hp.index('base'):])


if not os.path.exists( os.path.dirname(outpath)):
    os.makedirs(os.path.dirname(outpath))
    

with open(outpath, 'w') as outfile:
    json.dump(j, outfile,indent=2)