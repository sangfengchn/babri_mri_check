'''
Descripttion: Preprocessing raw data downloaded from MRI server to make it more easy to use.
version: 2.0
Author: SANGF
Date: 2020-09-30 21:18:41
LastEditors: SANGF
LastEditTime: 2021-08-29 11:15:51
'''
import os
from os.path import join as opj
import re
import tarfile
import gzip
import time
import shutil
import pydicom
import numpy as np
import pandas as pd
from pypinyin import pinyin, Style
import logging
import datetime
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

def fun_Convert2Pinyin(tmp_name):
    # convert chinese name to pinyin name.
    tmp_py_list = pinyin(tmp_name, heteronym=True, style=Style.NORMAL)
    multi_pinyin = []
    for item in tmp_py_list:
        if len(multi_pinyin) == 0:
            tmp_list = []
            for tmp in item:
                tmp_list.append(tmp)
            multi_pinyin.append(tmp_list)
        else:
            tmp_list = []
            for tmpa in multi_pinyin[-1]:
                for tmp in item:
                    tmp_list.append('{}{}'.format(tmpa, tmp))
            multi_pinyin.append(tmp_list)
    return multi_pinyin[-1]

def fun_untar(file_path, out_root):
    # unpack .tar.gz file.
    logging.info(f'In fun_untar: {file_path}')
    
    file_name = os.path.split(file_path)[-1]
    file = file_name.replace('.tar.gz', '')
    out_path = opj(out_root, file)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    tar = tarfile.open(file_path, 'r:gz')
    for sub in tar.getnames():
        tar.extract(sub, out_path)
    tar.close()

    # move file into out_path, and remove other dir in out_path
    for a, _, c in os.walk(out_path):
        if a == out_path:
            continue
        for i in c:
            tmp_path = opj(a, i)
            shutil.move(tmp_path, out_path)
        os.removedirs(a)

    # unpacked floder path
    return out_path


def fun_sorted(file_path):
    # sorted the dicom files into different series.
    logging.info(f'In fun_sorted: {file_path}')

    # file_name = os.path.split(file_path)[-1]
    for i in os.listdir(file_path):
        dcm_file = opj(file_path, i)
        ds = pydicom.dcmread(dcm_file)
        # series name
        series_name = ds[0x0018, 0x1030].value
        series_name = series_name.replace('.', '_')
        # series id
        series_id = ds[0x0020, 0x0011].value
        # out_path is a series path.
        out_path = opj(file_path, f'{int(series_id):04d}_{series_name}')
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        shutil.move(opj(file_path, i), out_path)


def fun_tar(file_path, out_file):
    # tar the file into a .tar.gz file.
    logging.info(f'In fun_tar: {file_path}')

    tar = tarfile.open(out_file, 'w:gz')
    for a, _, c in os.walk(file_path):
        for i in c:
            tar.add(opj(a, i), arcname=i)
    tar.close()


def fun_move(file_path, out_root, machine='OLD'):
    # move series floder to floder same as backup data.
    logging.info(f'In fun_move: {file_path} into {out_root}')

    file_name = os.path.split(file_path)[-1]
    
    squences = {
            'ge_func_31x31x35_240_RS': "REST",
            'ge_func_3x3x3p5_303': "EM",
            'ge_func_3x3x3p5_235': "NBACK",
            't1_mprage_sag_tr1900': "T1",
            't2_tirm_tra_dark-fluid-p2_new': "FLAIR",
            'DTI_30_2x2x2_128x128_b1000_p2': "DTI",
            't2_tse_tra_320_p2': "T2",
            'ge_func_3x3x3p5_360': "LANT"
            }
    if machine == 'OLD':
        pass
    else:
        squences = {
            't1_mprage_sag_1x1x1_p2_20ch': "T1",
            'bold_64x64_s2_3x3x3p5_tr1000_fa70': "REST",
            'bold_80x80_s2_2.5iso_tr2000': "REST",
            'DTI_BP_64_2x2x2_s2_p2_6-8': "DTI",
            'field_mapping_2x2x2_for_DTI': "DTI",
            'AAHead_Scout': "AAHead_Scout",
            't2_blade_tra_p2': "T2WI",
            't1_tirm_tra_dark-fluid_p2': "FLAIR",
            't2_tirm_tra_dark-fluid': "FLAIR",
            't2_blade_sag': "T2WI",
            'HighResHippocampus': "HIPPO",
            'TOF_3D_multi-slab': "TOF",
            'Sagittal 3D FLAIR': "3D-FLAIR",
            'ASL_3D_tra_iso': "ASL"
        }

    for i in os.listdir(file_path):
        series_name = i[5:]
        if series_name in squences.keys():
            tmp_src_path = opj(file_path, i)
            tmp_dst_path = opj(out_root, squences[series_name], file_name)
            if not os.path.exists(tmp_dst_path):
                os.makedirs(tmp_dst_path)
            for j in os.listdir(tmp_src_path): 
                shutil.copy(opj(tmp_src_path, j), opj(tmp_dst_path, j))
    shutil.rmtree(file_path)

    for _, v in squences.items():
        floder_path = opj(out_root, v, file_name)
        if os.path.exists(floder_path):
            # pack file to save space of disk.
            if os.path.exists(f'{floder_path}.tar.gz'):
                os.remove(f'{floder_path}.tar.gz')
            fun_tar(floder_path, f'{floder_path}.tar.gz')
            shutil.rmtree(floder_path)

    # return packed file path.
    return file_name


