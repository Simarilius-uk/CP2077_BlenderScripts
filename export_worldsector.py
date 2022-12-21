# Script to export CP2077 streaming sectors from Blender 
# Just does changes to existing bits so far
# By Simarilius Nov 2022
# latest version available at https://github.com/Simarilius-uk/CP2077_BlenderScripts

import json
import glob
import os
import bpy
from mathutils import Vector, Matrix
C = bpy.context

project = 'F:\\CPmod\\nomad_garage'
path = os.path.join(project,'source\\raw\\base')

jsonpath = os.path.join(project,'sectors')

outpath = os.path.join(jsonpath,'output')
jsons = glob.glob(path+"\**\*.streamingsector.json", recursive = True)

#filepath=jsons[0]
for filepath in jsons:
    with open(filepath,'r') as f: 
          j=json.load(f) 
    nodes = j["Data"]["RootChunk"]["nodeData"]['Data']
    sectorName=os.path.basename(filepath)[:-5]

    Sector_coll=bpy.data.collections.get(sectorName)

    for i,node in enumerate(nodes):
        nodeIndex=node['NodeIndex']
        col=[x for x in Sector_coll.children if x['nodeIndex']==nodeIndex]
        # Not dealing with multiple instanced stuff yet
        print(len(col) , ' - Objects found with NodeIndex ',nodeIndex, ' this should be 1')
        if len(col)==1:
            obj=col[0].objects[0]
            print( node.keys())
            print(nodeIndex,node['Position']["X"],float("{:.9g}".format(obj.location[0]*100)))
            node['Position']["X"]= float("{:.9g}".format(obj.location[0]*100))
            node['Position']["Y"]= float("{:.9g}".format(obj.location[1]*100))
            node['Position']["Z"]= float("{:.9g}".format(obj.location[2]*100))
            node["Orientation"]["i"]= float("{:.9g}".format(obj.rotation_quaternion[0] ))
            node["Orientation"]["j"]= float("{:.9g}".format(obj.rotation_quaternion[1] ))
            node["Orientation"]["k"]= float("{:.9g}".format(obj.rotation_quaternion[2] ))
            node["Orientation"]["r"]= float("{:.9g}".format(obj.rotation_quaternion[3]))
            node["Scale"]["X"]= float("{:.9g}".format(obj.scale[0]*100))
            node["Scale"]["Y"]= float("{:.9g}".format(obj.scale[1]*100))
            node["Scale"]["Z"]= float("{:.9g}".format(obj.scale[2]*100))
            if 'billy' in node.keys():
                min=[0,0,0]
                for o in col[0].objects:
                    for b in o.bound_box:
                        if b[0]<min[0]:
                            min[0]=b[0]
                        if b[1]<min[1]:
                            min[1]=b[1]
                        if b[2]<min[2]:
                            min[2]=b[2]
                    max=min
                    for b in o.bound_box:
                        if b[0]>max[0]:
                            max[0]=b[0]
                        if b[1]>max[1]:
                            max[1]=b[1]
                        if b[2]>max[2]:
                            max[2]=b[2]
                node["Bounds"]['Max']["X"]= float("{:.9g}".format(obj.location[0]*100))
                node["Bounds"]['Max']["Y"]= float("{:.9g}".format(obj.location[1]*100))
                node["Bounds"]['Max']["Z"]= float("{:.9g}".format(obj.location[2]*100))
                node["Bounds"]['Min']["X"]= float("{:.9g}".format(obj.location[0]*100))
                node["Bounds"]['Min']["Y"]= float("{:.9g}".format(obj.location[1]*100))
                node["Bounds"]['Min']["Z"]= float("{:.9g}".format(obj.location[2]*100))
    pathout=os.path.join(outpath,os.path.basename(filepath))
    with open(pathout, 'w') as outfile:
        json.dump(j, outfile,indent=2)
    
        