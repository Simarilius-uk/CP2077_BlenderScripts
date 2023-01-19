# Script to export CP2077 streaming sectors from Blender 
# Just does changes to existing bits so far
# By Simarilius Jan 2023
# latest version available at https://github.com/Simarilius-uk/CP2077_BlenderScripts

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
    print(inst)  
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


def set_bounds(node, obj):
        node["Bounds"]['Max']["X"]= float("{:.9g}".format(obj.location[0]*100))
        node["Bounds"]['Max']["Y"]= float("{:.9g}".format(obj.location[1]*100))
        node["Bounds"]['Max']["Z"]= float("{:.9g}".format(obj.location[2]*100))
        node["Bounds"]['Min']["X"]= float("{:.9g}".format(obj.location[0]*100))
        node["Bounds"]['Min']["Y"]= float("{:.9g}".format(obj.location[1]*100))
        node["Bounds"]['Min']["Z"]= float("{:.9g}".format(obj.location[2]*100))

def find_col(NodeIndex,Inst_idx,Sector_coll):
    print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.children if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        return inst[0]

def find_decal(NodeIndex,Inst_idx,Sector_coll):
    print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.objects if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return none
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        return inst[0]

def createNodeData(t, col, nodeIndex, obj):
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

for filepath in jsons:
    with open(filepath,'r') as f: 
          j=json.load(f) 
    nodes = j["Data"]["RootChunk"]["nodes"]
    t=j['Data']['RootChunk']['nodeData']['Data']
    sectorName=os.path.basename(filepath)[:-5]

    Sector_coll=bpy.data.collections.get(sectorName)
    Sector_coll['jsonpath']=filepath
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
                        obj_col=find_col(i,idx,Sector_coll)
                        obj=obj_col.objects[0]
                        if 'Data' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                            inst_trans=data['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                                   
                        elif 'HandleRefId' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                            bufferID = int(data['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId'])
                            ref=e
                            for n in nodes:
                                if n['HandleId']==str(bufferID-1):
                                    ref=n
                            inst_trans = ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                        set_pos(inst_trans,obj)
                        set_rot(inst_trans,obj)
                        set_scale(inst_trans,obj)
            case 'worldStaticDecalNode':
                print('worldStaticDecalNode')
                instances = [x for x in t if x['NodeIndex'] == i]
                for idx,inst in enumerate(instances):
                    obj=find_decal(i,idx,Sector_coll)
                    set_pos(inst,obj)
                    set_rot(inst,obj)
                    set_scale(inst,obj)
            case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode'| 'worldTerrainProxyMeshNode': 
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for idx,inst in enumerate(instances):
                            obj_col=find_col(i,idx,Sector_coll)
                            if obj_col:
                                obj=obj_col.objects[0]
                                set_pos(inst,obj)
                                set_rot(inst,obj)
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
                            obj=obj_col.objects[0]
                            set_pos(inst,obj)
                            set_rot(inst,obj)
                            set_scale(inst,obj)

    ID=666
    for node in t:
        if node['Id']>ID:
            ID=node['Id']+1
    if Sector_additions_coll:
        for col in Sector_additions_coll.children:
            if 'nodeIndex' in col.keys() and col['sectorName']==sectorName and len(col.objects)>0:
                match col['nodeType']:
                    case 'worldInstancedMeshNode'|'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode' | 'worldTerrainProxyMeshNode':
                        obj=col.objects[0]
                        createNodeData(t, col, col['nodeIndex'], obj)
                        ID+=1
            elif 'nodeIndex' in col.keys() and col['sectorName'] in bpy.data.collections.keys() and len(col.objects)>0:
                match col['nodeType']:
                    case 'worldInstancedMeshNode'|'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode' | 'worldTerrainProxyMeshNode':
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
                        createNodeData(t, col, new_Index, obj)

    


    pathout=os.path.join(outpath,os.path.basename(filepath))
    with open(pathout, 'w') as outfile:
        json.dump(j, outfile,indent=2)
    
        