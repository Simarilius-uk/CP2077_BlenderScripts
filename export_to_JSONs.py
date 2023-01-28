# Script to export CP2077 streaming sectors from Blender 
# Just does changes to existing bits so far
# By Simarilius Jan 2023
# latest version available at https://github.com/Simarilius-uk/CP2077_BlenderScripts
#
#  __       __   ___  __   __                        __   ___  __  ___  __   __      ___  __    ___         __  
# /  ` \ / |__) |__  |__) |__) |  | |\ | |__/       /__` |__  /  `  |  /  \ |__)    |__  |  \ |  |  | |\ | / _` 
# \__,  |  |__) |___ |  \ |    \__/ | \| |  \       .__/ |___ \__,  |  \__/ |  \    |___ |__/ |  |  | | \| \__> 
#                                                                                                              
# Havent written a tutorial for this yet so thought I should add some instructions
# 1) Import the sector you want to edit using the Import_and_instance_comb.py script from the github linked above.
# 2) You can move the existing objects around and this will be exported
# 3) If you delete the mesh from a collector but leave the collector, the script will set the scale for that instance to -1 which stops it rendering in game
# 4) to add new stuff create a new collector with the sector name with _new on the end ie interior_1_1_0_1.streamingsector_new and then copy any objects you want into it.
# 5) If its stuff already in the sector it will create nodeData nodes to instance it, if its from another imported sector it will copy the main node too
#    Its assuming it can find the json for the sector its copying from in the project, dont be clever merging blends or whatever.
# 6) not all nodetypes are supported yet, have a look at the case statements to see which are
# 

import json
import glob
import os
import bpy
import copy
from mathutils import Vector, Matrix
C = bpy.context

#Set this to your project directory
project = 'F:\\CPmod\\meshdecal_parralax'
path = os.path.join(project,'source\\raw\\base')

#its currently set to output the modified jsons to an output folder in the project dir (create one before running)
#you can change this to a path if you prefer
outpath = os.path.join(project,'output')



def set_pos(inst,obj):  
    #print(inst)  
    if 'Position'in inst.keys():
        if 'Properties' in inst['Position'].keys():
            inst['Position']['Properties']['X']= float("{:.9g}".format(obj.location[0]*100))
            inst['Position']['Properties']['Y'] = float("{:.9g}".format(obj.location[1]*100))
            inst['Position']['Properties']['Z'] = float("{:.9g}".format(obj.location[2]*100))
        else:
            if 'X' in inst['Position'].keys():
                inst['Position']['X'] = float("{:.9g}".format(obj.location[0]*100))
                inst['Position']['Y'] = float("{:.9g}".format(obj.location[1]*100))
                inst['Position']['Z'] = float("{:.9g}".format(obj.location[2]*100))
            else:
                inst['Position']['x'] = float("{:.9g}".format(obj.location[0]*100))
                inst['Position']['y'] = float("{:.9g}".format(obj.location[1]*100))
                inst['Position']['z'] = float("{:.9g}".format(obj.location[2]*100))
    elif 'position' in inst.keys():
        inst['position']['X'] = float("{:.9g}".format(obj.location[0]*100))
        inst['position']['Y'] = float("{:.9g}".format(obj.location[1]*100))
        inst['position']['Z'] = float("{:.9g}".format(obj.location[2]*100))
    elif 'translation' in inst.keys():
        inst['translation']['X'] = float("{:.9g}".format(obj.location[0]*100))
        inst['translation']['Y'] = float("{:.9g}".format(obj.location[1]*100))
        inst['translation']['Z'] = float("{:.9g}".format(obj.location[2]*100))


def set_rot(inst,obj):
    if 'Orientation' in inst.keys():
        if 'Properties' in inst['Orientation'].keys():
            inst['Orientation']['Properties']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Orientation']['Properties']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['Orientation']['Properties']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))  
            inst['Orientation']['Properties']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))        
        else:
            inst['Orientation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Orientation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] ))
            inst['Orientation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['Orientation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))
    elif 'Rotation' in inst.keys():
            inst['Rotation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['Rotation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['Rotation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['Rotation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))
    elif 'rotation' in inst.keys():
            inst['rotation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['rotation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['rotation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['rotation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))


