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
            
            # remove all values > 4, duplicates and sort
            trim = [x for x in ints if x<5]
            trim = list(set(trim))
            trim.sort()
            
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
        if df.loc[i,'Parsed_Component_Position'].isna():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']
    return df


def cp_navplt(df,libraries):
    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub("[^\w,]","",str(parse))

            # correct parsed labels
            parse = parse.replace('CPLT','CP')
            parse = parse.replace('CPT','CP')
            parse = parse.replace('CPILOT','CP')
            parse = parse.replace('COPILOT','CP')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            parse = parse.replace('PILOT','NAV')
            parse = parse.replace('CP','COPILOT')
            
            # remove duplicates and sort
            parse = parse.split(',')
            parse = list(set(parse))
            parse.sort()
            
            # convert back to string to remove []
            parse = ','.join(map(str, parse))

            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'].isna():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def cp_plt(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(int)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("C?O?\W?PI?L?O?T|C\W?P",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub("[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CP','COPILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            
            # remove duplicates and sort
            parse = parse.split(',')
            parse = list(set(parse))
            parse.sort()
            
            # convert back to string to remove []
            parse = ','.join(map(str, parse))

            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'].isna():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def pilot_cp_nav(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']
    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub("[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')
            parse = parse.replace('CP','COPILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            
            # remove duplicates and sort
            parse = parse.split(',')
            parse = list(set(parse))
            parse.sort()
            
            # convert back to string to remove []
            parse = ','.join(map(str, parse))
            
            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'].isna():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def INU(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            
            parse = re.findall("\#\d+|\# \d+|NO. \d+|NUMBER \d+|1 AND 2|1 \& 2|\#!",str(df.loc[i,checks[j]]))
            
            # replace 'ALL' matches with numbers
            parse = [x.replace('1 AND 2','1,2') for x in parse]
            parse = [x.replace('1 & 2','1,2') for x in parse]
            parse = [x.replace('#!','1') for x in parse]
            
            # keep only numeric digits and comma separators
            nums = re.sub("[^\d,]","",str(parse))
            
            # convert string into list of strings
            split = [x for x in nums.split(',')]
            
            # remove empty strings from list
            clean = filter(None, split)
            
            # convert list of strings into list of ints
            ints = map(int, clean)
            
            # remove all values > 2, duplicates and sort
            trim = [x for x in ints if x<3]
            trim = list(set(trim))
            trim.sort()
            
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


def EFI(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            if re.findall("COPILOT\'S EFI \(TOP\)",df.loc[i,checks[j]])==["COPILOT'S EFI (TOP)"]:
                parse='COPILOT_UPPER'
                
            else:
                parse = re.findall("(?:UPP?E?R|LO?WE?R|TOP|BOTTOM)? ?C?O?\W?PI?L?O?T\'?S? (?:UPP?E?R|LO?WE?R|TOP|BOTTOM)?|(?:UPP?E?R|LO?WE?R|TOP|BOTTOM)? ?C\W?P\'?S? (?:UPP?E?R|LO?WE?R|TOP|BOTTOM)?",str(df.loc[i,checks[j]]))

                # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
                parse = re.sub("[^\w,]","",str(parse))

                parse = parse.replace('S','')
                parse = parse.replace('TOP','UPPER')
                parse = parse.replace('BOTTOM','LOWER')
                parse = parse.replace('LWR','LOWER')
                parse = parse.replace('UPR','UPPER')
                parse = parse.replace('CPILOT','COPILOT')
                parse = parse.replace('CPLT','COPILOT')
                parse = parse.replace('CPT','COPILOT')
                parse = parse.replace('CP','COPILOT')
                parse = parse.replace('PLT','PILOT')
                parse = parse.replace('PT','PILOT')
                parse = parse.replace('PILOTLOWER','PILOT_LOWER')
                parse = parse.replace('PILOTUPPER','PILOT_UPPER')
                parse = parse.replace('LOWERCOPILOT','COPILOT_LOWER')
                parse = parse.replace('UPPERCOPILOT','COPILOT_UPPER')
                parse = parse.replace('LOWERPILOT','PILOT_LOWER')
                parse = parse.replace('UPPERPILOT','PILOT_UPPER')
                parse = parse.replace('COPILOT_','C_')
                parse = parse.replace('PILOT_','P_')
                parse = parse.replace('COPILOT','CP')
                parse = parse.replace('PILOT','PILOT_UPPER,PILOT_LOWER')
                parse = parse.replace('CP','COPILOT_UPPER,COPILOT_LOWER')
                parse = parse.replace('C_','COPILOT_')
                parse = parse.replace('P_','PILOT_')
                
                # remove duplicates and sort
                parse = parse.split(',')
                parse = list(set(parse))
                parse.sort()

                # convert back to string to remove []
                parse = ','.join(map(str, parse))
                
            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse
            
            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str(""):
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def engine_double(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("\#?\W?\d\W?[AB]\W?B?|[^R]\d(?: ENG)?(?:INE)?(?: FADEC)? ?[AB]\W?B?",str(df.loc[i,checks[j]]))

            # keep only alphanumeric and comma separators
            parse = re.sub("[^\w,]","",str(parse))
            
            # grab digit in 1AB to convert to 1A,1B
            try:
                digit = parse[0]
            except:
                digit = ''
            
            # correct parsed labels
            parse = parse.replace('ENG','')
            parse = parse.replace('INE','')
            parse = parse.replace('FADEC','')
            parse = parse.replace('AB',str('A,')+str(digit)+str('B'))
            
            parse = parse.split(',')
            trim = list(set(parse))
            trim.sort()
            
            # convert back to string to remove []
            parse = ','.join(map(str, trim))

            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

# if no information is found in the narratives, search for A/B in narratives and copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            if df.loc[i,'Component_Position_Number'] != str(''):

                j = 0
                parse = []
                while j < len(checks):

                    parse = re.findall("FADEC [AB]\W?B?",str(df.loc[i,checks[j]]))

                    # keep only alphanumeric and comma separators
                    parse = re.sub("[^\w,]","",str(parse))
        
                    digit = str(df.loc[i,'Component_Position_Number'])
                    parse = parse.replace('FADEC','')
                    parse = parse.replace('AB',str('A,')+str(digit)+str('B'))
                    
                    # if empty, check next narrative
                    if parse != str():
                        j = len(checks)
                        df.loc[i,'Parsed_Component_Position']=str(df.loc[i,'Component_Position_Number'])+str(parse)
                    else:
                        j = j+1        

    return df


def BAD(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']
    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("(?<=[^COM])C?O?\W?PI?L?O?T|^C?O?\W?PI?L?O?T|C\W?P|\bP |^P |AUG|AFT CARGO|FWD CARGO|OBS|CENTER|AFT",str(df.loc[i,checks[j]]))

            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub("[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')            
            parse = parse.replace('CP','COPILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            if parse=='P':
                parse = parse.replace('P','PILOT')
            parse = parse.replace('AUG','AUG_CREW')
            parse = parse.replace('AFTCARGO','A_CO')
            parse = parse.replace('FWDCARGO','FWD_CARGO')
            parse = parse.replace('OBS','OBSERVER')
            parse = parse.replace('CENTER','A_CENTER_CONSOLE')
            parse = parse.replace('AFT','AFT_CENTER_CONSOLE')
            parse = parse.replace('A_CO','AFT_CARGO')
            parse = parse.replace('A_CENTER_CONSOLE','AFT_CENTER_CONSOLE')
            
            # remove duplicates and sort
            parse = parse.split(',')
            parse = list(set(parse))
            parse.sort()
            
            # convert back to string to remove []
            parse = ','.join(map(str, parse))
            
            # save values into df
            df.loc[i,'Parsed_Component_Position']=parse

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def FQI(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']
    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("(?:RH|RT|RIGHT|LT|LH|LEFT|LFT|RGT) (?:AUX|EXT)",str(df.loc[i,checks[j]]))
            parsenum = re.findall("(?:\# ?|NO\.? |NUMBER )\d+",str(df.loc[i,checks[j]]))

            # keep only alphanumeric chars and comma separators
            parse = re.sub("[^\w,]","",str(parse))
            parsenum = re.sub("[^\d,]","",str(parsenum))
            
            # convert strings into list of strings
            split = [x for x in parsenum.split(',')]
            parse = [x for x in parse.split(',')]

# handle parsenum/split
            # remove all int values > 4
                # remove empty strings from list
            clean = filter(None, split)
            
                # convert list of strings into list of ints
            ints = map(int, clean)
            
                # remove all values > 4
            trim = [x for x in ints if x<5]
            
            # remove duplicates and sort
            trim = list(set(trim))
            trim.sort()
        
# handle parse    
            # convert back to string with only alphabetical, 1-4 labels
            parse = re.sub("[^\w,^\d]","",str(parse))
            parse = parse.lstrip(',').rstrip(',')
            
            # correct parsed labels
            parse = parse.replace("RH","RH_")
            parse = parse.replace("RT","RH_")
            parse = parse.replace("RIGHT","RH_")
            parse = parse.replace("RGT","RH_")
            parse = parse.replace("LH","LH_")
            parse = parse.replace("LT","LH_")
            parse = parse.replace("LEFT","LH_")
            parse = parse.replace("LFT","LH_")
            
            # remove duplicates and sort
            parse = parse.split(',')
            parse = list(set(parse))
            parse.sort()
            
# concatenate alphabetical labels to numeric positions to get single parsed list
            trim = trim+parse

            # convert back to string to remove []                       
            trim = ','.join(map(str, trim)).rstrip(',')
            
            
            # save values into df
            df.loc[i,'Parsed_Component_Position']=trim

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
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

        qpa_i = this_wuc_qpa.loc[i,:]

        # if labels vary by SN, filter to one set at a time
        if qpa_i.Maximum_SN > 0:
            df_thisqpa = df_one_wuc[(df_one_wuc.Serial_Number >= qpa_i.Minimum_SN_Inclusive) & (df_one_wuc.Serial_Number < qpa_i.Maximum_SN) & (df_one_wuc.Equipment_Designator == qpa_i.MDS)]
        else:
            # if MDS is blank, grab both J and H
            if str(qpa_i.MDS)=='None':
                df_thisqpa = df_one_wuc[(df_one_wuc.Equipment_Designator == 'C130J') | (df_one_wuc.Equipment_Designator == 'C130H')]
            else:
                df_thisqpa = df_one_wuc[df_one_wuc.Equipment_Designator == qpa_i.MDS]
        df_thisqpa['Parsed_Component_Position'] = df_thisqpa['Parsed_Component_Position'].astype(str)

        # Select labeling method based on Names from qpa
        if qpa_i.Names=='1':
            print('Filling with 1')
            df_thisqpa['Parsed_Component_Position'] = '1'
            df_i = df_thisqpa.copy()
            
        elif qpa_i.Names=='1,2,3,4':
            print('Filling with engine_reader')
            df_i = engine_reader(df_thisqpa,libraries)  
            
        elif qpa_i.Names=='copilot,nav':
            print('Filling with cp_navplt')
            df_i = cp_navplt(df_thisqpa,libraries)    
            
        elif qpa_i.Names=='pilot,copilot,nav':
            print('Filling with plt_cp_nav')
            df_i = pilot_cp_nav(df_thisqpa,libraries)   
            
        elif qpa_i.Names=='pilot,copilot':
            print('Filling with cp_plt')
            df_i = cp_plt(df_thisqpa,libraries)
            
        elif qpa_i.Names=='1,2':
            print('Filling with INU')
            df_i = INU(df_thisqpa,libraries)
            
        elif qpa_i.Names=='pilot_upper,pilot_lower,copilot_upper,copilot_lower':
            print('Filling with EFI')
            df_i = EFI(df_thisqpa,libraries)
            
        elif qpa_i.Names=='1A,1B,2A,2B,3A,3B,4A,4B':
            print('Filling with engine_double')
            df_i = engine_double(df_thisqpa,libraries)
            
        elif qpa_i.Names=='pilot,copilot,aug_crew,aft_center_console,aft_cargo,fwd_cargo,observer':
            print('Filling with BAD')
            df_i = BAD(df_thisqpa,libraries)
            
        elif qpa_i.Names=='LH_AUX,RH_AUX,RH_EXT,LH_EXT,1,2,3,4':
            print('Filling with FQI')
            df_i = FQI(df_thisqpa,libraries)
        
        else:
            print('Filling with nothing')
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

        df = pd.read_sql(con=conn, sql="""SELECT A.*, B.Serial_Number, B.Equipment_Designator, B.Work_Unit_Code, B.Discrepancy_Narrative, B.Work_Center_Event_Narrative, 
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

    # change all empty parsed positions to 0
    # df['Parsed_Component_Position'] = df['Parsed_Component_Position'].map(lambda x: 0 if x=='' else x)

    # keep only needed columns to save memory
    keys.append('Parsed_Component_Position')
    df = df[keys]

    return df
