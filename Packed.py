'''
Descripttion: Pack the DICOM file into a tar.gz file.
version: 1.0
Author: SANGF
Date: 2020-10-04 16:15:49
LastEditors: SANGF
LastEditTime: 2020-10-09 18:17:06
'''
import os
import re
import tarfile
import shutil
import logging

def tar(file_path, out_file):
    # tar the file into a .tar.gz file.
    logging.info(f'Pack {file_path}...')

    tar = tarfile.open(out_file, 'w:gz')
    for a, _, c in os.walk(file_path):
        for i in c:
            tar.add(os.path.join(a, i), arcname=i)
    tar.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    src = 'Test_Pack/DTI'
    for i in os.listdir(src):
        logging.info(f'{i}...')
        in_path = os.path.join(src, i)
        if re.search(r'\.tar.gz', in_path):
            continue
        out_path = os.path.join(src, f'{i}.tar.gz')
        tar(in_path, out_path)
        shutil.rmtree(in_path)