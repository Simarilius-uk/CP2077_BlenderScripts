# Script to export CP2077 streaming sectors from Blender 
# Just does changes to existing bits so far
# By Simarilius Jan 2023
# latest version available at https://github.com/Simarilius-uk/CP2077_BlenderScripts
#
#  __       __   ___  __   __  .  . .  . .   .       __   ___  __  ___  __   __      ___  __  . ___ . .  .  __  
# /  ` \ / |__) |__  |__) |__) |  | |\ | |__/       /__` |__  /  `  |  /  \ |__)    |__  |  \ |  |  | |\ | / _` 
# \__,  |  |__) |___ |  \ |    \__/ | \| |  \       .__/ |___ \__,  |  \__/ |  \    |___ |__/ |  |  | | \| \__/ 
#                                                                                                              
# Havent written a tutorial for this yet so thought I should add some instructions
# 1) Import the sector you want to edit using the Cyberpunk Blender Addon.
# 2) You can move the existing objects around and this will be exported
# 3) If you delete the mesh from a collector but leave the collector, the script will set the scale for that instance to -1 which stops it rendering in game
# 4) to add new stuff create a new collector with the sector name with _new on the end ie interior_1_1_0_1.streamingsector_new and then copy any objects you want into it.
#    You need to copy the collector and the meshes for the nodes you want to copy, not just the meshes, the tags that make it work are on the collectors.
# 5) If its stuff already in the sector it will create nodeData nodes to instance it, if its from another imported sector it will copy the main node too
#    Its assuming it can find the json for the sector its copying from in the project, dont be clever merging blends or whatever.
# 6) not all nodetypes are supported yet, have a look at the case statements to see which are
# 

import json
import glob
import os
import bpy
import copy
from mathutils import Vector, Matrix, Quaternion
C = bpy.context

#Set this to your project directory
project = 'F:\\CPmod\\corpo_apt'
path = os.path.join(project,'source\\raw\\base')

#its currently set to output the modified jsons to an output folder in the project dir (create one before running)
#you can change this to a path if you prefer
outpath = os.path.join(project,'output')

if not os.path.exists(outpath):
    os.makedirs(outpath)

def checkexists(meshname, Masters):
    groupname = os.path.splitext(os.path.split(meshname)[-1])[0]
    if groupname in Masters.children.keys() and len(Masters.children[groupname].objects)>0:
        return True
    else:
        return False

def get_pos(inst):
    pos=[0,0,0]
    if 'Position' in inst.keys():
        if 'Properties' in inst['Position'].keys():
            pos[0] = inst['Position']['Properties']['X'] /100
            pos[1] = inst['Position']['Properties']['Y'] /100
            pos[2] = inst['Position']['Properties']['Z'] /100          
        else:
            if 'X' in inst['Position'].keys():
                pos[0] = inst['Position']['X'] /100
                pos[1] = inst['Position']['Y'] /100
                pos[2] = inst['Position']['Z'] /100
            else:
                pos[0] = inst['Position']['x'] /100
                pos[1] = inst['Position']['y'] /100
                pos[2] = inst['Position']['z'] /100
    elif 'position' in inst.keys():
        if 'X' in inst['position'].keys():
                pos[0] = inst['position']['X'] /100
                pos[1] = inst['position']['Y'] /100
                pos[2] = inst['position']['Z'] /100
    elif 'translation' in inst.keys():
        pos[0] = inst['translation']['X'] /100
        pos[1] = inst['translation']['Y'] /100
        pos[2] = inst['translation']['Z'] /100
    return pos

