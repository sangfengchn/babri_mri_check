'''
Descripttion: Selecting and copying data.
version: 
Author: SANGF
Date: 2020-10-15 12:09:32
LastEditors: SANGF
LastEditTime: 2020-10-15 14:49:36
'''
import os
import re
import shutil
from tqdm import tqdm
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    src = 'Test'
    dst = 'dst'
    id_path = 'id.txt'
    
    # get id-path map
    logging.info('Get id-path map.')
    id_map = {}
    for i in os.listdir(src):
        file_name = i.replace('.tar.gz', '')
        # top 5 letter as index.
        id = file_name[0:5]
        if id not in id_map.keys():
            id_map[id] = [i]
        else:
            id_map[id].append(i)
        
    # get id list
    logging.info('Get id list.')
    ids = []
    with open(id_path, 'r') as f:
        lines = f.readlines()
    for i in lines:
        tmp_i = re.sub(r'\s', '', i)
        if tmp_i:
            ids.append(tmp_i)
    
    # copy
    logging.info('Copying.')
    for i in tqdm(range(len(ids))):
        tmp_id = ids[i]
        if tmp_id in id_map.keys():
            for j in id_map[tmp_id]:
                tmp_src_path = os.path.join(src, j)
                tmp_dst_path = os.path.join(dst, j)
                shutil.copy(tmp_src_path, tmp_dst_path)

    logging.info('Done.')