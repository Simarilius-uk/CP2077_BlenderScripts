bl_info = {
    "name": "Selected Meshes Panel",
    "author": "Simarilius",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool",
    "description": "Displays a panel with a list of selected mesh objects",
    "category": "Object",
}

import bpy


# Define the panel class
class OBJECT_PT_SelectedMeshesPanel(bpy.types.Panel):
    bl_label = "Selected Meshes"
    bl_idname = "OBJECT_PT_selected_meshes_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    # Panel UI layout
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Retrieve selected mesh objects
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

        # Display the list of selected mesh objects
        for obj in selected_objects:
            layout.label(text=obj.name)

        # Add copy button
        layout.operator("object.copy_selected_meshes")


# Operator to copy selected mesh names to clipboard
class OBJECT_OT_CopySelectedMeshes(bpy.types.Operator):
    bl_idname = "object.copy_selected_meshes"
    bl_label = "Copy Mesh Names"
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # Retrieve selected mesh object names
        selected_objects = [obj.name for obj in bpy.context.selected_objects if obj.type == 'MESH']
        mesh_names = '\n'.join(selected_objects)

        # Copy names to clipboard
        bpy.context.window_manager.clipboard = mesh_names

        self.report({'INFO'}, "Mesh names copied to clipboard")
        return {'FINISHED'}


# Register the addon
def register():
    bpy.utils.register_class(OBJECT_PT_SelectedMeshesPanel)
    bpy.utils.register_class(OBJECT_OT_CopySelectedMeshes)


# Unregister the addon
def unregister():
    bpy.utils.unregister_class(OBJECT_PT_SelectedMeshesPanel)
    bpy.utils.unregister_class(OBJECT_OT_CopySelectedMeshes)


# Enable running the script directly from Blender's Text Editor
if __name__ == "__main__":
    register()
