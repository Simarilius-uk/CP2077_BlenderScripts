
import bpy

obj=bpy.context.active_object
mat=obj.material_slots[0].material
nodes=mat.node_tree.nodes

colors=[[ 1.0 , 0.0 , 0.0 ],[ 0.0 , 1.0 , 0.0 ],[ 0.0 , 0.0 , 1.0 ],[ 1.0 , 1.0 , 0.0 ],[ 1.0 , 0.0 , 1.0 ],
[ 0.0 , 1.0 , 1.0 ],[ 0.5019607843137255 , 0.0 , 0.0 ],[ 0.0 , 0.5019607843137255 , 0.0 ],[ 0.0 , 0.0 , 0.5019607843137255 ],
[ 0.5019607843137255 , 0.5019607843137255 , 0.0 ],[ 0.5019607843137255 , 0.0 , 0.5019607843137255 ],[ 0.0 , 0.5019607843137255 , 0.5019607843137255 ],
[ 1.0 , 0.5019607843137255 , 0.0 ],[ 1.0 , 0.0 , 0.5019607843137255 ],[ 0.5019607843137255 , 1.0 , 0.0 ],[ 0.0 , 0.5019607843137255 , 1.0 ],
[ 0.5019607843137255 , 0.0 , 1.0 ],[ 1.0 , 0.5019607843137255 , 0.5019607843137255 ],[ 0.5019607843137255 , 1.0 , 0.5019607843137255 ],
[ 0.5019607843137255 , 0.5019607843137255 , 1.0 ]]
if mat.get('MLSetup'):    
    layer=0
    layer_txt=''
    numLayers= len([x for x in nodes if 'Image Texture' in x.name])
    while layer<numLayers:            
        LayerGroup=nodes['Mat_Mod_Layer_'+str(layer)]
        LayerGroup.inputs['ColorScale'].default_value[0]=colors[layer][0]
        LayerGroup.inputs['ColorScale'].default_value[1]=colors[layer][1]
        LayerGroup.inputs['ColorScale'].default_value[2]=colors[layer][2]        
        layer+=1

        
    
    