def set_scale(inst,obj):
    if 'Scale' in inst.keys():
        if 'Properties' in inst['Scale'].keys():
            inst['Scale']['Properties']['X'] = float("{:.9g}".format(obj.scale[0]*100))
            inst['Scale']['Properties']['Y'] = float("{:.9g}".format(obj.scale[1]*100))
            inst['Scale']['Properties']['Z']= float("{:.9g}".format(obj.scale[2]*100))
        else:
            inst['Scale']['X']  = float("{:.9g}".format(obj.scale[0]*100))
            inst['Scale']['Y']  = float("{:.9g}".format(obj.scale[1]*100))
            inst['Scale']['Z']  = float("{:.9g}".format(obj.scale[2]*100))
    elif 'scale' in inst.keys():
            inst['scale']['X']  = float("{:.9g}".format(obj.scale[0]*100))
            inst['scale']['Y']  = float("{:.9g}".format(obj.scale[1]*100))
            inst['scale']['Z']  = float("{:.9g}".format(obj.scale[2]*100))

def set_bounds(node, obj):
        node["Bounds"]['Max']["X"]= float("{:.9g}".format(obj.location[0]*100))
        node["Bounds"]['Max']["Y"]= float("{:.9g}".format(obj.location[1]*100))
        node["Bounds"]['Max']["Z"]= float("{:.9g}".format(obj.location[2]*100))
        node["Bounds"]['Min']["X"]= float("{:.9g}".format(obj.location[0]*100))
        node["Bounds"]['Min']["Y"]= float("{:.9g}".format(obj.location[1]*100))
        node["Bounds"]['Min']["Z"]= float("{:.9g}".format(obj.location[2]*100))

