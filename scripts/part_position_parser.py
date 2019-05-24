"""
Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in key fields, Discrepancy_Narrative, Work_Center_Event_Narrative, Corrective_Narrative, Component_Position_Number

    Returns:
        Data frame of key fields and Parsed_Component_Position
"""

def engine_reader(df,libraries):
    """ 
        used for work unit codes with QPA=4, 1 per engine
    """

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
#     df['Component_Position_Number'] = df['Component_Position_Number'].astype(int)
#     df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b",str(df.loc[i,checks[j]]))
            
            # replace 'ALL' matches with numbers
            parse = [x.replace('ALL FOUR','1,2,3,4') for x in parse]
            parse = [x.replace('ALL 4','1,2,3,4') for x in parse]
            
            # keep only numeric digits and comma separators
            nums = re.sub("[^\d,]","",str(parse))
            
            # convert string into list of strings
            split = [x for x in nums.split(',')]
            
            # remove empty strings from list
            clean = filter(None, split)
            
            # convert list of strings into list of ints
            ints = map(int, clean)
            
            # remove all values > 4
            trim = [x for x in ints if x<5]
            
            # convert back to string to remove []
            remove = ','.join(map(str, trim))

            # save values into df
            df.loc[i,'Parsed_Component_Position']=remove
            # if empty, check next narrative
            if any(x.isdigit() for x in remove):
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']
    return df


def label_picker(df_one_wuc,wuc_qpa,this_wuc,libraries):
"""
Determines which function to run in order to parse a given set of records. Returns updated dataframe with parsed positions
"""
    pd = libraries["pandas"]

    this_wuc_qpa = wuc_qpa.reset_index(drop=True)
    for i in range(0,len(this_wuc_qpa)):
#         print(this_wuc)
        qpa_i = this_wuc_qpa.loc[i,:]
#         print(qpa_i.MDS)
        # if labels vary by SN, filter to one set at a time
        if qpa_i.Maximum_SN > 0:
            df_thisqpa = df_one_wuc[(df_one_wuc.Serial_Number >= qpa_i.Minimum_SN_Inclusive) & (df_one_wuc.Serial_Number < qpa_i.Maximum_SN) & (df_one_wuc.Equipment_Designator == qpa_i.MDS)]
        else:
            # if MDS is blank, grab both J and H
            if str(qpa_i.MDS)=='nan':
                df_thisqpa = df_one_wuc[(df_one_wuc.Equipment_Designator == 'C130J') | (df_one_wuc.Equipment_Designator == 'C130H')]
            else:
                df_thisqpa = df_one_wuc[df_one_wuc.Equipment_Designator == qpa_i.MDS]
        
        # Select labeling method based on Names from qpa
        if qpa_i.Names=='1':
            df_thisqpa['Parsed_Component_Position'] = '1'
            df_i = df_thisqpa
            
        elif qpa_i.Names=='1,2,3,4':
            df_i = engine_reader(df_thisqpa)  
            
        elif qpa_i.Names=='copilot,nav':
            df_i = cp_navplt(df_thisqpa)    
            
        elif qpa_i.Names=='pilot,copilot,nav':
            df_i = pilot_cp_nav(df_thisqpa)   
            
        elif qpa_i.Names=='pilot,copilot':
            df_i = cp_plt(df_thisqpa)
            
        elif qpa_i.Names=='1,2':
            df_i = INU(df_thisqpa)
            
        elif qpa_i.Names=='pilot_upper,pilot_lower,copilot_upper,copilot_lower':
            df_i = EFI(df_thisqpa)
            
        elif qpa_i.Names=='1A,1B,2A,2B,3A,3B,4A,4B':
            df_i = engine_double(df_thisqpa)
            
        elif qpa_i.Names=='pilot,copilot,aug_crew,aft_center_console,aft_cargo,fwd_cargo,observer':
            df_i = BAD(df_thisqpa)
            
        elif qpa_i.Names=='LH_AUX,RH_AUX,RH_EXT,LH_EXT,1,2,3,4':
            df_i = FQI(df_thisqpa)
    
        else:
            df_i = df_thisqpa
        
        # Add labels to df
        df_one_wuc.update(df_i)
    return df_one_wuc

def fn(conn, libraries, params, predecessors):

    pd = libraries["pandas"]
    re = libraries["re"]

    if len(predecessors) in (2,3):

        if len(predecessors) == 2:
            # KC135, single WUC
            for pred in predecessors:
                if 'compiled' in pred:
                    compiled_table_name = pred
                else:
                    key_table_name = pred
        else:
            # C130, multiple WUCs and complex QPA
            for pred in predecessors:
                if 'compiled' in pred:
                    compiled_table_name = pred
                elif 'qpa' in pred:
                    qpa_table_name = pred
                else:
                    key_table_name = pred
            df_qpa = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(qpa_table_name))

        keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(key_table_name), con=conn).Column_name)
        join_clause = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
        join_clause = ' AND '.join(join_clause)

        df = pd.read_sql(con=conn, sql="""SELECT A.*, B.Work_Unit_Code, B.Discrepancy_Narrative, B.Work_Center_Event_Narrative, 
            B.Corrective_Narrative, B.Component_Position_Number FROM {} A 
            LEFT JOIN {} B ON {}""".format(key_table_name, compiled_table_name, join_clause))

    elif len(predecessors) == 1:
        keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(predecessors[0]), con=conn).Column_name)
        df = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(predecessors[0]))        

    else:
        raise Exception, "Component should have one, two, or three predecessor components"

    df['Parsed_Component_Position'] = ""
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)
    
    # change all provided,empty positions to 0
    df['Component_Position_Number'] = df['Component_Position_Number'].map(lambda x: 0 if not x.isdigit() else x)

    df_qpa.Maximum_SN = df_qpa.Maximum_SN.fillna(0)
    df_qpa.Maximum_SN = df_qpa.Maximum_SN.astype('int64')
    df_qpa.Minimum_SN_Inclusive = df_qpa.Minimum_SN_Inclusive.fillna(0)
    df_qpa.Minimum_SN_Inclusive = df_qpa.Minimum_SN_Inclusive.astype('int64')
    
    # treat all WUCs differently
    for this_wuc in df.Work_Unit_Code.unique():
    
        df_one_wuc = df[df.Work_Unit_Code == this_wuc]
        wuc_qpa = df_qpa[df_qpa.Work_Unit_Code == this_wuc]
        df_one_wuc = label_picker(df_one_wuc,wuc_qpa,this_wuc,libraries)
        df.update(df_one_wuc)
        print('WUC '+ str(this_wuc) + ' complete')

    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)

    # keep only needed columns to save memory
    keys.append('Parsed_Component_Position')
    df = df[keys]

    return df