def get_rot(inst):
    rot=[0,0,0,0]
    if 'Orientation' in inst.keys():
        if 'Properties' in inst['Orientation'].keys():
            rot[0] = inst['Orientation']['Properties']['r']  
            rot[1] = inst['Orientation']['Properties']['i'] 
            rot[2] = inst['Orientation']['Properties']['j'] 
            rot[3] = inst['Orientation']['Properties']['k']            
        else:
            rot[0] = inst['Orientation']['r'] 
            rot[1] = inst['Orientation']['i'] 
            rot[2] = inst['Orientation']['j'] 
            rot[3] = inst['Orientation']['k'] 
    elif 'orientation' in inst.keys():
            rot[0] = inst['orientation']['r'] 
            rot[1] = inst['orientation']['i'] 
            rot[2] = inst['orientation']['j'] 
            rot[3] = inst['orientation']['k'] 
    elif 'Rotation' in inst.keys():
            rot[0] = inst['Rotation']['r'] 
            rot[1] = inst['Rotation']['i'] 
            rot[2] = inst['Rotation']['j'] 
            rot[3] = inst['Rotation']['k'] 
    elif 'rotation' in inst.keys():
            rot[0] = inst['rotation']['r'] 
            rot[1] = inst['rotation']['i'] 
            rot[2] = inst['rotation']['j'] 
            rot[3] = inst['rotation']['k'] 
    return rot

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

def set_z_pos(inst,obj):  
    #print(inst)  
    if 'Position'in inst.keys():
        if 'Properties' in inst['Position'].keys():
            inst['Position']['Properties']['Z'] = float("{:.9g}".format(obj.location[2]*100))
        else:
            if 'X' in inst['Position'].keys():
                inst['Position']['Z'] = float("{:.9g}".format(obj.location[2]*100))
            else:
                inst['Position']['z'] = float("{:.9g}".format(obj.location[2]*100))
    elif 'position' in inst.keys():
        inst['position']['Z'] = float("{:.9g}".format(obj.location[2]*100))
    elif 'translation' in inst.keys():
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
    elif 'orientation' in inst.keys():
            inst['orientation']['r'] = float("{:.9g}".format(obj.rotation_quaternion[0] ))
            inst['orientation']['i'] = float("{:.9g}".format(obj.rotation_quaternion[1] )) 
            inst['orientation']['j'] = float("{:.9g}".format(obj.rotation_quaternion[2] ))
            inst['orientation']['k'] = float("{:.9g}".format(obj.rotation_quaternion[3] ))

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
        if len(inst)>0:
            return inst[0]
    return None

def find_wIDMN_col(NodeIndex,tl_inst_idx, sub_inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.children if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['tl_instance_idx']==tl_inst_idx and x['sub_instance_idx']==sub_inst_idx]
        if len(inst)>0:
            return inst[0]
    return None

def find_decal(NodeIndex,Inst_idx,Sector_coll):
    #print('Looking for NodeIndex ',NodeIndex,' Inst_idx ',Inst_idx, ' in ',Sector_coll)
    col=[x for x in Sector_coll.objects if x['nodeIndex']==NodeIndex]
    if len(col)==0:
        return None
    elif len(col)==1:
        return col[0]
    else: 
        inst=[x for x in col if x['instance_idx']==Inst_idx]
        if len(inst)>0:
            return inst[0]
    return None

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

Masters=bpy.data.collections.get("MasterInstances")

neg_cube=None
if 'neg_cube' not in Masters.objects.keys():
    bpy.ops.mesh.primitive_cube_add(size=.01, scale=(-1,-1,-1),location=(0,0,-10))
    neg_cube=C.selected_objects[0]
    neg_cube.name='neg_cube'
    neg_cube.users_collection[0].objects.unlink(neg_cube)
    Masters.objects.link(neg_cube) 
else:
    neg_cube=Masters.objects["neg_cube"]

 # .  .  __ .    .. .  .  __      __  ___ .  .  ___  ___ 
 # |\/| /  \ \  / | |\ | / _`    /__`  |  |  | |__  |__  
 # |  | \__/  \/  | | \| \__/    .__/  |  \__/ |    |    
 #
                                                      
