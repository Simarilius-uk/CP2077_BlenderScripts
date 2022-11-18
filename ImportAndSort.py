import json
import glob
import os
import bpy


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

path = 'F:\\CPmod\\arch\\source\\raw\\base'

C = bpy.context
coll_scene = C.scene.collection
if "MasterInstances" not in coll_scene.children.keys():
    Masters=bpy.data.collections.new("MasterInstances")
    coll_scene.children.link(Masters)
else:
    Masters=bpy.data.collections.get("MasterInstances")



# Set target collection to a known collection 
coll_target = coll_scene.children.get("MasterInstances")


meshes =  glob.glob(path+"\**\*.glb", recursive = True)
total=len(meshes)
print(total)
i=0
printProgressBar(i, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
for mesh in meshes:
    if os.path.basename(mesh)[:-4] not in Masters.children.keys():
        try:
           bpy.ops.io_scene_gltf.cp77(filepath=mesh)
           objs = C.selected_objects
           
           
           move_coll= coll_scene.children.get( objs[0].users_collection[0].name )
           coll_target.children.link(move_coll) 
           coll_scene.children.unlink(move_coll)
           # If target found and object list not empty
           #if coll_target and objs:
               # Loop through all objects
            #   print('moving')
             #  for ob in objs:
              #     active_coll = C.view_layer.active_layer_collection.collection
                   
                   
                   
                   
                   # Loop through all collections the obj is linked to
                   #for coll in ob.users_collection:
                    #   # Unlink the object
                     #  coll.objects.unlink(ob)
                   # Link each object to the target collection
                   #coll_target.objects.link(ob)      
        except:
            print("Failed on ",mesh)
    else:
        print('already imported')
            
    i=i+1
    printProgressBar(i, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
    

