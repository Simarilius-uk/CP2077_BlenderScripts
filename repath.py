# Script to repath a mesh file
# Simarilius Jan 2023
# ______                 _   _                           _   _      
# | ___ \               | | | |                         | | (_)     
# | |_/ /___ _ __   __ _| |_| |__   ___  _ __ ___   __ _| |_ _  ___ 
# |    // _ \ '_ \ / _` | __| '_ \ / _ \| '_ ` _ \ / _` | __| |/ __|
# | |\ \  __/ |_) | (_| | |_| | | | (_) | | | | | | (_| | |_| | (__ 
# \_| \_\___| .__/ \__,_|\__|_| |_|\___/|_| |_| |_|\__,_|\__|_|\___|
#           | |                                                     
#           |_|                                                    
#
# To use fill in the old_mi and new_mi lists with matching pairs of old and new mi names, and export the meshes that need modifying to json in wkit.
# Set the project path variable below to your project then run the script.
# Will change all instances of the old mi to the mi with the same index in the new list (so 2nd for 2nd etc)
# Will save over the original json
# 

from dataclasses import replace
import os
import json
import glob

def replace_mis(node):
    if type(node) is dict:
        #print("is dict")
        for k in node.keys():
            #print(k)
            if k=='DepotPath' and node['DepotPath'] in old_mis:
                print("Replacing ",node[k]," with ", new_mis[old_mis.index(node['DepotPath'])])
                node['DepotPath']=new_mis[old_mis.index(node['DepotPath'])]
            if type( node[k]) is dict:               
                #print(k, "is dict")
                replace_mis(node[k])
            if type( node[k]) is list:               
                #print(k, "is list")
                replace_mis(node[k])
    if type(node) is list:
        #print("is list")
        for li in node:
            #print(li)
            if type(li) is dict:
                #print(li, "is dict")
                replace_mis(li)



project_path='F:\\cpmod\\ids_irezumi_tattoos\\source\\raw\\'


old_mis=['base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_01_ca_pale_00_warm_ivory.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_02_ca_limestone.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_02_ca_limestone_00_beige.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_03_ca_senna.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_03_ca_senna_00_amber.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_03_ca_senna_01_honey.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_03_ca_senna_02_band.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_04_ca_almond.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_04_ca_almond_00_umber.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_05_bl_espresso.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_06_bl_dark.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_01_pale_dirt.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_02_black_dirt.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_03_limestone_sick.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_04_almond_sick.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_05_senna_valentino.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_05_senna_valentino_01.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_06_limestone_tyger.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_dead_01.mi',
'base\\characters\\common\\skin\\character_mat_instance\\female\\body\\female_npc_dead_02.mi']

new_mis=['island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_01_ca_pale_00_warm_ivory.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_02_ca_limestone.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_02_ca_limestone_00_beige.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_03_ca_senna.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_03_ca_senna_00_amber.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_03_ca_senna_01_honey.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_03_ca_senna_02_band.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_04_ca_almond.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_04_ca_almond_00_umber.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_05_bl_espresso.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_06_bl_dark.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_01_pale_dirt.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_02_black_dirt.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_03_limestone_sick.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_04_almond_sick.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_05_senna_valentino.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_05_senna_valentino_01.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_06_limestone_tyger.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_dead_01.mi',
'island_dancer\\custom\\skin\\body\\woman_average\\parameters\\custom\\female_npc_dead_02.mi']


jsons= glob.glob(project_path+"\**\*.mesh.json", recursive = True)

for filepath in jsons:
    with open(filepath,'r') as f: 
            j=json.load(f) 
    meshName=os.path.basename(filepath)[:-5]
    nodes=j['Data']['RootChunk']
    replace_mis(nodes)


    with open(filepath, 'w') as outfile:
        json.dump(j, outfile,indent=2)