for filepath in jsons:
    with open(filepath,'r') as f: 
        j=json.load(f) 
    nodes = j["Data"]["RootChunk"]["nodes"]
    t=j['Data']['RootChunk']['nodeData']['Data']
    sectorName=os.path.basename(filepath)[:-5]
    if sectorName not in bpy.data.collections.keys():
        break
    print('Updating sector ',sectorName)
    Sector_coll=bpy.data.collections.get(sectorName)
    if 'filepath' not in Sector_coll.keys():
        Sector_coll['filepath']=filepath
    #print(filepath)
    #print(len(nodes))
    Sector_additions_coll=bpy.data.collections.get(sectorName+'_new')
    wIMNs=0
    for i,e in enumerate(nodes):
        data = e['Data']
        type = data['$type']
        match type:
            case 'worldInstancedMeshNode' :
                wIMNs+=1
                #print(wIMNs)
                meshname = data['mesh']['DepotPath'] 
                #if 'chopstick' in meshname:
                #    print('worldInstancedMeshNode - ',meshname)
                if not checkexists(meshname, Masters):
                    print(meshname, ' not found in masters')
                    continue
                
                num=data['worldTransformsBuffer']['numElements']
                start=data['worldTransformsBuffer']['startIndex']
                if(meshname != 0):
                    for idx in range(start, start+num):
                        bufferID=0
                        if 'Data' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                inst_trans=data['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                                       
                        elif 'HandleRefId' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                            bufferID = int(data['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId'])
                            ref=e
                            for n in nodes:
                                if n['HandleId']==str(bufferID-1):
                                    ref=n
                            inst_trans = ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]
                    # store the bufferID for when we add new stuff.
                        if Sector_additions_coll:
                            Sector_additions_coll['Inst_bufferID']=bufferID
                        obj_col=find_col(i,idx,Sector_coll)    
                        if obj_col and inst_trans:
                            if len(obj_col.objects)>0:
                                obj=obj_col.objects[0]
                                set_pos(inst_trans,obj)
                                set_rot(inst_trans,obj)
                                set_scale(inst_trans,obj)
                            else:
                                obj=neg_cube
                                set_z_pos(inst_trans,obj)
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
                        set_z_pos(inst,obj)
            case   'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode'| 'worldTerrainProxyMeshNode': 
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
                                    set_z_pos(inst,obj)
            case  'worldEntityNode':
                if isinstance(e, dict) and 'entityTemplate' in data.keys():
                    entname = data['entityTemplate']['DepotPath']
                    
                    if(entname != 0):
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for idx,inst in enumerate(instances):
                            obj_col=find_col(i,idx,Sector_coll)
                            #print(obj_col)
                            if obj_col:
                                if len(obj_col.objects)>0:
                                    mat=Matrix(obj_col['matrix'])
                                    mat_inv=mat.inverted()
                                    obj=obj_col.objects[0]
                                    inst_trans_m = obj.matrix_world @ mat_inv
                                    obj_trans = obj.location
                                    pos=inst_trans_m.translation
                                    #pos=obj_trans-basic_pos
                                    inst['Position']['X'] = float("{:.9g}".format(pos[0]*100))
                                    inst['Position']['Y'] = float("{:.9g}".format(pos[1]*100))
                                    inst['Position']['Z'] = float("{:.9g}".format(pos[2]*100))
                                    quat=inst_trans_m.to_quaternion()
                                    inst['Orientation']['r'] = float("{:.9g}".format(quat[0] ))
                                    inst['Orientation']['i'] = float("{:.9g}".format(quat[1] ))
                                    inst['Orientation']['j'] = float("{:.9g}".format(quat[2] ))
                                    inst['Orientation']['k'] = float("{:.9g}".format(quat[3] ))
                                    scale=inst_trans_m.to_scale()
                                    inst['Scale']['X']=float("{:.9g}".format(scale.x*100))
                                    inst['Scale']['Y']=float("{:.9g}".format(scale.y*100))
                                    inst['Scale']['Z']=float("{:.9g}".format(scale.z*100))
                                    #set_pos(inst,obj)
                                    #set_rot(inst,obj)
                                    #set_scale(inst,obj)
                                else:
                                    obj=neg_cube
                                    set_z_pos(inst,obj)                                    
                                    
                                    
                                    
            case 'worldInstancedDestructibleMeshNode':
                #print('worldInstancedDestructibleMeshNode',i)
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    num=data['cookedInstanceTransforms']['numElements']
                    start=data['cookedInstanceTransforms']['startIndex']
                    instances = [x for x in t if x['NodeIndex'] == i]
                    for tlidx,inst in enumerate(instances):
                        for idx in range(start, start+num):
                            bufferID=0
                            basic_trans=None
                            # Transforms are inside the cookedInstanceTransforms in a buffer
                            if 'Data' in data['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                                basic_trans=data['cookedInstanceTransforms']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]

                            # Transforms are in a shared buffer in another node, so get the reference and find the transform data                    
                            elif 'HandleRefId' in data['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                                bufferID = int(data['cookedInstanceTransforms']['sharedDataBuffer']['HandleRefId'])
                                ref=e
                                for n in nodes:
                                    if n['HandleId']==str(bufferID-1):
                                        ref=n
                                basic_trans = ref['Data']['cookedInstanceTransforms']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][idx]   
                                #print(basic_trans)                  
                            else :
                                print(e)
                            # store the bufferID for when we add new stuff.
                            if Sector_additions_coll:
                                Sector_additions_coll['Dest_bufferID']=bufferID
                                #print('Setting Dest_bufferID to ',bufferID)
                            
                            # the Transforms are stored as 2 parts, a basic transform applied to all the instances and individual ones per instance
                            # lets get the basic one so we can calculate the instance one.
                            basic_pos =Vector(get_pos(basic_trans))
                            basic_rot =Quaternion(get_rot(basic_trans))
                            basic_scale =Vector((1,1,1))
                            basic_matr=Matrix.LocRotScale(basic_pos,basic_rot,basic_scale)
                            basic_matr_inv=basic_matr.inverted()
                            
                            # Never modify the basic on as other nodes may be referencing it. (its normally 0,0,0 anyway)
                            inst_pos =Vector(get_pos(inst))
                            inst_rot =Quaternion(get_rot(inst))
                            inst_scale =Vector((1,1,1))
                            inst_m=Matrix.LocRotScale(inst_pos,inst_rot,inst_scale)
                            

                            obj_col=find_wIDMN_col(i,tlidx,idx,Sector_coll)
                            if obj_col:
                                if len(obj_col.objects)>0:
                                    obj=obj_col.objects[0]
                                    
                                    inst_trans_m = obj.matrix_world @ basic_matr_inv
                                    obj_trans = obj.location
                                    pos=inst_trans_m.translation
                                    print(obj_trans, inst_pos)
                                    deltapos=sum(obj_trans-inst_pos)
                                    if abs(deltapos)>0.05:
                                        print('deltapos ',abs(deltapos))
                                        inst['Position']['X'] = float("{:.9g}".format(pos[0]*100))
                                        inst['Position']['Y'] = float("{:.9g}".format(pos[1]*100))
                                        inst['Position']['Z'] = float("{:.9g}".format(pos[2]*100))
                                        quat=inst_trans_m.to_quaternion()
                                        inst['Orientation']['i'] = float("{:.12g}".format(quat[0] ))
                                        inst['Orientation']['j'] = float("{:.12g}".format(quat[1] ))
                                        inst['Orientation']['k'] = float("{:.12g}".format(quat[2] ))
                                        inst['Orientation']['r'] = float("{:.12g}".format(quat[3] ))
                                        scale=inst_trans_m.to_scale()
                                        inst['Scale']['X']=float("{:.9g}".format(scale.x*100))
                                        inst['Scale']['Y']=float("{:.9g}".format(scale.y*100))
                                        inst['Scale']['Z']=float("{:.9g}".format(scale.z*100))
                                else:
                                    inst['Position']['Z']=-300
    print(wIMNs)
                                    
#       __   __          __      __  ___       ___  ___ 
#  /\  |  \ |  \ | |\ | / _`    /__`  |  |  | |__  |__  
# /~~\ |__/ |__/ | | \| \__>    .__/  |  \__/ |    |    
#                       
    instances_to_copy=[]                                                               
    destructibles_to_copy=[]
    ID=666
    for node in t:
        if node['Id']>ID:
            ID=node['Id']+1
    if Sector_additions_coll:
        for col in Sector_additions_coll.children:
            if 'nodeIndex' in col.keys() and col['sectorName']==sectorName and len(col.objects)>0:
                match col['nodeType']:
                    case 'worldStaticMeshNode' | 'worldStaticDecalNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode' | 'worldTerrainProxyMeshNode':
                        obj=col.objects[0]
                        createNodeData(t, col, col['nodeIndex'], obj,ID)
                        ID+=1
                    case 'worldEntityNode':
                        new_ni=len(nodes)
                        nodes.append(copy.deepcopy(nodes[col['nodeIndex']]))
                        obj=col.objects[0]
                        createNodeData(t, col, new_ni, obj,ID)
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
                                #if the transforms are in the nodeData itself we can just add to the end of it - WRONG. it may be the shared one everything else is pointing to.
                                base['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']
                                bufferID = nodeIndex
                                           
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

                    case 'worldInstancedDestructibleMeshNode':
                        obj=col.objects[0]
                        nodeIndex=col['nodeIndex']
                        base=nodes[nodeIndex]['Data']
                        meshname = col['mesh']
                        #print(base)
                        num=base['cookedInstanceTransforms']['numElements']
                        start=base['cookedInstanceTransforms']['startIndex']
                        base['cookedInstanceTransforms']['numElements']=num+1
                        print('start ',start,' num ',num)
                        #Need to build the transform to go in the sharedDataBuffer
                        trans= {"$type": "Transform","orientation": {"$type": "Quaternion","i": 0.0, "j": 0.0,"k": 0.0, "r": 1.0 },
                          "position": {"$type": "Vector4","W": 0,  "X": 0.0,"Y": 0.0, "Z": 0.0 }}
                        
                        
                        instances = [x for x in t if x['NodeIndex'] == nodeIndex]
                        inst=instances[0]
                        
                        inst_pos =Vector(get_pos(inst))
                        inst_rot =Quaternion(get_rot(inst))
                        inst_scale =Vector((1,1,1))
                        inst_m=Matrix.LocRotScale(inst_pos,inst_rot,inst_scale)
                        inst_m_inv=inst_m.inverted()
                        inst_trans_m = inst_m_inv @ obj.matrix_local 
                        pos=inst_trans_m.translation
                        trans['position']['X']=pos[0]*100
                        trans['position']['Y']=pos[1]*100
                        trans['position']['Z']=pos[2]*100
                        quat=inst_trans_m.to_quaternion()
                        trans['orientation']['r']=-quat[0]
                        trans['orientation']['i']=-quat[1]
                        trans['orientation']['j']=-quat[2]
                        trans['orientation']['k']=-quat[3]
                        print(trans)
                        
                        if(meshname != 0):
                            idx =start+num
                            if 'Data' in base['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                                #if the transforms are in the nodeData itself we can just add to the end of it - WRONG
                                wtbbuffer=base['cookedInstanceTransforms']['sharedDataBuffer']['Data']['buffer']['Data']
                                bufferID = nodeIndex
                                           
                            elif 'HandleRefId' in base['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                                # transforms are in a shared buffer in another nodeData need to insert then update all the references to the shared buffer
                                bufferID = int(base['cookedInstanceTransforms']['sharedDataBuffer']['HandleRefId'])
                                ref=base
                                for n in nodes:
                                    if n['HandleId']==str(bufferID-1):
                                        ref=n
                                wtbbuffer=ref['Data']['cookedInstanceTransforms']['sharedDataBuffer']['Data']['buffer']['Data']
                            print('Before = ',len(wtbbuffer['Transforms']))
                            print('inserting at ',idx)
                            wtbbuffer['Transforms'].insert(idx,trans)
                            print('After = ',len(wtbbuffer['Transforms']))
                            #Need to fix all the start pos for any instances after the node we're processing. What a ballache
                            for i,e in enumerate(nodes):
                                data = e['Data']
                                type = data['$type']
                                if type=='worldInstancedDestructibleMeshNode':
                                    citb=data['cookedInstanceTransforms']
                                    if 'HandleRefId' in citb['sharedDataBuffer'].keys()==bufferID:
                                        if citb['startIndex']>start:
                                            citb['startIndex']=citb['startIndex']+1

#            
#     ___       __    ___ __  _                     ____                              __  __                 _____           __                 
#    /   | ____/ /___/ (_) /_(_)___  ____  _____   / __/________  ____ ___     ____  / /_/ /_  ___  _____   / ___/___  _____/ /_____  __________
#   / /| |/ __  / __  / / __/ / __ \/ __ \/ ___/  / /_/ ___/ __ \/ __ `__ \   / __ \/ __/ __ \/ _ \/ ___/   \__ \/ _ \/ ___/ __/ __ \/ ___/ ___/
#  / ___ / /_/ / /_/ / / /_/ / /_/ / / / (__  )  / __/ /  / /_/ / / / / / /  / /_/ / /_/ / / /  __/ /      ___/ /  __/ /__/ /_/ /_/ / /  (__  ) 
# /_/  |_\__,_/\__,_/_/\__/_/\____/_/ /_/____/  /_/ /_/   \____/_/ /_/ /_/   \____/\__/_/ /_/\___/_/      /____/\___/\___/\__/\____/_/  /____/  
#                                                                                                                                              
#  Nodes from other sectors that have been imported           
                        
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
                    
                    # make a list of all the instances, we'll copy the main node once and instance them
                    case 'worldInstancedMeshNode':
                        if [col['nodeIndex'],col['sectorName']] not in instances_to_copy:
                            instances_to_copy.append([col['nodeIndex'],col['sectorName']])
                    
                    case 'worldInstancedDestructibleMeshNode':
                        if [col['nodeIndex'],col['sectorName']] not in destructibles_to_copy:
                            destructibles_to_copy.append([col['nodeIndex'],col['sectorName']])
    
    print(instances_to_copy)
    print(destructibles_to_copy)

    for node in instances_to_copy:
        ni=node[0]
        source_sector=node[1]
        source_sect_coll=bpy.data.collections.get(source_sector)
        source_sect_json_path=source_sect_coll['filepath']
        print(source_sect_json_path)
        with open(source_sect_json_path,'r') as f: 
            source_sect_json=json.load(f) 
        source_nodes = source_sect_json["Data"]["RootChunk"]["nodes"]
        nodes.append(copy.deepcopy(source_nodes[ni]))
        new_Index=len(nodes)-1
        new_node=nodes[new_Index]
        prev_node=nodes[new_Index-1]
        if 'cookedInstanceTransforms' in prev_node.keys() or 'worldTransformsBuffer' in prev_node.keys():
            if 'cookedInstanceTransforms' in prev_node.keys() and 'HandleId' in prev_node['cookedInstanceTransforms']:
                new_node['HandleId']=str(int(nodes[new_Index-1]['cookedInstanceTransforms']['HandleId'])+1)
            if 'worldTransformsBuffer' in prev_node.keys() and 'HandleId' in prev_node['worldTransformsBuffer']:
                new_node['HandleId']=str(int(nodes[new_Index-1]['worldTransformsBuffer']['HandleId'])+1)
        else:
            new_node['HandleId']=str(int(nodes[new_Index-1]['HandleId'])+1)
        print("New Node: ")
        print(new_node)
        #need the new nodeData node pointing to it.
        instances = [x for x in source_sect_json['Data']['RootChunk']['nodeData']['Data'] if x['NodeIndex'] == ni]
        inst=instances[0]
        t.append(copy.deepcopy(inst))
        new_nd_node=t[len(t)-1]
        new_nd_node['NodeIndex']=new_Index
        print("New nodeData Node: ")
        print(new_nd_node)
        bufferID=0
        new_node['Data']['worldTransformsBuffer']['numElements']=0
        # Hopefully we can add the instances to the end of the buffer we saved earlier.
        print("Sector_additions_coll['Inst_bufferID'] = ",Sector_additions_coll['Inst_bufferID'])
        if Sector_additions_coll['Inst_bufferID']>0:
            new_node['Data']['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId']=str(Sector_additions_coll['Inst_bufferID'])
            bufferID = Sector_additions_coll['Inst_bufferID']
            if 'Data' in new_node['Data']['worldTransformsBuffer']['sharedDataBuffer'].keys():
                new_node['Data']['worldTransformsBuffer']['sharedDataBuffer'].pop('Data')
        else:
            # the sector has no other instanced meshes already in it, so no wtb to point to. Need to create one in the wtb data
            # have absolutely no idea what the flags is here.
            newbuf={ "BufferId": str(new_Index+1), "Flags": 4063232,"Type": "WolvenKit.RED4.Archive.Buffer.WorldTransformsBuffer, WolvenKit.RED4.Archive, Version=1.61.0.0, Culture=neutral, PublicKeyToken=null", "Data": { "Transforms": []} } 
            new_node['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']={ "Data": {"$type": "worldSharedDataBuffer", "buffer": newbuf}}

            bufferID = new_node['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['Data']['BufferID']
            Sector_additions_coll['Inst_bufferID']=bufferID
        
        print('bufferID - ',bufferID)
        ref=new_nd_node
        for n in nodes:
            if n['HandleId']==str(bufferID-1):
                ref=n
        wtbbuffer=ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']
        new_node['Data']['worldTransformsBuffer']['startIndex']=len(wtbbuffer['Transforms'])

        new_node['HandleId']=str(int(nodes[new_Index-1]['HandleId'])+1)
        inst_col=[]
        for col in Sector_additions_coll.children:
            if col['nodeIndex']==ni and col['sectorName']==source_sector:
                inst_col.append(col.name)
        for colname in inst_col:
            col=Sector_additions_coll.children.get(colname)
            obj=col.objects[0]
            new_node['Data']['worldTransformsBuffer']['numElements']+=1
            trans= {"$type": "worldNodeTransform","rotation": {"$type": "Quaternion","i": 0.0, "j": 0.0,"k": 0.0, "r": 1.0 },
                          "translation": {"$type": "Vector3",  "X": 0.0,"Y": 0.0, "Z": 0.0 },'scale': {'$type': 'Vector3', 'X': 1.0, 'Y': 1.0, 'Z': 1.0} }
            set_pos(trans,obj)
            set_rot(trans,obj)
            set_scale(trans,obj)
            idx=len(wtbbuffer['Transforms'])
            print(trans)
            print('Before = ',len(wtbbuffer['Transforms']))
            print('inserting at ',idx)
            wtbbuffer['Transforms'].insert(idx,trans)
            print('After = ',len(wtbbuffer['Transforms']))
            
    for node in destructibles_to_copy:
        ni=node[0]
        source_sector=node[1]
        source_sect_coll=bpy.data.collections.get(source_sector)
        source_sect_json_path=source_sect_coll['filepath']
        print(source_sect_json_path)
        with open(source_sect_json_path,'r') as f: 
            source_sect_json=json.load(f) 
        source_nodes = source_sect_json["Data"]["RootChunk"]["nodes"]
        nodes.append(copy.deepcopy(source_nodes[ni]))
        new_Index=len(nodes)-1
        new_node=nodes[new_Index]
        prev_node=nodes[new_Index-1]
        if 'cookedInstanceTransforms' in prev_node.keys() or 'worldTransformsBuffer' in prev_node.keys():
            if 'cookedInstanceTransforms' in prev_node.keys() and 'HandleId' in prev_node['cookedInstanceTransforms']:
                new_node['HandleId']=str(int(nodes[new_Index-1]['cookedInstanceTransforms']['HandleId'])+1)
            if 'worldTransformsBuffer' in prev_node.keys() and 'HandleId' in prev_node['worldTransformsBuffer']:
                new_node['HandleId']=str(int(nodes[new_Index-1]['worldTransformsBuffer']['HandleId'])+1)
        else:
            new_node['HandleId']=str(int(nodes[new_Index-1]['HandleId'])+1)
        print("New Node: ")
        print(new_node)
        #need the new nodeData node pointing to it.
        instances = [x for x in source_sect_json['Data']['RootChunk']['nodeData']['Data'] if x['NodeIndex'] == ni]
        inst=instances[0]
        t.append(copy.deepcopy(inst))
        new_nd_node=t[len(t)-1]
        new_nd_node['NodeIndex']=new_Index
        new_nd_node['Position']['X']=0
        new_nd_node['Position']['Y']=0
        new_nd_node['Position']['Z']=0
        new_nd_node['Orientation']['r']=0
        new_nd_node['Orientation']['i']=0
        new_nd_node['Orientation']['j']=0
        new_nd_node['Orientation']['k']=0
        new_nd_node['Scale']['X']=1
        new_nd_node['Scale']['Y']=1
        new_nd_node['Scale']['Z']=1
        
        maxHid=new_node['HandleId']
        print("New nodeData Node: ")
        print(new_nd_node)
        bufferID=-99
        new_node['Data']['cookedInstanceTransforms']['numElements']=0
        # Hopefully we can add the instances to the end of the buffer we saved earlier.
        #print("Sector_additions_coll['Dest_bufferID'] = ",Sector_additions_coll['Dest_bufferID'])
        if 'Dest_bufferID' in Sector_additions_coll.keys() and int(Sector_additions_coll['Dest_bufferID'])>-1:
            
            print('  Found a shared buffer ',Sector_additions_coll['Dest_bufferID'])
            new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer']['HandleRefId']=str(Sector_additions_coll['Dest_bufferID'])
            bufferID = Sector_additions_coll['Dest_bufferID']
            if 'Data' in new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer'].pop('Data')
            if 'HandleId' in new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer'].keys():
                new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer'].pop('HandleId')
        else:
            # the sector has no other instanced meshes already in it, so no wtb to point to. Need to create one in the wtb data
            # have absolutely no idea what the flags is here.
            print('No shared buffer found.')
            newbuf={ "BufferId": str(new_Index+1), "Flags": 4063232,"Type": "WolvenKit.RED4.Archive.Buffer.WorldTransformsBuffer, WolvenKit.RED4.Archive, Version=1.61.0.0, Culture=neutral, PublicKeyToken=null", "Data": { "Transforms": []} } 
            new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer']['Data']= { "Data": {"$type": "worldSharedDataBuffer", "buffer": newbuf}}
            print(new_node)
            new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer']['HandleId']=maxHid+1
            maxHid+=1
            new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer'].pop('HandleRefId')
            bufferID = new_node['Data']['cookedInstanceTransforms']['sharedDataBuffer']['HandleId']
            print(new_node['Data']['cookedInstanceTransforms'])
            Sector_additions_coll['Dest_bufferID']=bufferID
        
        print('bufferID - ',bufferID)
        ref=new_node
        for n in nodes:
            if int(n['HandleId'])==int(bufferID)-1:
                ref=n
        print(ref['Data']['cookedInstanceTransforms']['sharedDataBuffer'])
        wtbbuffer=ref['Data']['cookedInstanceTransforms']['sharedDataBuffer']['Data']['buffer']['Data']
        new_node['Data']['cookedInstanceTransforms']['startIndex']=len(wtbbuffer['Transforms'])
        if 'HandleId' in new_node['Data']['filterData'].keys():
                new_node['Data']['filterData']['HandleId']=str(int(maxHid)+1)
        
        inst_col=[]
        for col in Sector_additions_coll.children:
            if col['nodeIndex']==ni and col['sectorName']==source_sector:
                inst_col.append(col.name)
        for colname in inst_col:
            col=Sector_additions_coll.children.get(colname)
            obj=col.objects[0]
            new_node['Data']['cookedInstanceTransforms']['numElements']+=1
            trans= {"$type": "Transform","orientation": {"$type": "Quaternion","i": 0.0, "j": 0.0,"k": 0.0, "r": 1.0 },
                          "position": {"$type": "Vector4","W": 0,  "X": 0.0,"Y": 0.0, "Z": 0.0 }}
            set_pos(trans,obj)
            set_rot(trans,obj)
            set_scale(trans,obj)
            idx=len(wtbbuffer['Transforms'])
            print(trans)
            print('Before = ',len(wtbbuffer['Transforms']))
            print('inserting at ',idx)
            wtbbuffer['Transforms'].insert(idx,trans)
            print('After = ',len(wtbbuffer['Transforms']))            
          
            
    # Export the modified json
    pathout=os.path.join(outpath,os.path.basename(filepath))
    with open(pathout, 'w') as outfile:
        json.dump(j, outfile,indent=2)
    
        
