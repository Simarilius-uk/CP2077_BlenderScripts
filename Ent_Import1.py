# Blender Entity import script by Simarilius
import json
import glob
import os
import bpy
C = bpy.context
coll_scene = C.scene.collection
path = 'F:\\CPmod\\coyote\\source\\raw'
ent_names = ['vending_machine_1.ent','vending_machine_1.ent','vending_machine_1.ent']
# The list below needs to be the appearanceNames for each ent that you want to import
appearences =['a_burrito','c_nicola','o_chromanticore']
 
jsonpath = glob.glob(path+"\**\*.ent.json", recursive = True)
if len(jsonpath)==0:
    print('No jsons found')
meshes =  glob.glob(path+"\**\*.glb", recursive = True)
glbnames = [ os.path.basename(x) for x in meshes]
meshnames = [ os.path.splitext(x)[0]+".mesh" for x in glbnames]
if len(meshnames)==0:
    print('No Meshes found')
if len(meshnames)>0 and len(jsonpath)>0:
    for x,ent_name in enumerate(ent_names):
        ent_coll=bpy.data.collections.new(ent_name+'_'+appearences[x])
        ent_coll['appearanceName']=appearences[x]
        ent_coll['depotPath']=ent_name
        coll_scene.children.link(ent_coll)
        for i,e in enumerate(jsonpath):
             if os.path.basename(e)== ent_name+'.json' :
                 filepath=e
                 
        with open(filepath,'r') as f: 
              j=json.load(f) 
        comps=[]
        apps= j['Data']['RootChunk']['appearances']
        if len(apps)>0:
            app_idx=0
            for i,a in enumerate(apps):
                if a['appearanceName']==appearences[x]:
                    app_idx=x
            app_file = apps[app_idx]['appearanceResource']['DepotPath']
            app_path = glob.glob(path+"\**\*.app.json", recursive = True)
            for i,e in enumerate(app_path):
                print(os.path.basename(e))
                if os.path.basename(e)== os.path.basename(app_file)+'.json' :
                    filepath=e
                    
                if len(filepath)>0:
                    with open(filepath,'r') as a: 
                        a_j=json.load(a)
                    comps= a_j['Data']['RootChunk']['appearances'][app_idx]['Data']['components']
                            
        if len(comps)<1:      
            comps= j['Data']['RootChunk']['components']
        for c in comps:
            if 'mesh' in c.keys():
                print(c['mesh']['DepotPath'])
                app='default'
                if isinstance( c['mesh']['DepotPath'], str):       
                    if  os.path.exists(os.path.join(path, c['mesh']['DepotPath'][:-4]+'glb')):
                        try:
                           bpy.ops.io_scene_gltf.cp77(filepath=os.path.join(path, c['mesh']['DepotPath'][:-4]+'glb'))
                           objs = C.selected_objects
                           x=c['localTransform']['Position']['x']['Bits']/131072
                           y=c['localTransform']['Position']['y']['Bits']/131072
                           z=c['localTransform']['Position']['z']['Bits']/131072
                           for obj in objs:
                               obj.location.x = x
                               obj.location.y = y                     
                               obj.location.z = z 
                               obj.rotation_quaternion.x = c['localTransform']['Orientation']['i']
                               obj.rotation_quaternion.y = c['localTransform']['Orientation']['j']
                               obj.rotation_quaternion.z = c['localTransform']['Orientation']['k']
                               obj.rotation_quaternion.w = c['localTransform']['Orientation']['r']
                               if 'scale' in c['localTransform'].keys():    
                                   obj.scale.x = c['localTransform']['scale']['X'] 
                                   obj.scale.y = c['localTransform']['scale']['Y'] 
                                   obj.scale.z = c['localTransform']['scale']['Z'] 
                           move_coll= coll_scene.children.get( objs[0].users_collection[0].name )
                           move_coll['depotPath']=c['mesh']['DepotPath']
                           ent_coll.children.link(move_coll) 
                           coll_scene.children.unlink(move_coll)
                        except:
                            print("Failed on ",c['mesh']['DepotPath'])

