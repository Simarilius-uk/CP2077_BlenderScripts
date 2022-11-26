# Script to tidy up a CP2077 rig and add IK constraints to the arms and legs
# Written by Simarilius, Nov 2022
# Latest at https://github.com/Simarilius-uk/CP2077_BlenderScripts/blob/main/TidyAndIK.py
# let me know on the CP modding Discord if you have issues.

import bpy
from mathutils import *; from math import *

bpy.ops.mesh.primitive_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), radius=.35)
circle=bpy.context.selected_objects[0]
circle.rotation_euler=(1.5708,0,0)
circle.data.transform(circle.matrix_basis)
circle.hide_set(True)
circle.hide_render=True
bpy.ops.mesh.primitive_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), radius=.35)
circle2=bpy.context.selected_objects[0]
circle2.hide_set(True)
circle2.hide_render=True

body = bpy.data.objects['BodyArmature']
for bone in body.data.bones:
    if 'JNT' in bone.name:
        print('JNT - ',bone.name)
        bone.layers[0]=False
        bone.layers[31]=True
    elif 'root'in bone.name or 'Root' in bone.name or 'gravity' in bone.name:
        print('root - ',bone.name)
        bone.layers[0]=False
        bone.layers[15]=True
    elif 'GRP' in bone.name:
        print('JNT - ',bone.name)
        bone.layers[0]=False
        bone.layers[30]=True



Pairs=[('LeftShoulder','LeftArm'),('LeftArm','LeftForeArm'),('LeftForeArm','LeftHand'),
('RightShoulder','RightArm'),('RightArm','RightForeArm'),('RightForeArm','RightHand'),
('LeftUpLeg','LeftLeg'),('LeftLeg','LeftFoot'),('RightUpLeg','RightLeg'),('RightLeg','RightFoot'),
('LeftInHandThumb','LeftHandThumb1'),('LeftHandThumb1','LeftHandThumb2'),
('LeftInHandIndex','LeftHandIndex1'),('LeftHandIndex1','LeftHandIndex2'),('LeftHandIndex2','LeftHandIndex3'),
('LeftInHandMiddle','LeftHandMiddle1'),('LeftHandMiddle1','LeftHandMiddle2'),('LeftHandMiddle2','LeftHandMiddle3'),
('LeftInHandRing','LeftHandRing1'),('LeftHandRing1','LeftHandRing2'),('LeftHandRing2','LeftHandRing3'),
('LeftInHandPinky','LeftHandPinky1'),('LeftHandPinky1','LeftHandPinky2'),('LeftHandPinky2','LeftHandPinky3'),
('RightInHandThumb','RightHandThumb1'),('RightHandThumb1','RightHandThumb2'),
('RightInHandIndex','RightHandIndex1'),('RightHandIndex1','RightHandIndex2'),('RightHandIndex2','RightHandIndex3'),
('RightInHandMiddle','RightHandMiddle1'),('RightHandMiddle1','RightHandMiddle2'),('RightHandMiddle2','RightHandMiddle3'),
('RightInHandRing','RightHandRing1'),('RightHandRing1','RightHandRing2'),('RightHandRing2','RightHandRing3'),
('RightInHandPinky','RightHandPinky1'),('RightHandPinky1','RightHandPinky2'),('RightHandPinky2','RightHandPinky3')
]
body.select_set(True)
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
body = bpy.data.objects['BodyArmature']
body.data.display_type='OCTAHEDRAL'
body.show_in_front = True

bpy.context.view_layer.objects.active = body

bpy.ops.object.mode_set(mode='EDIT', toggle=False)
body = bpy.data.objects['BodyArmature']
for (Abone,Abone2) in Pairs:
    bone=body.data.edit_bones[Abone]
    bone2=body.data.edit_bones[Abone2]
    bone.tail=bone2.head

# LEFT LEG IK Setup

Lleg=body.data.edit_bones["LeftLeg"]
eb=body.data.edit_bones.new("KneeIK.L")
eb.head=Lleg.head+Vector((0,.3,0))
eb.tail=Lleg.head+Vector((0,.5,0))
eb.use_deform=False
eb.layers[0]=False
eb.layers[16]=True
eb2=body.data.edit_bones.new("HeelIK.L")
eb2.head=Lleg.tail
eb2.tail=Lleg.tail+Vector((0,-.2,0))
eb2.use_deform=False
eb2.layers[0]=False
eb2.layers[16]=True
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

bpy.ops.object.mode_set(mode='EDIT', toggle=False)

Lfoot=body.data.edit_bones["LeftFoot"]
Lfoot.select=True
body.data.bones["HeelIK.L"].select=True
bpy.context.object.data.edit_bones.active = body.data.edit_bones["HeelIK.L"]
bpy.ops.armature.parent_set(type='OFFSET')
bpy.ops.armature.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='POSE', toggle=False)

Lleg=body.pose.bones["LeftLeg"]
LlegIK=Lleg.constraints.new('IK')
LlegIK.chain_count=2
LlegIK.target=body
LlegIK.subtarget='HeelIK.L'
LlegIK.pole_target=body
LlegIK.pole_subtarget='KneeIK.L'
LlegIK.pole_angle=180

Lfoot=body.pose.bones["LeftFoot"]
LfLoc=Lfoot.constraints.new('COPY_LOCATION')
LfLoc.target=body
LfLoc.subtarget='LeftLeg'
LfLoc.head_tail=1
body.pose.bones["HeelIK.L"].custom_shape=circle


bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#RIGHT LEG IK Setup

body = bpy.data.objects['BodyArmature']

bpy.ops.object.mode_set(mode='EDIT', toggle=False)
Rleg=body.data.edit_bones["RightLeg"]
eb=body.data.edit_bones.new("KneeIK.R")
eb.head=Rleg.head+Vector((0,.3,0))
eb.tail=Rleg.head+Vector((0,.5,0))
eb.use_deform=False
eb.layers[0]=False
eb.layers[16]=True
eb2=body.data.edit_bones.new("HeelIK.R")
eb2.head=Rleg.tail
eb2.tail=Rleg.tail+Vector((0,-.2,0))
eb2.use_deform=False
eb2.layers[0]=False
eb2.layers[16]=True
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

bpy.ops.object.mode_set(mode='EDIT', toggle=False)

Rfoot=body.data.edit_bones["RightFoot"]
Rfoot.select=True
body.data.bones["HeelIK.R"].select=True
bpy.context.object.data.edit_bones.active = body.data.edit_bones["HeelIK.R"]
bpy.ops.armature.parent_set(type='OFFSET')
bpy.ops.armature.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='POSE', toggle=False)

Rleg=body.pose.bones["RightLeg"]
RlegIK=Rleg.constraints.new('IK')
RlegIK.chain_count=2
RlegIK.target=body
RlegIK.subtarget='HeelIK.R'
RlegIK.pole_target=body
RlegIK.pole_subtarget='KneeIK.R'
RlegIK.pole_angle=180

Rfoot=body.pose.bones["RightFoot"]
RfLoc=Rfoot.constraints.new('COPY_LOCATION')
RfLoc.target=body
RfLoc.subtarget='RightLeg'
RfLoc.head_tail=1
body.pose.bones["HeelIK.R"].custom_shape=circle

bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#LEFT ARM

body = bpy.data.objects['BodyArmature']
bpy.ops.object.mode_set(mode='EDIT', toggle=False)

LArm=body.data.edit_bones["LeftForeArm"]
eb=body.data.edit_bones.new("ElbowIK.L")
eb.head=LArm.head+Vector((0,-.3,0))
eb.tail=LArm.head+Vector((0,-.5,0))
eb.use_deform=False
eb.layers[0]=False
eb.layers[16]=True
eb2=body.data.edit_bones.new("WristIK.L")
eb2.head=LArm.tail
eb2.tail=LArm.tail+Vector((0,-.2,0))
eb2.use_deform=False
eb2.layers[0]=False
eb2.layers[16]=True
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

bpy.ops.object.mode_set(mode='EDIT', toggle=False)

LHand=body.data.edit_bones["LeftHand"]
LHand.select=True
body.data.bones["WristIK.L"].select=True
bpy.context.object.data.edit_bones.active = body.data.edit_bones["WristIK.L"]
bpy.ops.armature.parent_set(type='OFFSET')
bpy.ops.armature.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='POSE', toggle=False)

LArm=body.pose.bones["LeftForeArm"]
LArmIK=LArm.constraints.new('IK')
LArmIK.chain_count=2
LArmIK.target=body
LArmIK.subtarget='WristIK.L'
LArmIK.pole_target=body
LArmIK.pole_subtarget='ElbowIK.L'
LArmIK.pole_angle=180

LHand=body.pose.bones["LeftHand"]
LHLoc=LHand.constraints.new('COPY_LOCATION')
LHLoc.target=body
LHLoc.subtarget='LeftForeArm'
LHLoc.head_tail=1
body.pose.bones["WristIK.L"].custom_shape=circle
body.pose.bones["WristIK.L"].custom_shape_transform=LHand
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

#RIGHT ARM

body = bpy.data.objects['BodyArmature']
bpy.ops.object.mode_set(mode='EDIT', toggle=False)

RArm=body.data.edit_bones["RightForeArm"]
eb=body.data.edit_bones.new("ElbowIK.R")
eb.head=RArm.head+Vector((0,-.3,0))
eb.tail=RArm.head+Vector((0,-.5,0))
eb.use_deform=False
eb.layers[0]=False
eb.layers[16]=True
eb2=body.data.edit_bones.new("WristIK.R")
eb2.head=RArm.tail
eb2.tail=RArm.tail+Vector((0,-.2,0))
eb2.use_deform=False
eb2.layers[0]=False
eb2.layers[16]=True
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

bpy.ops.object.mode_set(mode='EDIT', toggle=False)

RHand=body.data.edit_bones["RightHand"]
RHand.select=True
body.data.bones["WristIK.R"].select=True
bpy.context.object.data.edit_bones.active = body.data.edit_bones["WristIK.R"]
bpy.ops.armature.parent_set(type='OFFSET')
bpy.ops.armature.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='POSE', toggle=False)

RArm=body.pose.bones["RightForeArm"]
RArmIK=RArm.constraints.new('IK')
RArmIK.chain_count=2
RArmIK.target=body
RArmIK.subtarget='WristIK.R'
RArmIK.pole_target=body
RArmIK.pole_subtarget='ElbowIK.R'
RArmIK.pole_angle=180

RHand=body.pose.bones["RightHand"]
RHLoc=RHand.constraints.new('COPY_LOCATION')
RHLoc.target=body
RHLoc.subtarget='RightForeArm'
RHLoc.head_tail=1
body.pose.bones["WristIK.R"].custom_shape=circle
body.pose.bones["WristIK.R"].custom_shape_transform=RHand

bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
