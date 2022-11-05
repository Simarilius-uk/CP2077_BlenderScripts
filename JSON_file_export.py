import bpy
import json
from pprint import pprint

#Select an object and then run the script, and it should ask you for a filename then export a json.


def write_some_JSON_data(context, filepath):
    print("running write_some_JSON_data...")
    f = open(filepath, 'w', encoding='utf-8')
    
    C = bpy.context
    objs = C.selected_objects    

    for obj in objs:
        out_dict={}
        coll= obj.users_collection[0]
        out_dict['Id']=1924336415792
        out_dict["NodeIndex"]=coll['nodeIndex']
        out_dict["Position"] = { "$type": "Vector4","W": 0, "X": obj.location[0]*100, "Y": obj.location[1]*100, "Z": obj.location[2]*100}
        out_dict["Orientation"] = { "$type": "Quaternion","W": obj.rotation_quaternion[0], "X": obj.rotation_quaternion[1], "Y": obj.rotation_quaternion[2], "Z": obj.rotation_quaternion[3]}
        out_dict["Scale"] = { "$type": "Vector3", "X": obj.scale[0]*100, "Y": obj.scale[1]*100, "Z": obj.scale[2]*100}
        #cant work out how to get the pivot point out so putting it at the location for now.
        out_dict["Pivot"] = { "$type": "Vector3", "X": obj.location[0]*100, "Y": obj.location[1]*100, "Z": obj.location[2]*100}
        
        min=[0,0,0]
        for b in obj.bound_box:
            if b[0]<min[0]:
                min[0]=b[0]
            if b[1]<min[1]:
                min[1]=b[1]
            if b[2]<min[2]:
                min[2]=b[2]
        max=min
        for b in obj.bound_box:
            if b[0]>max[0]:
                min[0]=b[0]
            if b[1]>max[1]:
                min[1]=b[1]
            if b[2]>max[2]:
                min[2]=b[2]
        Max={ "$type": "Vector4", "W": 0, "X": max[0]*100, "Y": max[1]*100, "Z": max[2]*100  }
        Min={ "$type": "Vector4", "W": 0, "X": min[0]*100, "Y": min[1]*100, "Z": min[2]*100  }
        out_dict["Bounds"] = { "$type": "Box", "Max": Max,"Min": Min}
        out_dict["QuestPrefabRefHash"] = 0
        out_dict["UkHash1"]= 0,
        out_dict["CookedPrefabData"]={ "DepotPath": 0, "Flags": "Default" }
        out_dict["MaxStreamingDistance"]= 99.59849
        out_dict["UkFloat1"]= 66.68195
        out_dict["Uk10"]= 1088
        out_dict["Uk11"]=10370
        out_dict["Uk12"]= 0
        pprint(out_dict)
        json.dump(out_dict,f)
    
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
