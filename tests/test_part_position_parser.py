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
    df_input = pd.read_csv('./resources/input/ppp.csv')
    df_output = pd.read_csv('./resources/output/ppp_out.csv',dtype={'Component_Position_Number':'str','Parsed_Component_Position':'str'})
    df_qpa = pd.read_csv('../data/wuc_list_qpa_translated_simplified.csv',dtype={'Names':'str'})
    df_qpa.Alternate_WUC = df_qpa.Alternate_WUC.astype(str)

    df_input.loc[:,'Parsed_Component_Position'] = ""
    df_input.loc[:,'Parsed_Component_Position'] = df_input.loc[:,'Parsed_Component_Position'].astype(str)
    df_input.loc[:,'Component_Position_Number'] = df_input.loc[:,'Component_Position_Number'].map(lambda x: '0' if x=='nan' else x)
    df_input.loc[:,'Component_Position_Number'] = df_input.loc[:,'Component_Position_Number'].fillna(0.0).astype('int64').astype(str)  # no awful 0.0 strings
    df_output.loc[:,'Component_Position_Number'] = df_output.loc[:,'Component_Position_Number'].fillna(0.0).astype('int64').astype(str)  # no awful 0.0 strings
    
    df_qpa.Maximum_SN = df_qpa.Maximum_SN.fillna(0)
    df_qpa.Minimum_SN_Inclusive = df_qpa.Minimum_SN_Inclusive.fillna(0)

    # treat all WUCs differently
    for this_wuc in df_input.Work_Unit_Code.unique():
    
        df_one_wuc = df_input[df_input.Work_Unit_Code == this_wuc]
        wuc_qpa = df_qpa[(df_qpa.Work_Unit_Code == this_wuc) | [this_wuc in df_qpa.loc[x,'Alternate_WUC'] for x in range(0,len(df_qpa))]]
        df_one_wuc = label_picker(df_one_wuc,wuc_qpa,this_wuc,libraries)
        df_input.update(df_one_wuc)

    df_input.loc[:,'Parsed_Component_Position'] = df_input.loc[:,'Parsed_Component_Position'].astype(str)
    df_input.Serial_Number = df_input.Serial_Number.astype('int64') 
    df_input.loc[:,'Parsed_Component_Position'] = df_input.loc[:,'Parsed_Component_Position'].map(lambda x: '0' if x=='nan' else x)
    df_input.loc[:,'Component_Position_Number'] = df_input.loc[:,'Component_Position_Number'].map(lambda x: '0' if x=='nan' else x)
    df_output.Component_Position_Number = df_output.Component_Position_Number.astype(str)
    df_output.Parsed_Component_Position = df_output.Parsed_Component_Position.astype(str)

    pd.testing.assert_frame_equal(df_input,df_output)