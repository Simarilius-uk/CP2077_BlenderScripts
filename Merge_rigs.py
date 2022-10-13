import bpy
C = bpy.context
D = bpy.data

head = bpy.data.objects['HeadArmature']
body = bpy.data.objects['BodyArmature']
head_coll= head.users_collection[0]
dupes = []
relate={}

for bone in head.data.bones:
    if bone.name in body.data.bones.keys() and bone.name!='Root':
        dupes.append(bone.name)
        relate[bone.name]=bone.children.keys()

obs = bpy.context.scene.objects["HeadArmature"]   
obs.select_set(True) 
bpy.ops.object.mode_set(mode='EDIT')
for bone in dupes:
    bn=head.data.edit_bones[bone]
    head.data.edit_bones.remove(bn)

bpy.ops.object.mode_set(mode='OBJECT')

ob = bpy.context.scene.objects["BodyArmature"]  # Get the armature
bpy.ops.object.select_all(action='DESELECT')    # Deselect all objects
bpy.context.view_layer.objects.active = ob      # Make the armature the active object 
ob.select_set(True)                             # Select the armature

obs = [bpy.data.objects['BodyArmature'], bpy.data.objects['HeadArmature']]

c = {}
c["object"] = bpy.data.objects['BodyArmature']
c["active_object"] = bpy.data.objects['BodyArmature']
c["selected_objects"] = obs
c["selected_editable_objects"] = obs

with C.temp_override(active_object=c["active_object"], selected_editable_objects=obs):
    bpy.ops.object.join()

bpy.ops.object.mode_set(mode='EDIT')
for bn in dupes:
    for bone in relate[bn]:
        if bone not in body.data.bones[bn].children.keys():
            print(bone)
            #child = body.data.bones[bone]
            if bone!='Root':
                body.data.edit_bones[bone].parent = body.data.edit_bones[bn]

bpy.ops.object.mode_set(mode='OBJECT')

for obj in head_coll.objects:
    obj.modifiers['Armature'].object=body

#arm.data.edit_bones['boneName'].parent = arm.data.edit_bones['parentBone']