def fun_GetIndex(df, date, name):
    # to find the id of mri file in subject information table.
    # logging.info(f'Searching the index of {date}-{name}...')

    res = None
    target = f'{date}{name}'
    for i in df.index.values:
        # if df.loc[i, 'CheckDateName']=='yes':
        #     continue
        tmp_date = df.loc[i, '时间']
        tmp_name = df.loc[i, '姓名']
        for tmp_name_pinyin in fun_Convert2Pinyin(tmp_name):
            current = f'{int(tmp_date)}{tmp_name_pinyin}'.upper()
            if current == target:
                res = [i, tmp_date, tmp_name_pinyin.upper()]
                break
        if res:
            break
    # return id, date, and pinyin name.
    return res


if __name__ == "__main__":
    
    # save results
    proj = os.path.abspath('.')
    src = opj(proj, 'Old_Raw')
    tmp = opj(proj, 'Old_ResTmp') 
    dst = opj(proj, 'Old_Res')
    check = opj(proj, 'Old_CheckRes')
    table_file = '师大核磁人员情况新_20230716.xls'

    # subject information file
    oldDf = pd.read_excel(opj('0.List', table_file), sheet_name='Sheet1', header=0)
    oldDf['CheckDateName'] = ['no']*len(oldDf)

    for i in os.listdir(src):
        logging.info(f'\n\n{i}')
        # split date and name from file name.
        tmp_file_name = i.replace('.tar.gz', '')
        date = tmp_file_name.split('_')[0]
        name = tmp_file_name.split('_')[-1].upper()
        if re.search(r'\d', name):
            name = re.sub(r'\d*', '', name)
            
        res_index = fun_GetIndex(oldDf, date, name)
        if not res_index:
            # save image file in log, because it is not in subject file.
            logging.warning(f'Not in list: {i}')
            continue

        index = res_index[0]
        date = res_index[1]
        name_pinyin = res_index[2]

        # the image is in subject file, and record the checked yes in CheckDateName.
        oldDf.loc[index, 'CheckDateName'] = 'yes'
        new_file_name = f'{int(oldDf.loc[index, "序号"])}{name_pinyin}'.upper()

        # untar
        sub_path = fun_untar(opj(src, i), tmp)
        time.sleep(1)

        # rename
        new_path = opj(tmp, f'{new_file_name}')
        os.rename(sub_path, new_path)
        time.sleep(1)

        # sorted
        fun_sorted(new_path)
        time.sleep(1)

        # move & tar
        
        tar_name = fun_move(new_path, dst)
        time.sleep(1)

        # Check series 
        # for T1
        res_check_series = 'yes'
        res_check_series_a = ''
        status_list = oldDf.loc[index, '结构']
        status_file = opj(dst, 'T1', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'T1;'
        # for rest
        status_list = oldDf.loc[index, '静息态']
        status_file = opj(dst, 'REST', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'REST;'
        # for em
        status_list = oldDf.loc[index, '情景记忆']
        status_file = opj(dst, 'EM', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'EM;'
        # for wm
        status_list = oldDf.loc[index, '工作记忆']
        status_file = opj(dst, 'NBACK', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'NBACK;'
        # for dti
        status_list = oldDf.loc[index, 'DTI']
        status_file = opj(dst, 'DTI', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'DTI;'
        # for flair
        status_list = oldDf.loc[index, 'flair']
        status_file = opj(dst, 'FLAIR', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'FLAIR;'
        # for clinical
        status_list = oldDf.loc[index, '临床']
        status_file = opj(dst, 'T2', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'T2;'
        # for LANT
        status_list = oldDf.loc[index, '失独老人任务']
        status_file = opj(dst, 'LANT', f'{tar_name}.tar.gz')
        if (status_list == '√') and (not os.path.exists(status_file)):
            res_check_series = 'no'
            res_check_series_a += 'LANT;'
        oldDf.loc[index, 'CheckSeries'] = res_check_series
        oldDf.loc[index, 'CheckSeries_A'] = res_check_series_a

        # delete the correct data.
        if res_check_series == 'yes':
            os.remove(opj(src, i))

    # to save check result file.
    now_date = datetime.datetime.now().strftime('%Y%m%d')
    oldDf.to_excel(opj(check, f'Checked_{now_date}_{table_file.replace(".xls", ".xlsx")}'))
    logging.info("Done.")