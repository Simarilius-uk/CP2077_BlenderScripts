import bpy
import math
import numpy as np

def np_array_from_image(img_name):
    img = bpy.data.images[img_name]
    return np.array(img.pixels[:])

# Change this to the name of the material you want to convert
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
for i in range(no_layers,0,-1):
    pixels.append(np_array_from_image(image_basename+str(i)))

pixels_D=np.concatenate(pixels,axis=0)  
# need to get the image size for width and height here
image_w= layers['Layer_1'].image.size[0]
image_h= layers['Layer_1'].image.size[1]
image = bpy.data.images.new(image_basename+'atlas', width=image_w, height=image_h*no_layers)
image.colorspace_settings.name='Non-Color'
image.pixels=pixels_D.tolist()
image.pack()

#replace the layer images with the atlas
for i in range(1,no_layers+1):
    layer=layers['Layer_'+str(i)]
    #change the texture to the atlas
    layer.image= image
    
    valNode=nodes.nodes.new("ShaderNodeValue")
    valNode.location=(layer.location[0]-1100,layer.location[1]+30)
    valNode.outputs[0].default_value=i
    valNode.hide = True

    subNode=nodes.nodes.new("ShaderNodeMath")
    subNode.location=(layer.location[0]-1000,layer.location[1]+30)
    subNode.operation='SUBTRACT'
    subNode.inputs[0].default_value=no_layers
    subNode.hide = True
    nodes.links.new(valNode.outputs[0],subNode.inputs[1])

    divNode=nodes.nodes.new("ShaderNodeMath")
    divNode.location=(layer.location[0]-700,layer.location[1]+30)
    divNode.operation='DIVIDE'
    divNode.inputs[1].default_value=no_layers
    divNode.hide = True
    nodes.links.new(subNode.outputs[0],divNode.inputs[0])
    
    combNode=nodes.nodes.new("ShaderNodeCombineXYZ")
    combNode.location=(layer.location[0]-600,layer.location[1]+30)
    combNode.hide = True
    nodes.links.new(divNode.outputs[0],combNode.inputs[1])
    
    texMapNode = nodes.nodes.new("ShaderNodeTexCoord")
    texMapNode.location=(layer.location[0]-1000,layer.location[1]-10)
    texMapNode.hide = True
    
    combNode2=nodes.nodes.new("ShaderNodeCombineXYZ")
    combNode2.location=(layer.location[0]-800,layer.location[1]-40)
    combNode2.inputs['X'].default_value=1.0
    combNode2.inputs['Y'].default_value=1/no_layers
    combNode2.inputs['Z'].default_value=1.0
    combNode2.hide = True
   
    
    mapRngNode = nodes.nodes.new("ShaderNodeMapRange")
    mapRngNode.location=(layer.location[0]-600,layer.location[1]-30)
    mapRngNode.data_type='FLOAT_VECTOR'
    mapRngNode.hide = True
    nodes.links.new(texMapNode.outputs['UV'],mapRngNode.inputs['Vector'])
    nodes.links.new(combNode2.outputs[0],mapRngNode.inputs[10])
     
    mapNode = nodes.nodes.new("ShaderNodeMapping")
    mapNode.location=(layer.location[0]-400,layer.location[1]-40)
    mapNode.vector_type='POINT'
    mapNode.hide = True
    nodes.links.new(mapRngNode.outputs['Vector'],mapNode.inputs['Vector'])
    nodes.links.new(combNode.outputs[0],mapNode.inputs['Location'])
    nodes.links.new(mapNode.outputs[0],layer.inputs['Vector'])
    
groups=[]
for node in nodes.nodes:
     if node.name[:14]=='Mat_Mod_Layer_' and node.type=='GROUP':
         print(node.name)
         groups.append(node)

#replace the black and white textures with generated plain color checkers. (dont seem to count as textures against the limit)
for group in groups:
    inner=group.node_tree.nodes['Group'].node_tree
    for node in inner.nodes:
        if node.name[:13]=='Image Texture':
            if node.image.name=='white':
                whiteNode = inner.nodes.new("ShaderNodeTexChecker")
                whiteNode.inputs[1].default_value = (1,1,1,1)
                whiteNode.inputs[2].default_value = (1,1,1,1)
                whiteNode.location=(node.location[0],node.location[1])
                inner.links.new(node.inputs[0].links[0].from_socket, whiteNode.inputs[0])
                inner.links.new(whiteNode.outputs[0],node.outputs[0].links[0].to_socket)
                inner.nodes.remove(node)
                whiteNode.hide = True
            elif node.image.name=='black':
                blackNode = inner.nodes.new("ShaderNodeTexChecker")
                blackNode.inputs[1].default_value = (0,0,0,1)
                blackNode.inputs[2].default_value = (0,0,0,1)                
                blackNode.location=(node.location[0],node.location[1])
                inner.links.new(node.inputs[0].links[0].from_socket, blackNode.inputs[0])
                inner.links.new(blackNode.outputs[0],node.outputs[0].links[0].to_socket)
                inner.nodes.remove(node)
                blackNode.hide = True
     
     
