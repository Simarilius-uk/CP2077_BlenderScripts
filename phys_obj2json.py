# Created by Boe6 for Vehicle Modding Guide
# See full guide for detailed instructions
# https://docs.google.com/document/d/1a5Xvviw_GQxcvbxEwc3GoboaNk0igxlhiyS7ux34sIs/edit?usp=sharingimport os

import os
import json

submeshCount = 6
# edit as needed. 0-5_submesh = 6

outputJsonPath = 'boe6_mini_cooper_interaction_collider.phys_EDIT.json'
# edit as needed.
#     Don't overwrite the original json, just in case you need to revert

originalJson = 'boe6_mini_cooper_interaction_collider.phys.json'
# edit as needed. Used to copy json formatting into output.

submeshPaths = [
                'submesh_0_None-edit.obj',
                'submesh_1_None-edit.obj',
                'submesh_2_None-edit.obj',
                'submesh_3_None-edit.obj',
                'submesh_4_None-edit.obj',
                'submesh_5_chassis_bottom-edit.obj'
                ]
# edit with your submesh .obj files.


def fileRefresh(path):
    if os.path.exists(path): # check for existing file
        os.remove(path)
        open(path, 'w')

def newObjLine(txt, path):
    with open(path, 'a') as obj:
        obj.write(txt + '\n')

def newObjLineNoBreak(txt, path):
    with open(path, 'a') as obj:
        obj.write(txt)

def file_len(filename):
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

def copyLines(first,last):
    for i in range(first,last+1):
        originalLine = originalFileLines[i-1]
        newObjLineNoBreak(originalLine, outputJsonPath)


# ==== LOGIC ====


#reset output file
fileRefresh(outputJsonPath)


originalFile = open(originalJson)
originalFileLines = originalFile.readlines()

num_lines = file_len(originalJson)
print('STARTED. Source file line count: ' + str(num_lines))

jsonData = json.load(open(originalJson))


# initial json lines. header, data start
copyLines(1,56) # Likely to break in the future. use reference guide.



# actual xyz data entry
for submeshObj in submeshPaths:
    submeshNumber = int(submeshObj[8])+1 # breaks with double digit submesh count
    # submesh names / collisionShapes tags
    submeshTag = ( submeshObj[:-9] )[10:]
    newObjLine('                    \"$value\": \"' +
               submeshTag + '\"', outputJsonPath)

    copyLines(58,60)

    verticesCount = file_len(submeshObj) - 4

    objFile = open(submeshObj)
    objLines = objFile.readlines()

    # xyz entry
    lineCount = 0
    for line in objLines:
        lineCount += 1
        if line[0] == 'v':
            nums = line.split(' ')
            
            x = nums[1]
            y = nums[2]
            z = nums[3]

            newObjLine('                      \"$type\": \"Vector3\",',
                       outputJsonPath)
            newObjLine('                      \"X\": ' + x + ',',
                       outputJsonPath)
            newObjLine('                      \"Y\": ' + y + ',',
                       outputJsonPath)
            newObjLineNoBreak('                      \"Z\": ' + z,
                       outputJsonPath)

            # if not last vertice
            if not lineCount == file_len(submeshObj):
                copyLines(65,66)

    # if not last submesh
    if not submeshObj == submeshPaths[-1]:
        copyLines(251,256)

        newObjLine('                \"HandleId\": \"' + str(submeshNumber+1) + '\",',
                   outputJsonPath)
        
        copyLines(23,41)

        collisionShapes = jsonData['Data']['RootChunk']['bodies'][0]['Data']['collisionShapes']
        local2body = collisionShapes[submeshNumber]['Data']['localToBody']

        # localToBody position data. (preserves submesh transformation)
        x = local2body['position']['X']
        y = local2body['position']['Y']
        z = local2body['position']['Z']

        newObjLine('                      \"X\": ' + str(0) + ',',
                       outputJsonPath)
        newObjLine('                      \"Y\": ' + str(0) + ',',
                       outputJsonPath)
        newObjLine('                      \"Z\": ' + str(0),
                       outputJsonPath)

        copyLines(45,56)
    
# finish lines
copyLines(1330,1424)

print("FINISHED. Result fileline count out: " + str(file_len(outputJsonPath)))















