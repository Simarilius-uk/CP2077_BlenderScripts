# Script to repath a mesh file
# Simarilius Jan 2023
#

from dataclasses import replace
import os
import json
import glob

def replace_mis(node):
    if type(node) is dict:
        print("is dict")
        for k in node.keys():
            print(k)
            if k=='DepotPath' and node['DepotPath'] in old_mis:
                print("Replacing ",node[k]," with ", new_mis[old_mis.index(node['DepotPath'])])
                node['DepotPath']=new_mis[old_mis.index(node['DepotPath'])]
            if type( node[k]) is dict:               
                print(k, "is dict")
                replace_mis(node[k])
            if type( node[k]) is list:               
                print(k, "is list")
                replace_mis(node[k])
    if type(node) is list:
        print("is list")
        for li in node:
            print(li)
            if type(li) is dict:
                print(li, "is dict")
                replace_mis(li)



project_path='F:\\cpmod\\ids_irezumi_tattoos\\source\\raw\\'
outpath=

old_mis=['base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_01_ca_pale.mi']

new_mis=['island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_01_ca_pale.mi']


jsons= glob.glob(project_path+"\**\*.mesh.json", recursive = True)

for filepath in jsons:
    with open(filepath,'r') as f: 
            j=json.load(f) 
    meshName=os.path.basename(filepath)[:-5]
    nodes=j['Data']['RootChunk']
    replace_mis(nodes)


    with open(filepath, 'w') as outfile:
        json.dump(j, outfile,indent=2)