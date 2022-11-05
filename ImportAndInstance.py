# Script to import CP2077 streaming sectors to Blender 
# Can be used with or without materials, just set the withMaterials to True or False accordingly
# see https://wiki.redmodding.org/wolvenkit/guides/modding-community/exporting-streaming-sectors-to-blender
# By Simarilius Nov 2022
# latest version available at https://github.com/Simarilius-uk/CP2077_BlenderScripts

import json
import glob
import os
import bpy
from mathutils import Vector, Matrix
C = bpy.context

# Enter the path to your projects source\raw\base folder below, needs double slashes between folder names.

path = 'F:\\CPmod\\nomad_garage\\source\\raw\\base'

withMaterials=False

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    Thanks Greenstick:    
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

coll_scene = C.scene.collection
Masters=bpy.data.collections.new("MasterInstances")
coll_scene.children.link(Masters)

# Set target collection to a known collection 
coll_target = coll_scene.children.get("MasterInstances")


meshes =  glob.glob(path+"\**\*.glb", recursive = True)
glbnames = [ os.path.basename(x) for x in meshes]
meshnames = [ os.path.splitext(x)[0]+".mesh" for x in glbnames]

total=len(meshes)
print(total)
i=0
printProgressBar(i, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
for mesh in meshes:
    try:
       bpy.ops.io_scene_gltf.cp77(filepath=mesh, with_materials=withMaterials)
       objs = C.selected_objects       
       move_coll= coll_scene.children.get( objs[0].users_collection[0].name )
       coll_target.children.link(move_coll) 
       coll_scene.children.unlink(move_coll)
       coll_target['glb_file']=mesh
    except:
        print("Failed on ",mesh)
    i=i+1
    printProgressBar(i, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    

jsonpath = glob.glob(path+"\**\*.streamingsector.json", recursive = True)

for filepath in jsonpath:    
    with open(filepath,'r') as f: 
          j=json.load(f) 
    sectorName=os.path.basename(filepath)[:-5]
    Sector_coll=bpy.data.collections.new(sectorName)
    coll_scene.children.link(Sector_coll)
    
    t=j['Data']['RootChunk']['nodeData']['Data']

    nodes = j["Data"]["RootChunk"]["nodes"]
    print(len(nodes))
    for i,e in enumerate(nodes):

        #if i > 2: break
        data = e['Data']
        type = data['$type']
        
        match type:
            case 'worldEntityNode': 
                print('worldEntityNode',i)
                instances = [x for x in t if x['NodeIndex'] == i]
                for inst in instances:
                    print( inst)
                    o = bpy.data.objects.new( "empty", None )
                    o['nodeType']='worldEntityNode'
                    o['HandleId']=e['HandleId']
                    o['sectorName']=sectorName
                    o['entityTemplate']=os.path.basename(e['Data']['entityTemplate']['DepotPath'])
                    o['appearanceName']=e['Data']['appearanceName']
                    o['pivot']=inst['Pivot']

                    # due to the new mechanism of "collection"
#                    bpy.context.scene.collection.objects.link( o )
                    Sector_coll.objects.link(o)
                    curse=bpy.context.scene.cursor.location
                    bpy.context.scene.cursor.location=Vector((inst['Pivot']['X'] /100,inst['Pivot']['Y'] /100,inst['Pivot']['Z'] /100))
                    with bpy.context.temp_override(selected_editable_objects=o):
                        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                    
                    o.location.x = inst['Position']['X'] /100
                    o.location.y = inst['Position']['Y'] /100
                    o.location.z = inst['Position']['Z'] /100
                    o.rotation_quaternion.x = inst['Orientation']['i']
                    o.rotation_quaternion.y = inst['Orientation']['j']
                    o.rotation_quaternion.z = inst['Orientation']['k']
                    o.rotation_quaternion.w = inst['Orientation']['r']
                    o.scale.x=inst['Scale']['X']
                    o.scale.y=inst['Scale']['Y']
                    o.scale.z=inst['Scale']['Z']
                    # empty_draw was replaced by empty_display
                    o.empty_display_size = .002
                    o.empty_display_type = 'CUBE'   
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
                                    #print('Group found for ',groupname)                               
                                    for i in range(start, start+num):
                                        #create the linked copy of the group of mesh
                                        
                                        new=bpy.data.collections.new(groupname)
                                        Sector_coll.children.link(new)
                                        new['nodeType']='worldInstancedMeshNode'
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
                                                
            case 'worldDecorationMeshNode': 
                #print('worldDecorationMeshNode',i)
                pass
            case 'worldInstancedOccluderNode':
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
                    o.location.x = inst['Position']['X'] /100
                    o.location.y = inst['Position']['Y'] /100
                    o.location.z = inst['Position']['Z'] /100
                    o.rotation_quaternion.x = inst['Orientation']['i']
                    o.rotation_quaternion.y = inst['Orientation']['j']
                    o.rotation_quaternion.z = inst['Orientation']['k']
                    o.rotation_quaternion.w = inst['Orientation']['r']
                    o.scale.x=inst['Scale']['X']
                    o.scale.y=inst['Scale']['Y']
                    o.scale.z=inst['Scale']['Z']
                    o.empty_display_size = 0.002
                    o.empty_display_type = 'IMAGE'   
            case 'worldStaticOccluderMeshNode':
                #print('worldStaticOccluderMeshNode',i)
                pass
            case 'worldCollisionNode':
                #print('worldCollisionNode',1)
                pass
            case 'worldStaticMeshNode': 
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
                                        new['nodeType']='worldStaticMeshNode'
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
                                            curse=bpy.context.scene.cursor.location
                                            bpy.context.scene.cursor.location=Vector((inst['Pivot']['X'] /100,inst['Pivot']['Y'] /100,inst['Pivot']['Z'] /100))
                                            with bpy.context.temp_override(selected_editable_objects=obj):
                                                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                                            
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
                                            bpy.context.scene.cursor.location=curse  
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
                                        new['nodeType']='worldInstancedDestructibleMeshNode'
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
                                            curse=bpy.context.scene.cursor.location
                                            bpy.context.scene.cursor.location=Vector((inst['Pivot']['X'] /100,inst['Pivot']['Y'] /100,inst['Pivot']['Z'] /100))
                                            with bpy.context.temp_override(selected_editable_objects=obj):
                                                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                                           
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
                                            bpy.context.scene.cursor.location=curse  
                                else:
                                    print('Mesh not found - ',meshname, ' - ',i, e['HandleId'])
                                            
            case _:
                print('None of the above',i)
                
                pass
    
    print('Finished with ',filepath)
    
Masters.hide_viewport=True
bpy.ops.object.select_all(action='SELECT')

print('Finished')