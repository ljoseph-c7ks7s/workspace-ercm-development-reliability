import os
import sys
import pandas as pd
import re

# import modules for testing
from scripts.part_position_parser import engine_reader,cp_navplt,cp_plt,pilot_cp_nav,INU,EFI,engine_double,BAD,FQI,label_picker

# create libraries dict in studio fashion
libraries = {'pandas': pd,'re': re}

def test_part_position_parser():
    pd = libraries['pandas']
    re = libraries['re']

    # import data for testing
    df_input = pd.read_csv('./resources/input/ppp.csv',dtype={'Component_Position_Number':'str'})
    df_output = pd.read_csv('./resources/output/ppp_out.csv',dtype={'Component_Position_Number':'str','Parsed_Component_Position':'str'})
    df_qpa = pd.read_csv('../data/wuc_list_qpa_translated_simplified.csv',dtype={'Names':'str'})
    df_qpa.Alternate_WUC = df_qpa.Alternate_WUC.astype(str)

    df_input['Parsed_Component_Position'] = ""
    df_input.Serial_Number = df_input.Serial_Number.astype('int64')
    df_input.Component_Position_Number = df_input.Component_Position_Number.astype(str)
    df_output.Component_Position_Number = df_output.Component_Position_Number.astype(str)
    df_input.Parsed_Component_Position = df_input.Parsed_Component_Position.astype(str)
    df_output.Parsed_Component_Position = df_output.Parsed_Component_Position.astype(str)
    df_input.loc[:,'Component_Position_Number'] = df_input.loc[:,'Component_Position_Number'].map(lambda x: '0' if x=='nan' else x)
    df_qpa.Alternate_WUC = df_qpa.Alternate_WUC.astype(str)

    for this_wuc in df_input.Work_Unit_Code.unique():
        
        df_one_wuc = df_input.loc[df_input.Work_Unit_Code == this_wuc]
        wuc_qpa = df_qpa[(df_qpa.Work_Unit_Code == this_wuc) | [this_wuc in df_qpa.loc[x,'Alternate_WUC'] for x in range(0,len(df_qpa))]]
    #     wuc_qpa.Maximum_SN = wuc_qpa.Maximum_SN.astype('int64')
    #     wuc_qpa.Minimum_SN_Inclusive = wuc_qpa.Minimum_SN_Inclusive.astype('int64')
        df_one_wuc = label_picker(df_one_wuc.copy(),wuc_qpa,this_wuc,libraries)
        df_input.update(df_one_wuc)

    df_input.Serial_Number = df_input.Serial_Number.astype('int64') 
    df_input.loc[:, 'Parsed_Component_Position'] = df_input['Parsed_Component_Position'].astype(str)
    df_input.loc[:, 'Parsed_Component_Position'] = df_input['Parsed_Component_Position'].map(lambda x: '0' if x == 'nan' else x)
    df_input.loc[:, 'Parsed_Component_Position'] = df_input['Parsed_Component_Position'].map(lambda x: '0' if x == '' else x)

    # split the dataframes in order to improve debug process
    input1 = df_input.head(60)
    input2 = df_input.tail(60)
    output1 = df_output.head(60)
    output2 = df_output.tail(60)
    pd.testing.assert_frame_equal(input1,output1)
    pd.testing.assert_frame_equal(input2,output2)
