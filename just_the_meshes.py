# Script to import CP2077 streaming sectors to Blender 
# Recommended for use without materials
# see https://wiki.redmodding.org/wolvenkit/guides/modding-community/exporting-streaming-sectors-to-blender
# By Simarilius Oct 2022

import json
import glob
import os
import bpy
path = 'F:\\CPmod\\coyote\\source\\raw'

withMaterials=False

meshes =  glob.glob(path+"\**\*.glb", recursive = True)
glbnames = [ os.path.basename(x) for x in meshes]
meshnames = [ os.path.splitext(x)[0]+".mesh" for x in glbnames]

jsonpath = glob.glob(path+"\**\*.streamingsector.json", recursive = True)
for filepath in jsonpath:
    with open(filepath,'r') as f: 
          j=json.load(f) 
    t=j['Data']['RootChunk']['nodeData']['Data']
    nodes = j["Data"]["RootChunk"]["nodes"]
    #print(len(nodes))
    for i,e in enumerate(nodes):

        #if i > 2: break
        data = e['Data']
        type = data['$type']
        
        match type:
            case 'worldEntityNode': 
                print('worldEntityNode',i)
                pass
            case 'worldInstancedMeshNode':
                #print('worldInstancedMeshNode')
                meshname = data['mesh']['DepotPath'] 
                num=data['worldTransformsBuffer']['numElements']
                start=data['worldTransformsBuffer']['startIndex']
                if(meshname != 0):
                                #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                                glbfoundname = [ x for x in meshes if os.path.splitext(str(meshname))[0] in x] 
                                if(len(glbfoundname) == 1):
                                    #print('Glb found - ',glbfoundname)     
                                    
                                    for i in range(start, start+num):
                                        if withMaterials:
                                            try:
                                                bpy.ops.io_scene_gltf.cp77(filepath=glbfoundname[0])                                        
                                            except:
                                                bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                        else:
                                            bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                         
                                        objects = bpy.context.selected_objects
                                        for obj in objects:                            
                                            nn= str(data['debugName']).replace('{','').replace('}','')
                                            nn = [nn[1:],nn][nn[0].isalnum()]
                                            #print(nn)                            
                                            obj.name = nn
                                            #print(inst['Position'].keys())
                                            
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
                #print('worldStaticDecalNode')
                pass
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
                                glbfoundname = [ x for x in meshes if os.path.splitext(str(meshname))[0] in x] 
                                if(len(glbfoundname) == 1):
                                    #print('Glb found - ',glbfoundname)     
                                    #print('Glb found, looking for instances of ',i)
                                    instances = [x for x in t if x['NodeIndex'] == i]
                                    for inst in instances:
                                        #print('Inst - ',i, ' - ',meshname)
                                        
                                        if withMaterials:
                                            try:
                                                bpy.ops.io_scene_gltf.cp77(filepath=glbfoundname[0])                                        
                                            except:
                                                bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                        else:
                                            bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                        
                                        objects = bpy.context.selected_objects
                                        #obj = bpy.context.object
                                        #print(data.keys())
                                        for obj in objects:                            
                                            nn= str(data['debugName']).replace('{','').replace('}','')
                                            nn = [nn[1:],nn][nn[0].isalnum()]
                                            #print(nn)                            
                                            obj.name = nn
                                            #print(inst['Position'].keys())
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
                                glbfoundname = [ x for x in meshes if os.path.splitext(str(meshname))[0] in x] 
                                if(len(glbfoundname) == 1):
                                    #print('Glb found - ',glbfoundname)     
                                    #print('Glb found, looking for instances of ',i)
                                    instances = [x for x in t if x['NodeIndex'] == i]
                                    for inst in instances:
                                        #print('Inst - ',i, ' - ',meshname)
                                        
                                        if withMaterials:
                                            try:
                                                bpy.ops.io_scene_gltf.cp77(filepath=glbfoundname[0])                                        
                                            except:
                                                bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                        else:
                                            bpy.ops.import_scene.gltf(filepath=glbfoundname[0])
                                        
                                        objects = bpy.context.selected_objects
                                        #obj = bpy.context.object
                                        #print(data.keys())
                                        for obj in objects:                            
                                            nn= str(data['debugName']).replace('{','').replace('}','')
                                            nn = [nn[1:],nn][nn[0].isalnum()]
                                            #print(nn)                            
                                            obj.name = nn
                                            #print(inst['Position'].keys())
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
                                            
            case _:
                print('None of the above',i)
                
                pass
                   
    print("Done with ",filepath)   
print('Finished')
