import sys
sys.path.append("F://CPmod//ImportPluginGIT//i_scene_cp77_gltf//material_types")
sys.path.append("F://CPmod//ImportPluginGIT//i_scene_cp77_gltf//main")

import bpy
import os
import json

from common import *

class speedtree:
    def __init__(self, BasePath,image_format):
        self.BasePath = BasePath
        self.image_format = image_format
    def create(self,Data,Mat):
        CurMat = Mat.node_tree
        CurMat.nodes['Principled BSDF'].inputs['Specular'].default_value = 0
        #Diffuse
       


        dTexMapping = CurMat.nodes.new("ShaderNodeMapping")
        dTexMapping.label = "UVMapping"
        dTexMapping.location = (-1000,300)

        if "DiffuseMap" in Data:
            dImgNode = CreateShaderNodeTexImage(CurMat,self.BasePath + Data["DiffuseMap"],-800,400,'DiffuseTexture',self.image_format)
            CurMat.links.new(dTexMapping.outputs[0],dImgNode.inputs[0])
            CurMat.links.new(dImgNode.outputs[0],CurMat.nodes['Principled BSDF'].inputs['Base Color'])
            CurMat.links.new(dImgNode.outputs[1],CurMat.nodes['Principled BSDF'].inputs['Alpha'])
            dImgNode.hide=False

        if "UVOffsetX" in Data:
            dTexMapping.inputs[1].default_value[0] = Data["UVOffsetX"]
        if "UVOffsetY" in Data:
            dTexMapping.inputs[1].default_value[1] = Data["UVOffsetY"]
        if "UVRotation" in Data:
            dTexMapping.inputs[2].default_value[0] = Data["UVRotation"]
            dTexMapping.inputs[2].default_value[1] = Data["UVRotation"]
        if "UVScaleX" in Data:
            dTexMapping.inputs[3].default_value[0] = Data["UVScaleX"]
        if "UVScaleY" in Data:
            dTexMapping.inputs[3].default_value[1] = Data["UVScaleY"]

        UVNode = CurMat.nodes.new("ShaderNodeTexCoord")
        UVNode.location = (-1200,300)
        CurMat.links.new(UVNode.outputs[2],dTexMapping.inputs[0])

        #CurMat.links.new(mulNode.outputs[0],CurMat.nodes['Principled BSDF'].inputs['Alpha'])


        if "NormalMap" in Data:
            nMap = CreateShaderNodeNormalMap(CurMat,self.BasePath + Data["NormalMap"],-300,-350,'NormalMap',self.image_format)
            CurMat.links.new(nMap.outputs[0],CurMat.nodes['Principled BSDF'].inputs['Normal'])
            nMap.inputs[1].links[0].from_node.inputs[0].links[0].from_node.hide=False
            nMap.inputs[1].links[0].from_node.inputs[0].links[0].from_node.location = (-800,-200)


        if "TransGlossMap" in Data:
            rImgNode = CreateShaderNodeTexImage(CurMat,self.BasePath + Data["TransGlossMap"],-800,100,'TransGlossMap',self.image_format,True)
            rImgNode.hide=False            
            mathNode = CurMat.nodes.new("ShaderNodeMath")
            mathNode.operation = 'SUBTRACT'
            mathNode.inputs[0].default_value = 1.0
            mathNode.location = (-400,100)
            CurMat.links.new(rImgNode.outputs[0],mathNode.inputs[1])
            CurMat.links.new(mathNode.outputs[0],CurMat.nodes['Principled BSDF'].inputs['Roughness'])

filepath="F:\\CPmod\\lakehouse\\source\\raw\\base\\environment\\vegetation\\shrubs\\atriplex\\atriplex_big_thorny.glb"
BasePath = os.path.splitext(filepath)[0]
file = open(BasePath + ".Material.json",mode='r')
obj = json.loads(file.read())
BasePath = str(obj["MaterialRepo"])  + "\\"

bpyMat = bpy.data.materials.new("TestMat")
bpyMat.use_nodes = True
rawMat=obj['Materials'][0]
speedtree = speedtree(BasePath,"png")
speedtree.create(rawMat["Data"],bpyMat)