def find_col(NodeIndex,Inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.children if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        return inst[0]

def find_decal(NodeIndex,Inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.objects if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return none
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        return inst[0]

def createNodeData(t, col, nodeIndex, obj, ID):
    print(ID)
    t.append({'Id':ID,'Uk10':1088,'Uk11':256,'Uk12':0,'UkFloat1':60.47757,'UkHash1':1088,'QuestPrefabRefHash': 0,'MaxStreamingDistance': 3.4028235e+38})
    new = t[len(t)-1]
    new['NodeIndex']=nodeIndex
    new['Position']={'$type': 'Vector4','W':0,'X':float("{:.9g}".format(obj.location[0]*100)),'Y':float("{:.9g}".format(obj.location[1]*100)),'Z':float("{:.9g}".format(obj.location[2]*100))}
    new['Pivot']= {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0}
    new['Bounds']= {'$type': 'Box'}
    new['Bounds']['Max']={'$type': 'Vector4','X':float("{:.9g}".format(obj.location[0]*100)),'Y':float("{:.9g}".format(obj.location[1]*100)),'Z':float("{:.9g}".format(obj.location[2]*100))}
    new['Bounds']['Min']={'$type': 'Vector4','X':float("{:.9g}".format(obj.location[0]*100)),'Y':float("{:.9g}".format(obj.location[1]*100)),'Z':float("{:.9g}".format(obj.location[2]*100))}
    new['Orientation']={'$type': 'Quaternion','r':float("{:.9g}".format(obj.rotation_quaternion[0])),'i':float("{:.9g}".format(obj.rotation_quaternion[1])),'j':float("{:.9g}".format(obj.rotation_quaternion[2])),'k':float("{:.9g}".format(obj.rotation_quaternion[3]))}
    new['Scale']= {'$type': 'Vector3', 'X':  float("{:.9g}".format(obj.scale[0]*100)), 'Y':  float("{:.9g}".format(obj.scale[1]*100)), 'Z':  float("{:.9g}".format(obj.scale[2]*100))}
    




jsons = glob.glob(path+"\**\*.streamingsector.json", recursive = True)
bpy.ops.mesh.primitive_cube_add(size=.01, scale=(-1,-1,-1),location=(0,0,0))
neg_cube=C.selected_objects[0]
neg_cube.scale=(-1,-1,-1)

 #       __               __      __  ___       ___  ___ 
 # |\/| /  \ \  / | |\ | / _`    /__`  |  |  | |__  |__  
 # |  | \__/  \/  | | \| \__>    .__/  |  \__/ |    |    
 #
                                                      
for filepath in jsons:
    with open(filepath,'r') as f: 
          j=json.load(f) 
    nodes = j["Data"]["RootChunk"]["nodes"]
    t=j['Data']['RootChunk']['nodeData']['Data']
    sectorName=os.path.basename(filepath)[:-5]

    Sector_coll=bpy.data.collections.get(sectorName)
    Sector_coll['filepath']=filepath
    Sector_additions_coll=bpy.data.collections.get(sectorName+'_new')
    for i,e in enumerate(nodes):
        data = e['Data']
        type = data['$type']
        match type:
            case 'worldInstancedMeshNode' :
                meshname = data['mesh']['DepotPath'] 
                num=data['worldTransformsBuffer']['numElements']
                start=data['worldTransformsBuffer']['startIndex']
                if(meshname != 0):
                    for idx in range(start, start+num):
                        
                        if 'Data' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                inst_trans=data['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                                       
                        elif 'HandleRefId' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                            bufferID = int(data['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId'])
                            ref=e
                            for n in nodes:
                                if n['HandleId']==str(bufferID-1):
                                    ref=n
                            inst_trans = ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                        obj_col=find_col(i,idx,Sector_coll)    
                        if obj_col:
                            if len(obj_col.objects)>0:
                                obj=obj_col.objects[0]
                                set_pos(inst_trans,obj)
                                set_rot(inst_trans,obj)
                                set_scale(inst_trans,obj)
                            else:
                                obj=neg_cube
                                set_scale(inst_trans,obj)
            case 'worldStaticDecalNode':
                #print('worldStaticDecalNode')
                instances = [x for x in t if x['NodeIndex'] == i]
                for idx,inst in enumerate(instances):
                    obj=find_decal(i,idx,Sector_coll)
                    if obj:
                        set_pos(inst,obj)
                        set_rot(inst,obj)
                        set_scale(inst,obj)
                    else:
                        obj=neg_cube
                        set_scale(inst_trans,obj)
            case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode'| 'worldTerrainProxyMeshNode': 
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for idx,inst in enumerate(instances):
                            obj_col=find_col(i,idx,Sector_coll)
                            #print(obj_col)
                            if obj_col:
                                if len(obj_col.objects)>0:
                                    obj=obj_col.objects[0]
                                    set_pos(inst,obj)
                                    set_rot(inst,obj)
                                    set_scale(inst,obj)
                                else:
                                    obj=neg_cube
                                    set_scale(inst,obj)
            case 'worldInstancedDestructibleMeshNode':
                #print('worldInstancedDestructibleMeshNode',i)
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    num=data['cookedInstanceTransforms']['numElements']
                    start=data['cookedInstanceTransforms']['startIndex']
                    instances = [x for x in t if x['NodeIndex'] == i]
                    for inst in instances:
                        for idx in range(start, start+num):
                            obj_col=find_col(i,idx,Sector_coll)
                            if obj_col:
                                if len(obj_col.objects)>0:
                                    obj=obj_col.objects[0]
                                    set_pos(inst,obj)
                                    set_rot(inst,obj)
                                    set_scale(inst,obj)
                                else:
                                    obj=neg_cube
                                    set_scale(inst,obj)

                                    
#       __   __          __      __  ___       ___  ___ 
#  /\  |  \ |  \ | |\ | / _`    /__`  |  |  | |__  |__  
# /~~\ |__/ |__/ | | \| \__>    .__/  |  \__/ |    |    
#                                                                                          
    ID=666
    for node in t:
        if node['Id']>ID:
            ID=node['Id']+1
    if Sector_additions_coll:
        for col in Sector_additions_coll.children:
            if 'nodeIndex' in col.keys() and col['sectorName']==sectorName and len(col.objects)>0:
                match col['nodeType']:
                    case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode' | 'worldTerrainProxyMeshNode':
                        obj=col.objects[0]
                        createNodeData(t, col, col['nodeIndex'], obj,ID)
                        ID+=1
                        
                    case 'worldInstancedMeshNode':
                        obj=col.objects[0]
                        nodeIndex=col['nodeIndex']
                        base=nodes[nodeIndex]['Data']
                        meshname = col['mesh']
                        #print(base)
                        num=base['worldTransformsBuffer']['numElements']
                        start=base['worldTransformsBuffer']['startIndex']
                        base['worldTransformsBuffer']['numElements']=num+1
                        print('start ',start,' num ',num)
                        #Need to build the transform to go in the sharedDataBuffer
                        trans= {"$type": "worldNodeTransform","rotation": {"$type": "Quaternion","i": 0.0, "j": 0.0,"k": 0.0, "r": 1.0 },
                          "translation": {"$type": "Vector3",  "X": 0.0,"Y": 0.0, "Z": 0.0 },'scale': {'$type': 'Vector3', 'X': 1.0, 'Y': 1.0, 'Z': 1.0} }
                        set_pos(trans,obj)
                        set_rot(trans,obj)
                        set_scale(trans,obj)
                        print(trans)
                        
                        if(meshname != 0):
                            idx =start+num
                            if 'Data' in base['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                #if the transforms are in the nodeData itself we can just add to the end of it
                                base['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'].append(trans)
                                           
                            elif 'HandleRefId' in base['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                # transforms are in a shared buffer in another nodeData need to insert then update all the references to the shared buffer
                                bufferID = int(base['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId'])
                                ref=base
                                for n in nodes:
                                    if n['HandleId']==str(bufferID-1):
                                        ref=n
                                wtbbuffer=ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']
                                print('Before = ',len(wtbbuffer['Transforms']))
                                print('inserting at ',idx)
                                wtbbuffer['Transforms'].insert(idx,trans)
                                print('After = ',len(wtbbuffer['Transforms']))
                                #Need to fix all the start pos for any instances after the node we're processing. What a ballache
                                for i,e in enumerate(nodes):
                                    data = e['Data']
                                    type = data['$type']
                                    if type=='worldInstancedMeshNode':
                                        wtb=data['worldTransformsBuffer']
                                        if 'HandleRefId' in wtb['sharedDataBuffer'].keys()==bufferID:
                                            if wtb['startIndex']>start:
                                                wtb['startIndex']=wtb['startIndex']+1

                        
                        
                        
                        
                        
                        
            elif 'nodeIndex' in col.keys() and col['sectorName'] in bpy.data.collections.keys() and len(col.objects)>0:
                match col['nodeType']:
                    case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode' | 'worldTerrainProxyMeshNode':
                        source_sector=col['sectorName']
                        print(source_sector)
                        source_sect_coll=bpy.data.collections.get(source_sector)
                        source_sect_json_path=source_sect_coll['filepath']
                        print(source_sect_json_path)
                        with open(source_sect_json_path,'r') as f: 
                            source_sect_json=json.load(f) 
                        source_nodes = source_sect_json["Data"]["RootChunk"]["nodes"]
                        print(len(source_nodes),col['nodeIndex'])
                        print(source_nodes[col['nodeIndex']])
                        nodes.append(copy.deepcopy(source_nodes[col['nodeIndex']]))
                        new_Index=len(nodes)-1
                        nodes[new_Index]['HandleId']=str(int(nodes[new_Index-1]['HandleId'])+1)
                        obj=col.objects[0]
                        createNodeData(t, col, new_Index, obj,ID)
                        ID+=1

    
    # Export the modified json

    pathout=os.path.join(outpath,os.path.basename(filepath))
    with open(pathout, 'w') as outfile:
        json.dump(j, outfile,indent=2)
    
        
