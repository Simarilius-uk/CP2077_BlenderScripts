import json
import glob
import os
import bpy
from mathutils import Vector, Matrix
import time
start_time = time.time()
C = bpy.context
coll_scene = C.scene.collection
path = 'F:\\CPmod\\coyote\\source\\raw'

def get_pos(inst):
    pos=[0,0,0]
    if 'Properties' in inst['Position'].keys():
        pos[0] = inst['Position']['Properties']['X'] /100
        pos[1] = inst['Position']['Properties']['Y'] /100
        pos[2] = inst['Position']['Properties']['Z'] /100          
    else:
        pos[0] = inst['Position']['X'] /100
        pos[1] = inst['Position']['Y'] /100
        pos[2] = inst['Position']['Z'] /100
    return pos

def get_rot(inst):
    rot=[0,0,0,0]
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
    return rot

def get_scale(inst):
    scale=[0,0,0]
    if 'Properties' in inst['Scale'].keys():
        scale[0] = inst['Scale']['Properties']['X'] /100
        scale[1] = inst['Scale']['Properties']['Y'] /100
        scale[2] = inst['Scale']['Properties']['Z'] /100
    else:
        scale[0] = inst['Scale']['X'] /100
        scale[1] = inst['Scale']['Y'] /100
        scale[2] = inst['Scale']['Z'] /100
    return scale

if "MasterInstances" not in coll_scene.children.keys():
    Masters=bpy.data.collections.new("MasterInstances")
    coll_scene.children.link(Masters)
else:
    Masters=bpy.data.collections.get("MasterInstances")
    


jsonpath = glob.glob(path+"\**\*.streamingsector.json", recursive = True)

