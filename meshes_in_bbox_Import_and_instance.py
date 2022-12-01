import json
import glob
import os
import bpy
from mathutils import Vector, Matrix
from pathlib import Path

C = bpy.context

def get_pos(inst):
    pos=[0,0,0]
    if 'Properties' in inst['Position'].keys():
        pos[0] = inst['Position']['Properties']['X'] 
        pos[1] = inst['Position']['Properties']['Y'] 
        pos[2] = inst['Position']['Properties']['Z']           
    else:
        pos[0] = inst['Position']['X'] 
        pos[1] = inst['Position']['Y'] 
        pos[2] = inst['Position']['Z'] 
    return pos

def in_bounds(pos,bounds):
   # print(pos, 'vs ',bounds)
    if pos[0]>bounds[3] or pos[0]< bounds[0]:
        return False
    if pos[1]>bounds[4] or pos[1]< bounds[1]:
        return False
    if pos[2]>bounds[5] or pos[2]< bounds[2]:
        return False
    return True

# Enter the path to your projects source\raw\base folder below, needs double slashes between folder names.
path = 'F:\\CPmod\\Totentanz\\source\\raw\\base'

# Enter 2 sets of user co-ords that define the area of interest (bottom left, top right, defines box orienatated with grid)



PointA = [-8000,-9000,67]
PointB = [8000,10080,67]
# grab everything within Zmax+z_tol to Zmin-z_tol
z_tol = 500

bounds =[min(PointA[0],PointB[0]),min(PointA[1],PointB[1]),min(PointA[2],PointB[2])-z_tol, max(PointA[0],PointB[0]),max(PointA[1],PointB[1]),max(PointA[2],PointB[2])+z_tol]

jsonpath = glob.glob(path+"\**\*.streamingsector.json", recursive = True)
len(jsonpath)

meshes=[]


for filepath in jsonpath:    
    with open(filepath,'r') as f: 
          j=json.load(f) 
    sectorName=os.path.basename(filepath)[:-5]
    t=j['Data']['RootChunk']['nodeData']['Data']
    nodes = j["Data"]["RootChunk"]["nodes"]
    print(len(nodes))
    for i,e in enumerate(nodes):
        data = e['Data']
        type = data['$type']
        match type:
            case 'worldEntityNode': 
                print('worldEntityNode',i)
                instances = [x for x in t if x['NodeIndex'] == i]
                for inst in instances:
                   # print( inst )
                    pos=get_pos(inst)
                    if in_bounds(pos, bounds):
                        meshes.append({'basename':e['Data']['entityTemplate']['DepotPath'],'appearance':e['Data']['appearanceName'],'sector':sectorName})
            case 'worldInstancedMeshNode':
                meshname = data['mesh']['DepotPath'] 
                num=data['worldTransformsBuffer']['numElements']
                start=data['worldTransformsBuffer']['startIndex']
                if(meshname != 0):
                    for i in range(start, start+num):
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for inst in instances:
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
                            pos = [inst_trans['translation']['X'] ,inst_trans['translation']['Y'] , inst_trans['translation']['Z'] ]
                            if in_bounds(pos, bounds):
                                meshes.append({'basename':data['mesh']['DepotPath'] ,'appearance':e['Data']['meshAppearance'],'sector':sectorName})
            case 'worldStaticMeshNode' | 'worldBuildingProxyMeshNode' | 'worldGenericProxyMeshNode': 
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                        #print('Mesh - ',meshname, ' - ',i, e['HandleId'])
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for inst in instances:
                            pos = get_pos(inst)
                            if in_bounds(pos, bounds):
                                meshes.append({'basename':data['mesh']['DepotPath'] ,'appearance':e['Data']['meshAppearance'],'sector':sectorName})
            case 'worldInstancedDestructibleMeshNode':
                #print('worldInstancedDestructibleMeshNode',i)
                if isinstance(e, dict) and 'mesh' in data.keys():
                    meshname = data['mesh']['DepotPath']
                    #print('Mesh name is - ',meshname, e['HandleId'])
                    if(meshname != 0):
                        instances = [x for x in t if x['NodeIndex'] == i]
                        for inst in instances:
                            pos = get_pos(inst)
                            if in_bounds(pos, bounds):
                                meshes.append({'basename':data['mesh']['DepotPath'] ,'appearance':e['Data']['meshAppearance'],'sector':sectorName})

len(meshes)                                            

basenames=[]
for m in meshes:
     if m['basename'] not in basenames:
         basenames.append(m['basename'])
'''
#uncomment this block to generate the paths to use with the wscript add to project script
savepath='F:\\CPmod\\script\\basepaths.txt'
pp=pprint.pformat(basenames)
with open(savepath,'w') as out: 
    out.write(pp)
'''
meshes_w_apps={}

def add_to_list(mesh, dict):
     if mesh['basename'] in dict.keys():
         if mesh['appearance'] not in dict[mesh['basename']]['apps']:
             dict[mesh['basename']]['apps'].append(mesh['appearance'])
         if mesh['sector'] not in dict[mesh['basename']]['sectors']:
            dict[mesh['basename']]['sectors'].append(mesh['sector'])
     else:
         dict[mesh['basename']]={'apps':[mesh['appearance']],'sectors':[mesh['sector']]}

for m in meshes:
   if len(m)>0:
        add_to_list(m , meshes_w_apps)

len(meshes_w_apps)
path = 'F:\\CPmod\\Totentanz\\source\\raw'
import time
C = bpy.context
coll_scene = C.scene.collection
if "MasterInstances" not in coll_scene.children.keys():
    coll_target=bpy.data.collections.new("MasterInstances")
    coll_scene.children.link(coll_target)
else:
    coll_target=bpy.data.collections.get("MasterInstances")



start_time = time.time()

from_mesh_no=101
to_mesh_no=160

for i,m in enumerate(meshes_w_apps):
    if i>=from_mesh_no and i<=to_mesh_no:
        #print(m, meshes_w_apps[m]['apps'])
        apps=[]
        for meshApp in meshes_w_apps[m]['apps']:
            dic={}
            dic['name']=meshApp
            apps.append(dic)
        impapps=tuple(apps)
        print(os.path.join(path, m[:-4]+'glb'),impapps)
        meshpath=os.path.join(path, m[:-4]+'glb')
        try:
            bpy.ops.io_scene_gltf.cp77(filepath=meshpath, appearances=impapps)
            objs = C.selected_objects
            move_coll= coll_scene.children.get( objs[0].users_collection[0].name )
            coll_target.children.link(move_coll) 
            coll_scene.children.unlink(move_coll)
        except:
            print('failed on ',os.path.basename(meshpath))

print("--- %s seconds ---" % (time.time() - start_time))

# first 20 267 secs w all materials
# 82 with just required 
print('done')


#68009.89051365852 second