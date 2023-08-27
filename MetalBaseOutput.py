#################################################################################################################
# Initial attempt at getting metal_base info back out of blender.
# Simarilius, August 2023
##################################################################################################################

import bpy
import json
import os
import numpy as np
import copy

def make_rel(filepath):
    before,mid,after=filepath.partition('base\\')
    return mid+after

def get_node_by_key(nodes, label):
    valNodes = [node for node in nodes if node.label==label]
    if len(valNodes)>0:
        valNode=valNodes[0]
        return valNode
    else:
        return None

def extract_imgpath_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        Data[label]['DepotPath']['$value']=make_rel(valNode.image.filepath)

def extract_value_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        Data[label]=valNode.outputs[0].default_value

def extract_RGB_and_setjson(nodes, Data, label):
    valNode = get_node_by_key(nodes, label)
    if valNode:
        # order based on the create RGB node bit in common
        Data[label]['X']=valNode.outputs[0].default_value[0]
        Data[label]['Y']=valNode.outputs[0].default_value[1]
        Data[label]['Z']=valNode.outputs[0].default_value[2]
        Data[label]['W']=valNode.outputs[0].default_value[3]

##################################################################################################################
# These are from common.py in the plugin, can be replaced by an include if its put in the plugin 

def openJSON(path, mode='r',  ProjPath='', DepotPath=''):
    inproj=os.path.join(ProjPath,path)
    if os.path.exists(inproj):
        file = open(inproj,mode)
    else:
        file = open(os.path.join(DepotPath,path),mode)
    return file

    
##################################################################################################################
obj=bpy.context.active_object
mat=obj.material_slots[0].material
nodes=mat.node_tree.nodes    
MaterialTemplate = mat.get('MaterialTemplate')
if MaterialTemplate and MaterialTemplate=="engine\\materials\\metal_base.remt":
    ProjPath=mat.get('ProjPath')
    DepotPath=mat.get('DepotPath')
    file = open( "resources\\metal_base_template.mi.json",mode='r')
    if not json:
        bpy.ops.cp77.message_box('INVOKE_DEFAULT', message="No json found for Material Template")
        
    mi_temp = json.loads(file.read())
    file.close()

    valNode = get_node_by_key(nodes, 'EnableMask')
    if valNode:
        mi_temp['Data']['RootChunk']['enableMask']=int(valNode.outputs[0].default_value)

    values = mi_temp['Data']['RootChunk']['values']
    for Data in values:
        if "BaseColor" in Data:
            extract_imgpath_and_setjson(nodes, Data, 'BaseColor')

        if "BaseColorScale" in Data:
            extract_RGB_and_setjson(nodes, Data,'BaseColorScale')

        if "Metalness" in Data:
            extract_imgpath_and_setjson(nodes, Data,'Metalness')
           
        if 'MetalnessScale' in Data:
            extract_value_and_setjson(nodes, Data,'MetalnessScale')

        if 'MetalnessBias' in Data:
            extract_value_and_setjson(nodes, Data,'MetalnessBias')
            
        if "Roughness" in Data:
            extract_imgpath_and_setjson(nodes, Data, 'Roughness')
        
        if 'RoughnessScale' in Data:
            extract_value_and_setjson(nodes, Data,'RoughnessScale')

        if 'RoughnesssBias' in Data:
            extract_value_and_setjson(nodes, Data,'RoughnesssBias')

        if "AlphaThreshold" in Data:
            extract_value_and_setjson(nodes, Data,'AlphaThreshold')

        if "Normal" in Data:
            extract_imgpath_and_setjson(nodes, Data, 'Normal')
 
        if "EmissiveColor" in Data:
            extract_RGB_and_setjson(nodes, Data,'EmissiveColor')

        if "Emissive" in Data:
           extract_imgpath_and_setjson(nodes, Data, 'Emissive')

        if "EmissiveEV" in Data:
            Data[label] = pBSDF.inputs['Emission Strength'].default_value + 1 # took one off in import

    mi_filepath=obj.users_collection[0]['orig_filepath'][:-4]+'.mi.json'
    with open(mi_filepath, 'w') as outfile:
        json.dump(mi_temp, outfile,indent=2)  
        print('Saved to ',mi_filepath)  