for filepath in jsonpath:    
    with open(filepath,'r') as f: 
          j=json.load(f) 
          
    t=j['Data']['RootChunk']['nodeData']['Data']
    sectorName=os.path.basename(filepath)[:-5]
    if sectorName in coll_scene.children.keys():
        Sector_coll=bpy.data.collections.get(sectorName)
    else:
        Sector_coll=bpy.data.collections.new(sectorName)
        coll_scene.children.link(Sector_coll)       
    
       
    meshes =  glob.glob(path+"\**\*.glb", recursive = True)
    
    glbnames = [ os.path.basename(x) for x in meshes]
    meshnames = [ os.path.splitext(x)[0]+".mesh" for x in glbnames]
    
    nodes = j["Data"]["RootChunk"]["nodes"]
    print(len(nodes))
    for i,e in enumerate(nodes):
    
        #if i > 2: break
        data = e['Data']
        type = data['$type']

        match type:
            case 'worldEntityNode': 
                print('worldEntityNode',i)
                app=e['Data']['appearanceName']
                entpath=os.path.join(path,e['Data']['entityTemplate']['DepotPath'])+'.json'
                ent_groupname=os.path.basename(entpath).split('.')[0]+'_'+app
                if ent_groupname in Masters.children.keys():
                    move_coll=Masters.children.get(ent_groupname)
                else:
                    try:
                        bpy.ops.io_scene_gltf.cp77entity(filepath=entpath, appearances=app)
                        objs = C.selected_objects
                        move_coll= coll_scene.children.get( os.path.basename(entpath).split('.')[0]+'_'+app )
                        Masters.children.link(move_coll) 
                        coll_scene.children.unlink(move_coll)
                    except:
                        print('failed on ',os.path.basename(entpath))
                instances = [x for x in t if x['NodeIndex'] == i]
                for inst in instances:
                    print(inst)
                    group=move_coll
                    groupname=move_coll.name
                    if (group):
                        print('Group found for ',groupname)     
                        new=bpy.data.collections.new(groupname)
                        Sector_coll.children.link(new)
                        new['nodeType']=type
                        new['nodeIndex']=i
                        new['debugName']=e['Data']['debugName']
                        new['sectorName']=sectorName 
                        new['HandleId']=e['HandleId']
                        new['entityTemplate']=os.path.basename(e['Data']['entityTemplate']['DepotPath'])
                        new['appearanceName']=e['Data']['appearanceName']
                        new['pivot']=inst['Pivot']
                        for old_obj in group.all_objects:                            
                            obj=old_obj.copy()  
                            new.objects.link(obj)  
                            curse=bpy.context.scene.cursor.location
                            with bpy.context.temp_override(selected_editable_objects=obj):
                                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                            
                            obj.location = get_pos(inst)
                            obj.rotation_quaternion = get_rot(inst)
                            obj.scale = get_scale(inst)
                            bpy.context.scene.cursor.location=curse 

 
            case 'worldInstancedMeshNode':
                #print('worldInstancedMeshNode')
                meshname = data['mesh']['DepotPath'] 
                num=data['worldTransformsBuffer']['numElements']
                start=data['worldTransformsBuffer']['startIndex']
                if(meshname != 0):
                                #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                                groupname = os.path.splitext(os.path.split(meshname)[-1])[0]
                                group=Masters.children.get(groupname)
                                if (group):
                                    print('Group found for ',groupname)                               
                                    for i in range(start, start+num):
                                        #create the linked copy of the group of mesh
                                        
                                        new=bpy.data.collections.new(groupname)
                                        Sector_coll.children.link(new)
                                        new['nodeType']=type
                                        new['nodeIndex']=i
                                        new['mesh']=meshname
                                        new['debugName']=e['Data']['debugName']
                                        new['sectorName']=sectorName 
                                        
                                        for old_obj in group.all_objects:                            
                                            obj=old_obj.copy()  
                                            new.objects.link(obj)                                    
                                            if 'Data' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                                inst_trans=data['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][i]
                                                       
                                            elif 'HandleRefId' in data['worldTransformsBuffer']['sharedDataBuffer'].keys():
                                                bufferID = int(data['worldTransformsBuffer']['sharedDataBuffer']['HandleRefId'])
                                                ref=e
                                                for n in nodes:
                                                    if n['HandleId']==str(bufferID-1):
                                                        ref=n
                                                inst_trans = ref['Data']['worldTransformsBuffer']['sharedDataBuffer']['Data']['buffer']['Data']['Transforms'][i]       
                                            else :
                                                print(e)
                                            obj.location.x = inst_trans['translation']['X'] /100
                                            obj.location.y = inst_trans['translation']['Y'] /100
                                            obj.location.z = inst_trans['translation']['Z'] /100
                                            if obj.location.x == 0:
                                                print('Mesh - ',meshname, ' - ',i,'HandleId - ', e['HandleId'])      
                                            
                                            #print(i,obj.name,' x= ',obj.location.x, ' y= ', obj.location.y, ' z= ',obj.location.z)
                                     
                                            obj.rotation_quaternion.x = inst_trans['rotation']['i']
                                            obj.rotation_quaternion.y = inst_trans['rotation']['j']
                                            obj.rotation_quaternion.z = inst_trans['rotation']['k']
                                            obj.rotation_quaternion.w = inst_trans['rotation']['r']
                                            
                                            obj.scale.x = inst_trans['scale']['X'] /100
                                            obj.scale.y = inst_trans['scale']['Y'] /100
                                            obj.scale.z = inst_trans['scale']['Z'] /100
                                                    
                                else:
                                    print('Mesh not found - ',meshname, ' - ',i, e['HandleId'])
                                                
            case 'XworldDecorationMeshNode': 
                #print('worldDecorationMeshNode',i)
                pass
            case 'XworldInstancedOccluderNode':
                #print('worldInstancedOccluderNode')
                pass
            case 'worldStaticDecalNode':
                print('worldStaticDecalNode')
                instances = [x for x in t if x['NodeIndex'] == i]
                for inst in instances:
                    print( inst)
                    o = bpy.data.objects.new( "empty", None )
                    o['nodeType']='worldStaticDecalNode'
                    o['nodeIndex']=i
                    o['decal']=e['Data']['material']['DepotPath']
                    o['debugName']=e['Data']['debugName']
                    o['sectorName']=sectorName
                    Sector_coll.objects.link(o)
                    o.location = get_pos(inst)
                    o.rotation_quaternion = get_rot(inst)
                    o.scale = get_scale(inst)
                    o.empty_display_size = 0.002
                    o.empty_display_type = 'IMAGE'   

            case 'XworldStaticOccluderMeshNode':
                #print('worldStaticOccluderMeshNode',i)
                pass
            case 'XworldCollisionNode':
                #print('worldCollisionNode',1)
                pass
            case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode': 
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                                #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                                groupname = os.path.splitext(os.path.split(meshname)[-1])[0]
                                group=Masters.children.get(groupname)
                                if (group):
                                    print('Group found for ',groupname) 
                                    instances = [x for x in t if x['NodeIndex'] == i]
                                    for inst in instances:
                                        new=bpy.data.collections.new(groupname)
                                        Sector_coll.children.link(new)
                                        new['nodeType']=type
                                        new['nodeIndex']=i
                                        new['mesh']=meshname
                                        new['debugName']=e['Data']['debugName']
                                        new['sectorName']=sectorName
                                        new['pivot']=inst['Pivot']
                                        
                                        for old_obj in group.all_objects:                            
                                            obj=old_obj.copy()  
                                            new.objects.link(obj)                             
                                            
                                            if 'Properties' in inst['Position'].keys():
                                                obj.location.x = inst['Position']['Properties']['X'] /100
                                                obj.location.y = inst['Position']['Properties']['Y'] /100
                                                obj.location.z = inst['Position']['Properties']['Z'] /100          
                                            else:
                                                obj.location.x = inst['Position']['X'] /100
                                                obj.location.y = inst['Position']['Y'] /100
                                                obj.location.z = inst['Position']['Z'] /100
                                            if obj.location.x == 0:
                                                print('Mesh - ',meshname, ' - ',i,'HandleId - ', e['HandleId'])      
                                            
                                           #print(i,obj.name,' x= ',obj.location.x, ' y= ', obj.location.y, ' z= ',obj.location.z)
                                            if 'Properties' in inst['Orientation'].keys():
                                                obj.rotation_quaternion.x = inst['Orientation']['Properties']['i']
                                                obj.rotation_quaternion.y = inst['Orientation']['Properties']['j']
                                                obj.rotation_quaternion.z = inst['Orientation']['Properties']['k']
                                                obj.rotation_quaternion.w = inst['Orientation']['Properties']['r']
                                            else:                                    
                                                obj.rotation_quaternion.x = inst['Orientation']['i']
                                                obj.rotation_quaternion.y = inst['Orientation']['j']
                                                obj.rotation_quaternion.z = inst['Orientation']['k']
                                                obj.rotation_quaternion.w = inst['Orientation']['r']
                                            if 'Properties' in inst['Scale'].keys():                       
                                                obj.scale.x = inst['Scale']['Properties']['X'] /100
                                                obj.scale.y = inst['Scale']['Properties']['Y'] /100
                                                obj.scale.z = inst['Scale']['Properties']['Z'] /100
                                            else:
                                                obj.scale.x = inst['Scale']['X'] /100
                                                obj.scale.y = inst['Scale']['Y'] /100
                                                obj.scale.z = inst['Scale']['Z'] /100
                                else:
                                    print('Mesh not found - ',meshname, ' - ',i, e['HandleId'])
                                  
            case 'worldInstancedDestructibleMeshNode':
                #print('worldInstancedDestructibleMeshNode',i)
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                                #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                                groupname = os.path.splitext(os.path.split(meshname)[-1])[0]
                                group=Masters.children.get(groupname)
                                if (group):
                                    #print('Glb found - ',glbfoundname)     
                                    #print('Glb found, looking for instances of ',i)
                                    instances = [x for x in t if x['NodeIndex'] == i]
                                    for inst in instances:
                                        #print('Inst - ',i, ' - ',meshname)
                                        
                                        new=bpy.data.collections.new(groupname)
                                        Sector_coll.children.link(new)
                                        new['nodeType']=type
                                        new['nodeIndex']=i
                                        new['mesh']=meshname
                                        new['debugName']=e['Data']['debugName']
                                        new['sectorName']=sectorName  
                                        new['pivot']=inst['Pivot']
                                        
                                        for old_obj in group.all_objects:                            
                                            obj=old_obj.copy()  
                                            new.objects.link(obj)   
                                            
                                            if 'Properties' in inst['Position'].keys():
                                                obj.location.x = inst['Position']['Properties']['X'] /100
                                                obj.location.y = inst['Position']['Properties']['Y'] /100
                                                obj.location.z = inst['Position']['Properties']['Z'] /100          
                                            else:
                                                obj.location.x = inst['Position']['X'] /100
                                                obj.location.y = inst['Position']['Y'] /100
                                                obj.location.z = inst['Position']['Z'] /100
                                            if obj.location.x == 0:
                                                print('Mesh - ',meshname, ' - ',i,'HandleId - ', e['HandleId'])      
                                            
                                           #print(i,obj.name,' x= ',obj.location.x, ' y= ', obj.location.y, ' z= ',obj.location.z)
                                            if 'Properties' in inst['Orientation'].keys():
                                                obj.rotation_quaternion.x = inst['Orientation']['Properties']['i']
                                                obj.rotation_quaternion.y = inst['Orientation']['Properties']['j']
                                                obj.rotation_quaternion.z = inst['Orientation']['Properties']['k']
                                                obj.rotation_quaternion.w = inst['Orientation']['Properties']['r']
                                            else:                                    
                                                obj.rotation_quaternion.x = inst['Orientation']['i']
                                                obj.rotation_quaternion.y = inst['Orientation']['j']
                                                obj.rotation_quaternion.z = inst['Orientation']['k']
                                                obj.rotation_quaternion.w = inst['Orientation']['r']
                                            if 'Properties' in inst['Scale'].keys():                       
                                                obj.scale.x = inst['Scale']['Properties']['X'] /100
                                                obj.scale.y = inst['Scale']['Properties']['Y'] /100
                                                obj.scale.z = inst['Scale']['Properties']['Z'] /100
                                            else:
                                                obj.scale.x = inst['Scale']['X'] /100
                                                obj.scale.y = inst['Scale']['Y'] /100
                                                obj.scale.z = inst['Scale']['Z'] /100
                                else:
                                    print('Mesh not found - ',meshname, ' - ',i, e['HandleId'])
            case 'worldRoadProxyMeshNode' : 
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                                #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                                #roads all have stupid prx0 names so instancing by name wont work.
                                try:
                                   bpy.ops.io_scene_gltf.cp77(filepath=meshname, with_materials=withMaterials)
                                   objs = C.selected_objects     
                                   groupname = objs[0].users_collection[0].name
                                   group= coll_scene.children.get( groupname )
                                   coll_target.children.link(group) 
                                   coll_scene.children.unlink(group)
                                   coll_target['glb_file']=meshname
                                except:
                                    print("Failed on ",meshname)
                                
                                if (group):
                                    print('Group found for ',groupname) 
                                    instances = [x for x in t if x['NodeIndex'] == i]
                                    for inst in instances:
                                        new=bpy.data.collections.new(groupname)
                                        Sector_coll.children.link(new)
                                        new['nodeType']=type
                                        new['nodeIndex']=i
                                        new['mesh']=meshname
                                        new['debugName']=e['Data']['debugName']
                                        new['sectorName']=sectorName
                                        new['pivot']=inst['Pivot']
                                        
                                        for old_obj in group.all_objects:                            
                                            obj=old_obj.copy()  
                                            new.objects.link(obj)                             

                                            obj.location = get_pos(inst)
                                            
                                            if obj.location.x == 0:
                                                print('Mesh - ',meshname, ' - ',i,'HandleId - ', e['HandleId'])      
                                            curse=bpy.context.scene.cursor.location
                                            bpy.context.scene.cursor.location=Vector((inst['Pivot']['X'] /100,inst['Pivot']['Y'] /100,inst['Pivot']['Z'] /100))
                                            with bpy.context.temp_override(selected_editable_objects=obj):
                                                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                                            
                                            #print(i,obj.name,' x= ',obj.location.x, ' y= ', obj.location.y, ' z= ',obj.location.z)
                                            obj.rotation_quaternion = get_rot(inst)
                                            obj.scale = get_scale(inst)
                                            bpy.context.scene.cursor.location=curse  
                                else:
                                    print('Mesh not found - ',meshname, ' - ',i, e['HandleId'])
                                             
                                            
            case _:
                print('None of the above',i)
                
                pass
    print('Finished with ',filepath)
print('Finished')
print("--- %s seconds ---" % (time.time() - start_time))