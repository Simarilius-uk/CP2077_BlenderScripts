# Created by Boe6 for Vehicle Modding Guide
# See full guide for detailed instructions
# https://docs.google.com/document/d/1a5Xvviw_GQxcvbxEwc3GoboaNk0igxlhiyS7ux34sIs/edit?usp=sharing

import json
import os

physJsonPath = 'boe6_mini_cooper_interaction_collider-edit.phys.json' # set custom

physObjPath = ( physJsonPath[:-5] + '.obj' )

physMtlPath = ( physJsonPath[:-5] + '.mtl' )

phys = open(physJsonPath)

data = json.load(phys)

x = 0

def fileRefresh(path):
    if os.path.exists(path): # check for existing file
        os.remove(path) # delete it if it exists

def newObjLine(txt, path):
    with open(path, 'a') as obj:
        obj.write(txt + '\n')




fileRefresh(physMtlPath)
with open(physMtlPath, 'a') as obj:
    obj.write('# Created with boe6 json2obj script')


for i in data['Data']['RootChunk']['bodies'][0]['Data']['collisionShapes']:
    #iterates through the collisionShapes array. runs once for each submesh
    
    submeshNum = int(i['HandleId']) -1
    submeshName = 'submesh_' + str(submeshNum) + '_' + i['Data']['tag']['$value']
    submeshPath = submeshName + '.obj'

    #print('== submesh '+ submeshName + ' ==')
    
    fileRefresh(submeshPath)

    #.obj headers
    newObjLine('# Created with boe6 json2obj script', submeshPath)
    newObjLine('# https://wiki.redmodding.org/wolvenkit/readme', submeshPath)
    newObjLine('mtllib ' + physMtlPath, submeshPath)

    #.obj submesh name
    newObjLine('o submesh_' + str(submeshNum) + '_' +
               i['Data']['tag']['$value'], submeshPath)
    
    #.obj vertices
    vertCount = 0
    for j in i['Data']['vertices']:
        vertCount += 1
        
        x = j['X']
        y = j['Y']
        z = j['Z']

        newObjLine('v ' + str(x) + ' ' + str(y) + " " + str(z), submeshPath)
        

    #print(vertCount)

print('\n=== COMPLETE ===\n')



phys.close()
