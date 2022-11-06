import bpy
import json
from pprint import pprint

#Select an object and then run the script, and it should ask you for a filename then export a json.
#
#[{
#"app":"",
#"path":"base\\quest\\main_quests\\part1\\q115\\entities\\q115_netrunners_chair.ent",
#"rot":{"pitch":-0,"yaw":169.99043273926,"roll":0},
#"pos":{"x":1486.6485595703,"y":-1404.9145507813,"z":51.299728393555,"w":1}}]
#
#
#

def write_some_JSON_data(context, filepath):
    print("running write_some_JSON_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("[")
    C = bpy.context
    objs = C.selected_objects    

    for obj in objs:
        out_dict={}
        coll= obj.users_collection[0]
        out_dict["app"]=""
        out_dict["path"]=coll['mesh']
        out_dict["pos"] = { "w": 0, "x": obj.location[0]*100, "y": obj.location[1]*100, "z": obj.location[2]*100}
        out_dict["rot"] = {  "pitch": obj.rotation_euler.y, "roll": obj.rotation_euler.x, "yaw": obj.rotation_euler.z}
        pprint(out_dict)
        json.dump(out_dict,f )
    f.write("]")
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeJSONData(Operator, ExportHelper):
    """Export Cyberpunk JSON Data for selected objects"""
    bl_idname = "export_test.some_json_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Cyberpunk JSON Data for selected objects"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )


    def execute(self, context):
        return write_some_JSON_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeJSONData.bl_idname, text="Cyberpunk JSON Export Operator")


# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access).
def register():
    bpy.utils.register_class(ExportSomeJSONData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeJSONData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_json_data('INVOKE_DEFAULT')
