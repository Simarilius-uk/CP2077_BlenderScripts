# Script to create a panel in the tools section of the side panel of the Node Editor
# Gives you info on the active node, and lets you copy a create_node command that would reproduce the node
# By Simarilius, July 23

import bpy
from bpy.types import Panel

class NODE_PT_InfoPanel(Panel):
    bl_label = "Node Info Panel"
    bl_idname = "NODE_PT_info_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree

    def draw(self, context):
        layout = self.layout

        # Get the active node
        active_node = context.active_node

        if active_node:
            layout.label(text="Selected Node: " + active_node.name)
            # You can add more information about the node here
            layout.label(text="Type: " + active_node.bl_rna.identifier)
            layout.label(text="Location: " + str(active_node.location[0])+','+ str(active_node.location[1]))
            operation=''
            blend_type=''
            hide=''
            if active_node.hide==False:
                hide=', hide=False '
            if hasattr(active_node, 'operation'):
                layout.label(text="Operation: " + active_node.operation)
                operation=', operation='+active_node.operation
            if hasattr(active_node, 'blend_type'):
                layout.label(text="Blend type: " + active_node.blend_type)
                blend_type=', blend_type='+active_node.blend_type
            createCall='create_node(NODETREE,"' + active_node.bl_rna.identifier+'",'+str(tuple(active_node.location))+hide+blend_type+operation+')'
            layout.label(text=createCall)
            # Add a button to copy the create text to clipboard
            layout.operator("node.copy_node_name", text="Copy Node Name").node_name = createCall
        else:
            layout.label(text="No node selected")
            
class NODE_OT_CopyNodeName(bpy.types.Operator):
    bl_idname = "node.copy_node_name"
    bl_label = "Copy Node Definition"
    node_name: bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.window_manager.clipboard = self.node_name
        return {'FINISHED'}

def register():
    bpy.utils.register_class(NODE_PT_InfoPanel)
    bpy.utils.register_class(NODE_OT_CopyNodeName)

def unregister():
    bpy.utils.unregister_class(NODE_PT_InfoPanel)
    bpy.utils.unregister_class(NODE_OT_CopyNodeName)

if __name__ == "__main__":
    register()