'''
Descripttion: 
version: 
Author: SANGF
Date: 2021-01-25 17:15:13
LastEditors: SANGF
LastEditTime: 2021-06-03 15:25:29
'''
# import pandas as pd

# all_df = pd.read_excel('0.List\师大核磁人员情况新_20210118(1).xls', sheet_name='旧机器', header=0, index_col=0)
# had_df = pd.read_csv('0.List\subjects.csv', index_col=0, header=0)
# for i in all_df.index.values:
#     if i in had_df.index.values:
#         all_df.loc[i, 'HadDTI'] = 'Yes'
# all_df.to_excel('0.List\旧机器_withDTI.xlsx')

import pydicom

img = pydicom.dcmread(r'New_Raw\20210528_P01_ZHANGZJ_DXW_CHENQINGREN\20210528_P01_ZhangZJ_DXW_ChenQingRen\0002_t1_mprage_sag_1x1x1_p2_20ch\20210528_P01_ZHANGZJ_DXW_CHENQINGREN.MR.BNU_P2018_20CH_ZHANG_ZHANJUN.0002.0004.2021.05.28.10.31.28.49328.546466949.IMA')
print(img)