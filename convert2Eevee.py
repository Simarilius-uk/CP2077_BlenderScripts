import bpy
import math
import numpy as np

def np_array_from_image(img_name):
    img = bpy.data.images[img_name]
    return np.array(img.pixels[:])


matname='ml_l1_001_wa_pants__judy_masksset'


mat=bpy.data.materials.get(matname)

nodes=mat.node_tree
layers={}
for node in nodes.nodes:
     if node.name[:13]=='Image Texture' and node.label[:5]=='Layer':
         print(node.name, node.label)
         layers[node.label]=node

no_layers=len(layers.keys())

# Build the atlas
image_basename=layers['Layer_1'].image.name[:-1]
# Need to make it split them into 10 images per atlas, at some point they break blender if too big
pixels=[]
for i in range(1,no_layers+1):
    pixels.append(np_array_from_image(image_basename+str(i)))

pixels_D=np.concatenate(pixels,axis=0)  
# need to get the image size for width and height here
image = bpy.data.images.new(image_basename+'atlas', width=1024, height=1024*no_layers)
image.colorspace_settings.name='Non-Color'
image.pixels=pixels_D.tolist()
image.pack()

#replace the layer images with the atlas
for i in range(1,no_layers+1):
    layer=layers['Layer_'+str(i)]
    #change the texture to the atlas
    layer.image= image
    
    valNode=nodes.nodes.new("ShaderNodeValue")
    valNode.location=(layer.location[0]-250,layer.location[1]+20)
    valNode.outputs[0].default_value=i
    valNode.hide = True

    divNode=nodes.nodes.new("ShaderNodeMath")
    divNode.location=(layer.location[0]-800,layer.location[1]+20)
    divNode.operation='DIVIDE'
    divNode.inputs[0].default_value=1
    divNode.hide = True
    nodes.links.new(valNode.outputs[0],divNode.inputs[1])
    
    combNode=nodes.nodes.new("ShaderNodeCombineXYZ")
    combNode.location=(layer.location[0]-600,layer.location[1]+20)
    combNode.hide = True
    nodes.links.new(divNode.outputs[0],combNode.inputs[1])
    
    texMapNode = nodes.nodes.new("ShaderNodeTexCoord")
    texMapNode.location=(layer.location[0]-1000,layer.location[1])
    texMapNode.hide = True
    
    combNode2=nodes.nodes.new("ShaderNodeCombineXYZ")
    combNode2.location=(layer.location[0]-800,layer.location[1]-60)
    combNode2.inputs['X'].default_value=1.0
    combNode2.inputs['Y'].default_value=1/no_layers
    combNode2.inputs['Z'].default_value=1.0
    combNode2.hide = True
   
    
    mapRngNode = nodes.nodes.new("ShaderNodeMapRange")
    mapRngNode.location=(layer.location[0]-600,layer.location[1]-40)
    mapRngNode.data_type='FLOAT_VECTOR'
    mapRngNode.hide = True
    nodes.links.new(texMapNode.outputs['UV'],mapRngNode.inputs['Vector'])
    nodes.links.new(combNode2.outputs[0],mapRngNode.inputs[10])
     
    mapNode = nodes.nodes.new("ShaderNodeMapping")
    mapNode.location=(layer.location[0]-400,layer.location[1]-40)
    mapNode.vector_type='TEXTURE'
    mapNode.hide = True
    nodes.links.new(mapRngNode.outputs['Vector'],mapNode.inputs['Vector'])
    nodes.links.new(combNode.outputs[0],mapNode.inputs['Location'])
    nodes.links.new(mapNode.outputs[0],layer.inputs['Vector'])