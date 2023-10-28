import bpy
C=bpy.context
obj=C.selected_objects[0]
if obj.type=='CURVE':
    spline=obj.data.splines[0]
    bzps=spline.bezier_points
    print('"points": [')
    for point in bzps:
        print('  {\n   "$type": "SplinePoint",\n   "automaticTangents": 1,\n   "continuousTangents": 1,\n   "id": 0,\n   "position": {\n\t "$type": "Vector3",')
        print('\t "X":'+str(point.co[0])+',')
        print('\t "Y":'+str(point.co[1])+',')
        print('\t "Z":'+str(point.co[2])+',')
        print('\t },\n   "rotation": {\n\t "$type": "Quaternion",\n\t "i": 0,\n\t "j": 0,\n\t "k": 0,\n\t "r": 1\n },\n "tangents": {\n   "Elements": [\n\t{ \n\t "$type": "Vector3",')
        print('\t "X":'+str(point.handle_right[0])+',')
        print('\t "Y":'+str(point.handle_right[1])+',')
        print('\t "Z":'+str(point.handle_right[2])+',')             
        print('\t\t},\n\t {   \n\t "$type": "Vector3", ')
        print('\t "X":'+str(point.handle_left[0])+',')
        print('\t "Y":'+str(point.handle_left[1])+',')
        print('\t "Z":'+str(point.handle_left[2])+',')     
        print('\t}\n   ]\n  }\n},')
    print(']')
