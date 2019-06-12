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

def engine_reader(df_eng,libraries):

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # for each entry, search fields for component position numbers 
    # indexer = list(df.index.values)
    # for i in indexer:
    #     j = 0
    #     parse = []
    #     while j < len(checks):
            
    #         # search narratives for given patterns
    #         parse = re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b|HDD ?\d+",str(df.loc[i,checks[j]]))
            
    #         # replace 'ALL' matches with numbers
    #         parse = [x.replace('ALL FOUR','1,2,3,4') for x in parse]
    #         parse = [x.replace('ALL 4','1,2,3,4') for x in parse]
            
    #         # keep only numeric digits and comma separators
    #         nums = re.sub(r"[^\d,]","",str(parse))
            
    #         # convert string into list of strings
    #         split = [x for x in nums.split(',')]
            
    #         # remove empty strings from list
    #         clean = filter(None, split)
            
    #         # convert list of strings into list of ints
    #         ints = map(int, clean)
            
    #         # remove all values > 4, duplicates and sort
    #         trim = [x for x in ints if x<5]
    #         trim = list(set(trim))
    #         trim.sort()
            
    #         # convert back to string to remove []
    #         remove = ','.join(map(str, trim))

    #         # save values into df
    #         df.loc[i,'Parsed_Component_Position']=remove
    #         # if empty, check next narrative
    #         if any(x.isdigit() for x in remove):
    #             j = len(checks)
    #         else:
    #             j = j+1
                

    #         # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    #     if df.loc[i,'Parsed_Component_Position']==str(''):
    #         df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    def extract_positions_single_narr_engine_reader(df, col):
        # search narratives for given patterns
        df['parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b|HDD ?\d+", x))

        # replace 'ALL' matches with numbers
        df['parse'] = df['parse'].apply(lambda x: [str(ii).replace('ALL FOUR', '1,2,3,4').replace('ALL 4', '1,2,3,4') for ii in x])

        # keep only numeric digits and comma separators
        df['nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df['nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df['nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 4, duplicates and sort
        df['nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<5]))))

        # convert back to string to remove []
        df['nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['nums']
        
        df.drop(['parse','nums'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    for j in checks:

        if df_eng.loc[df_eng.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_engine_reader(df_eng.loc[df_eng.Parsed_Component_Position.str.len()==0].copy(), j)
        df_eng.update(df_sub)
    
    # if no information is found in the narratives, copy in the provided 'Component_Position_Number' - make sure its a non-decimal string
    df_eng.loc[df_eng.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_eng.loc[df_eng.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']

    return df_eng


def cp_navplt(df,libraries):

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check. Use j to iterate through this list.
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):

            # search narratives for given patterns
            parse = re.findall(r"C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub(r"[^\w,]","",str(parse))            
            
            # correct parsed labels
            parse = parse.replace('CPIT','PIT')
            parse = parse.replace(',PIT','')
            parse = parse.replace('PIT,','')
            parse = parse.replace('PIT','')
            parse = parse.replace('PILT','PILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            parse = parse.replace('CPLT','CP')
            parse = parse.replace('CPT','CP')
            parse = parse.replace('CPILOT','CP')
            parse = parse.replace('COPILOT','CP')
            parse = parse.replace('PILOT','NAV')
            parse = parse.replace('CP','COPILOT')
            
            # remove duplicates and sort
            parse = parse.strip()
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
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df

def cp_plt(df,libraries):

    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check. Use j to iterate through this list.
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # search narratives for given patterns
            parse = re.findall("C?O?\W?PI?L?O?T|C\W?P",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub(r"[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('OPI','PI')
            parse = parse.replace('CPIT','PIT')
            parse = parse.replace(',PIT','')
            parse = parse.replace('PIT,','')
            parse = parse.replace('PIT','')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            parse = parse.replace('PILT','PILOT')
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CP','COPILOT')
            
            # remove duplicates and sort
            parse = parse.strip()
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
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def pilot_cp_nav(df,libraries):

    pd = libraries['pandas']
    re = libraries['re']
    
    # define fields to check. Use j to iterate through this list.
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # search narratives for given patterns
            parse = re.findall("C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub(r"[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('OPI','PI')
            parse = parse.replace('CPIT','PIT')
            parse = parse.replace(',PIT','')
            parse = parse.replace('PIT,','')
            parse = parse.replace('PIT','')
            parse = parse.replace('PILT','PILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')
            parse = parse.replace('CP','COPILOT')
            
            # remove duplicates and sort
            parse = parse.strip()
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
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df


def INU(df_inu, libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # for each entry, search fields for component position numbers 
    # indexer = list(df.index.values)
    # for i in indexer:
    #     j = 0
    #     parse = []
    #     while j < len(checks):
            
    #         # search narratives for given patterns
    #         parse = re.findall(r"\#\d+|\# \d+|NO. \d+|NUMBER \d+|1 AND 2|1 \& 2|\#!",str(df.loc[i,checks[j]]))
            
    #         # replace 'AND' matches with numbers
    #         parse = [x.replace('1 AND 2','1,2') for x in parse]
    #         parse = [x.replace('1 & 2','1,2') for x in parse]
    #         parse = [x.replace('#!','1') for x in parse]
            
    #         # keep only numeric digits and comma separators
    #         nums = re.sub(r"[^\d,]","",str(parse))
            
    #         # convert string into list of strings
    #         split = [x for x in nums.split(',')]
            
    #         # remove empty strings from list
    #         clean = filter(None, split)
            
    #         # convert list of strings into list of ints
    #         ints = map(int, clean)
            
    #         # remove all values > 2, duplicates and sort
    #         trim = [x for x in ints if x<3]
    #         trim = list(set(trim))
    #         trim.sort()
            
    #         # convert back to string to remove []
    #         remove = ','.join(map(str, trim))

    #         # save values into df
    #         df.loc[i,'Parsed_Component_Position']=remove
    #         # if empty, check next narrative
    #         if any(x.isdigit() for x in remove):
    #             j = len(checks)
    #         else:
    #             j = j+1
                

          #  # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        # if df.loc[i,'Parsed_Component_Position'] == str(''):
        #     df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    def extract_positions_single_narr_inu(df, col):
        # search narratives for given patterns
        df['parse'] = df[col].apply(lambda x: re.findall(r"\#\d+|\# \d+|NO. \d+|NUMBER \d+|1 AND 2|1 \& 2|\#!", x))
        
        # replace 'AND' matches with numbers
        df['parse'] = df['parse'].apply(lambda x: [str(ii).replace('1 AND 2','1,2').replace('1 & 2','1,2').replace('#!','1') for ii in x])

        # keep only numeric digits and comma separators
        df['nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df['nums'] = df['nums'].apply(lambda x: [ii for ii in x.split(',')])
        # remove empty strings from list
        df['nums'] = df['nums'].apply(lambda x: filter(None, x))
        # convert list of strings into list of ints
        df['nums'] = df['nums'].apply(lambda x: map(int, x))

        # remove all values > 2, duplicates and sort
        df['nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<3]))))
        
        # convert back to string to remove []
        df['nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)).strip())

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['nums']
        
        df.drop(['parse','nums'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    for j in checks:

        if df_inu.loc[df_inu.Parsed_Component_Position.str.len()==0].empty:
                # if all positions have been found then do nothing
                break
        
        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_inu(df_inu.loc[df_inu.Parsed_Component_Position.str.len()==0].copy(), j)
        df_inu.update(df_sub)
        
    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_inu.loc[df_inu.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_inu.loc[df_inu.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']

    return df_inu


def EFI(df,libraries):
    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            if df.loc[i,'Action'] =='SW':
                parse = str('0')      
            
            else:
                # search narratives for given patterns
                parse = re.findall(r"(?:UPP?E?R|LO?WW?E?R|TOP|BOTTOM)? ?C?O?\W?PI?L?O?T\'?S? (?:UPP?E?R|LO?WE?R|TOP|BOTTOM)?|(?:UPP?E?R|LO?WE?R|TOP|BOTTOM)? ?C\W?P\'?S? (?:UPP?E?R|LO?WE?R|TOP|BOTTOM)?|ALL 4|4 NEW",str(df.loc[i,checks[j]]))

                # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
                parse = re.sub(r"[^\w,\d]","",str(parse))
                parse = parse.replace('S','')
                parse = parse.replace('OPI','PI')
                parse = parse.replace('TOP','UPPER')
                parse = parse.replace('BOTTOM','LOWER')
                parse = parse.replace('LWR','LOWER')
                parse = parse.replace('LOWWER','LOWER')
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
                parse = parse.replace('ALL4','PILOT_UPPER,PILOT_LOWER,COPILOT_UPPER,COPILOT_LOWER')
                parse = parse.replace('4NEW','PILOT_UPPER,PILOT_LOWER,COPILOT_UPPER,COPILOT_LOWER')

                # remove duplicates and sort
                parse = parse.split(',')
                parse = list(set(parse))
                parse.sort()

                # convert back to string to remove []
                parse = ','.join(map(str, parse))

                if (parse == str('PILOT_LOWER,PILOT_UPPER') or parse == str('COPILOT_LOWER,COPILOT_UPPER')) and j <2:
                    parse2 = re.findall("(?:UPP?E?R|LO?WW?E?R|TOP|BOTTOM)",str(df.loc[i,checks[j+1]]))
                    if parse2 != []:
                        parse2 = re.sub(r"[^\w,]","",str(parse2))
                        parse2 = parse2.replace('TOP','UPPER')
                        parse2 = parse2.replace('BOTTOM','LOWER')
                        parse2 = parse2.replace('LWR','LOWER')
                        parse2 = parse2.replace('LOWWER','LOWER')
                        parse2 = parse2.replace('UPR','UPPER')
                        parse = parse.replace('COPILOT_LOWER,COPILOT_UPPER','CP')
                        parse = parse.replace('PILOT_LOWER,PILOT_UPPER','PILOT_')
                        parse = parse.replace('CP','COPILOT_')
                        parse = parse+parse2
                
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

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
        j = 0
        parse = []
        while j < len(checks):
            
            # search narratives for given patterns
            parse = re.findall(r"\#?\W?\d\W?[AB]\W?B?|[^R]\d(?: ENG)?(?:INE)?(?: FADEC)? ?[AB]\W?B?",str(df.loc[i,checks[j]]))

            # keep only alphanumeric and comma separators
            parse = re.sub(r"[^\w,]","",str(parse))
            
            # ensure number 1, 2, 3, or 4
            if parse != str(''):
                if (int(parse[0])>4) | (int(parse[0])==0):
                    parse = str('')
                try:
                    if parse[1].isdigit():
                        parse = ''
                except:
                    parse = parse
        
            # grab digit in 1AB to convert to 1A,1B
            try:
                digit = parse[0]
            except:
                digit = ''
            
            
            # correct parsed labels
            parse = parse.replace('ENG','')
            parse = parse.replace('INE','')
            parse = parse.replace('FADEC','')
            parse = parse.replace('BB','B')
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
        if df.loc[i,'Parsed_Component_Position'] == str(''):
            if df.loc[i,'Component_Position_Number'] != str('0'):

                j = 0
                parse = []
                while j < len(checks):

                    parse = re.findall("FADEC [AB]\W?B?",str(df.loc[i,checks[j]]))

                    # keep only alphanumeric and comma separators
                    parse = re.sub(r"[^\w,]","",str(parse))
        
                    digit = str(df.loc[i,'Component_Position_Number'])
                    parse = parse.replace('FADEC','')
                    parse = parse.replace('BB','B')
                    parse = parse.replace('AB',str('A,')+str(digit)+str('B'))
                    
                    # if empty, check next narrative
                    if parse != str(''):
                        j = len(checks)
                        df.loc[i,'Parsed_Component_Position']=str(df.loc[i,'Component_Position_Number'])+str(parse)
                    else:
                        j = j+1
# if still empty, fill with 0
        if df.loc[i,'Parsed_Component_Position'] == str(''):
            df.loc[i,'Parsed_Component_Position'] = '0'
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

            # search narratives for given patterns
            parse = re.findall(r"\bP |^P |(?<=[^COM])C?O?\W?PI?L?O?T|^C?O?\W?PI?L?O?T|C\W?P|AUG|AFT CARGO|FWD CARGO|OBS|CENTER|AFT",str(df.loc[i,checks[j]]))
            
            # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
            parse = re.sub(r"[^\w,]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('CPILOT','COPILOT')
            parse = parse.replace('CPLT','COPILOT')
            parse = parse.replace('CPT','COPILOT')          
            parse = parse.replace('CP','COPILOT')
            parse = parse.replace('PLT','PILOT')
            parse = parse.replace('PT','PILOT')
            parse = parse.replace(',PIT','')
            parse = parse.replace('PIT,','')
            parse = parse.replace('PIT','')
            if parse=='P':
                parse = parse.replace('P','PILOT')
            if 'P,' in parse:
                parse = parse.replace('P,','PILOT,')
            if ',P' in parse:
                parse = parse.replace(',P',',PILOT')
                parse = parse.replace('ILOTILOT','ILOT')
            parse = parse.replace('COPILOT','CP')
            parse = parse.replace('OPILOT','')
            parse = parse.replace('CP','COPILOT')
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

    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # search narratives for given patterns
            parse = re.findall(r"(?:R\/?[HT]|RIGHT|L\/?[HT]|LEFT|LFT|RGT|R|L)\.? (?:HAND )?(?:AUX|EXT)",str(df.loc[i,checks[j]]))
            parsenum = re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+",str(df.loc[i,checks[j]]))

            # keep only alphanumeric chars and comma separators
            parse = re.sub(r"[^\w,]","",str(parse))
            parsenum = re.sub(r"[^\d,]","",str(parsenum))
            
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
            parse = re.sub(r"[^\w,^\d]","",str(parse))
            parse = parse.lstrip(',').rstrip(',')
            
            # correct parsed labels
            parse = parse.replace("HAND","")
            parse = parse.replace("RH","RH_")
            parse = parse.replace("RT","RH_")
            parse = parse.replace("RIGHT","RH_")
            parse = parse.replace("RGT","RH_")
            parse = parse.replace("LH","LH_")
            parse = parse.replace("LT","LH_")
            parse = parse.replace("LEFT","LH_")
            parse = parse.replace("LFT","LH_")
            parse = parse.replace("LEX","LH_EX")
            parse = parse.replace("REX","RH_EX")
            parse = parse.replace("LAUX","LH_AUX")
            parse = parse.replace("RAUX","RH_AUX")
            
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


def ECBU(df_ecbu,libraries):

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # # for each entry, search fields for component position numbers 
    # indexer = list(df.index.values)
    # for i in indexer:
    #     j = 0
    #     parse = []
    #     while j < len(checks):
            
    #         # search narratives for given patterns
    #         parse = re.findall(r"(?:\# ?|NO\.? |NUMBER |ECBU ?)\d+",str(df.loc[i,checks[j]]))
            
    #         # only SW entries can have multiple positions
    #         if df.loc[i,'Action'] != 'SW' and parse != []:
    #             parse = parse[0]
            
    #         # keep only numeric digits and comma separators
    #         nums = re.sub(r"[^\d,]","",str(parse))
            
    #         # convert string into list of strings
    #         split = [x for x in nums.split(',')]
            
    #         # remove empty strings from list
    #         clean = filter(None, split)
            
    #         # convert list of strings into list of ints
    #         ints = map(int, clean)
            
    #         # remove all values > 4, duplicates and sort
    #         trim = [x for x in ints if x<14]
    #         trim = list(set(trim))
    #         trim.sort()
            
    #         # convert back to string to remove []
    #         remove = ','.join(map(str, trim))

    #         # save values into df
    #         df.loc[i,'Parsed_Component_Position']=remove
    #         # if empty, check next narrative
    #         if any(x.isdigit() for x in remove):
    #             j = len(checks)
    #         else:
    #             j = j+1

    # # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    #     if df.loc[i,'Parsed_Component_Position']==str(''):
    #         df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']
                
    def extract_positions_single_narr_ecbu(df, col):
        # search narratives for given patterns
        df['parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER |ECBU ?)\d+", x))

        # only SW entries can have multiple positions
        df.loc[(df.Action!='SW') & (df.parse.str.len()!=0), 'parse'] = df.loc[(df.Action!='SW') & (df.parse.str.len()!=0), 'parse'].apply(lambda x: x[0])

        # keep only numeric digits and comma separators
        df['nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df['nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df['nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 13, duplicates and sort
        df['nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<14]))))

        # convert back to string to remove []
        df['nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['nums']
        
        df.drop(['parse','nums'], axis=1, inplace=True)

        return df[df.Parsed_Component_Position.str.len()>0]

    for j in checks:

        if df_ecbu.loc[df_ecbu.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_ecbu(df_ecbu.loc[df_ecbu.Parsed_Component_Position.str.len()==0].copy(), j)
        df_ecbu.update(df_sub)
        
    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_ecbu.loc[df_ecbu.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_ecbu.loc[df_ecbu.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']
    
    return df_ecbu


def CCU(df,libraries):
    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    indexer = list(df.index.values)
    for i in indexer:
#     for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):

            # search narratives for given patterns
            parse = re.findall(r"\d+A\d+|CENTER CONSOL|CNTR CONSOL|RTP|AUG(?:MENTED)? (?:(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L)?|(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L",str(df.loc[i,checks[j]]))
        
            # keep only alphabetical chars and comma separators
            parse = re.sub(r"[^\w,]","",str(parse))
            parse = re.sub(r"[\d]","",str(parse))
            
            # correct parsed labels
            parse = parse.replace('CUROSR','CURSOR')
            parse = parse.replace('CURSOR','CURSOR_')            
            parse = parse.replace('CNTRL','CONTROL')
            parse = parse.replace('CNTL','CONTROL')
            parse = parse.replace('CNT','CONTROL')
            parse = parse.replace('CNTR','CONTROL')
            parse = parse.replace('CONTRL','CONTROL')
            parse = parse.replace('CNTROL','CONTROL')
            parse = parse.replace('PANEL','')
            parse = parse.replace('PNL','')
            parse = parse.replace('PANL','')
            parse = parse.replace('PNEL','')
            parse = parse.replace('CURSOR_CONTROL','CENTER')
            parse = parse.replace('CNTR','CENTER')
            parse = parse.replace('CONSOL','')
            parse = parse.replace('AUGMENTED','UG_CREW')
            parse = parse.replace('AUG','UG_CREW')
            parse = parse.replace('RTP','OTHER')
            parse = parse.replace('A','OTHER')
            parse = parse.replace('UG_CREW','AUG')
            parse = parse.replace('AUGCENTER','AUG')
            
            # remove duplicates and sort
#             parse = parse.strip()
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
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df



def APU(df_apu,libraries):

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # # for each entry, search fields for component position numbers 
    # indexer = list(df.index.values)
    # for i in indexer:
    #     j = 0
    #     parse = []
    #     while j < len(checks):
            
    #         # search narratives for given patterns
    #         parse = re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b",str(df.loc[i,checks[j]]))
    #         parseapu = re.findall("APU",str(df.loc[i,checks[j]]))
            
    #         # keep only numeric digits, APU, and comma separators
    #         nums = re.sub(r"[^\d,]","",str(parse))
            
    #         # convert string into list of strings
    #         split = [x for x in nums.split(',')]
            
    #         # remove empty strings from list
    #         clean = filter(None, split)
            
    #         # convert list of strings into list of ints
    #         ints = map(int, clean)
            
    #         # remove all values > 4, duplicates and sort
    #         trim = [x for x in ints if x<5]
    #         trim = list(set(trim))
    #         trim.sort()
            
    #         # add APU back into label
    #         parseapu = list(set(parseapu))
    #         trim = map(str,trim)
    #         trim=trim+parseapu
            
    #         # convert back to string to remove []
    #         remove = ','.join(map(str, trim)).strip()

    #         # save values into df
    #         df.loc[i,'Parsed_Component_Position']=remove
    #         # if empty, check next narrative
    #         if ((any(x.isdigit() for x in remove)) | ('APU' in remove)):
    #             j = len(checks)
    #         else:
    #             j = j+1
                

    #         # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    #     if df.loc[i,'Parsed_Component_Position']==str(''):
    #         df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']
            
            # # convert numeric '5' into 'APU'
            # if str(df.loc[i,'Parsed_Component_Position']) == '5':
            #     df.loc[i,'Parsed_Component_Position'] = 'APU'

    def extract_positions_single_narr_apu_reader(df, col):
        # search narratives for given patterns
        df['parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b", x))
        df['parseapu'] = df[col].apply(lambda x: re.findall(r"APU", x))

        # keep only numeric digits and comma separators
        df['nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df['nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df['nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 4, duplicates and sort
        df['nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<5]))))

        # add APU back into label
        df['parseapu'] = df['parseapu'].apply(lambda x: list(set(x)))
        df['nums'] = df['nums'].apply(lambda x: map(str, x))
        df['nums'] = df.apply(lambda row: row.nums + row.parseapu, 
                              axis=1)
        
        # convert back to string to remove []
        df['nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)).strip())

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['nums']
        
        df.drop(['parse','nums','parseapu'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    for j in checks:
        
        if df_apu.loc[df_apu.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_apu_reader(df_apu.loc[df_apu.Parsed_Component_Position.str.len()==0].copy(), j)
        df_apu.update(df_sub)
        
    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    # convert numeric '5' into 'APU'
    df_apu.loc[(df_apu.Parsed_Component_Position.str.len()==0) &
                   (df_apu.Component_Position_Number == 5), 'Parsed_Component_Position'] = 'APU'
    df_apu.loc[df_apu.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_apu.loc[df_apu.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']
                
    return df_apu


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
            # filter by SN range & MDS
            df_thisqpa = df_one_wuc[(df_one_wuc.Serial_Number >= qpa_i.Minimum_SN_Inclusive) & (df_one_wuc.Serial_Number < qpa_i.Maximum_SN) & (df_one_wuc.Equipment_Designator == qpa_i.MDS)]
        
        else:
            # if MDS is blank, grab both J and H
            if "C" not in str(qpa_i.MDS):
                df_thisqpa = df_one_wuc[(df_one_wuc.Equipment_Designator == 'C130J') | (df_one_wuc.Equipment_Designator == 'C130H')]
            
            else:
                df_thisqpa = df_one_wuc[df_one_wuc.Equipment_Designator == qpa_i.MDS]
        
        df_thisqpa.loc[:,'Parsed_Component_Position'] = df_thisqpa.loc[:,'Parsed_Component_Position'].astype(str)

        # Select labeling method based on Names from qpa
        if qpa_i.Names==str('1'):

            df_thisqpa.loc[:,'Parsed_Component_Position'] = str('1')
            df_i = df_thisqpa
            
        elif qpa_i.Names=='1,2,3,4':
            # print('Filling with engine_reader')
            df_i = engine_reader(df_thisqpa,libraries)  
            
        elif qpa_i.Names=='copilot,nav':
            # print('Filling with cp_navplt')
            df_i = cp_navplt(df_thisqpa,libraries)    
            
        elif qpa_i.Names=='pilot,copilot,nav':
            # print('Filling with plt_cp_nav')
            df_i = pilot_cp_nav(df_thisqpa,libraries)   
            
        elif qpa_i.Names=='pilot,copilot':
            # print('Filling with cp_plt')
            df_i = cp_plt(df_thisqpa,libraries)
            
        elif qpa_i.Names=='1,2':
            # print('Filling with INU')
            df_i = INU(df_thisqpa,libraries)
            
        elif qpa_i.Names=='pilot_upper,pilot_lower,copilot_upper,copilot_lower':
            # print('Filling with EFI')
            df_i = EFI(df_thisqpa,libraries)
            
        elif qpa_i.Names=='1A,1B,2A,2B,3A,3B,4A,4B':
            # print('Filling with engine_double')
            df_i = engine_double(df_thisqpa,libraries)
            
        elif qpa_i.Names=='pilot,copilot,aug_crew,aft_center_console,aft_cargo,fwd_cargo,observer':
            # print('Filling with BAD')
            df_i = BAD(df_thisqpa,libraries)
            
        elif qpa_i.Names=='LH_AUX,RH_AUX,RH_EXT,LH_EXT,1,2,3,4':
            # print('Filling with FQI')
            df_i = FQI(df_thisqpa,libraries)

        elif qpa_i.Names=='1,2,3,4,5,6,7,8,9,10,11,12,13':
            # print('Filling with ECBU')
            df_i = ECBU(df_thisqpa,libraries)

        elif qpa_i.Names=='aug,center,other':
            # print('Filling with CCU')
            df_i = CCU(df_thisqpa,libraries)

        elif qpa_i.Names=='1,2,3,4,apu':
            # print('Filling with APU')
            df_i = APU(df_thisqpa,libraries)
        
        else:
            # print('Scheme not found. Position left unparsed')
            df_i = df_thisqpa
        
        # Add labels to df
        df_one_wuc.update(df_i)
    return df_one_wuc

def fn(conn, libraries, params, predecessors):

    pd = libraries["pandas"]
    re = libraries["re"]

    if len(predecessors) in (2,4):

        if len(predecessors) == 2:  
            if len([ii for ii in predecessors if 'compiled' in ii]) > 0:
                # KC135, single WUC
                for pred in predecessors:
                    if 'compiled' in pred:
                        compiled_table_name = pred
                    else:
                        key_table_name = pred
                df_qpa = pd.DataFrame()
            else:
                # C130 comparisons for ercm
                for pred in predecessors:
                    if 'qpa' in pred:
                        qpa_table_name = pred
                    else:
                        data_table_name = pred
                compiled_table_name = None
                df_qpa = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(qpa_table_name))
                df = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(data_table_name))
                keys = list(df.columns)  # all data
        else:
            # C130, multiple WUCs and complex QPA
            for pred in predecessors:
                if 'compiled' in pred:
                    compiled_table_name = pred
                elif 'qpa' in pred:
                    qpa_table_name = pred
                elif 'label' in pred:
                    action_table_name = pred
                else:
                    wuc_table_name = pred
            df_qpa = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(qpa_table_name))

        if compiled_table_name:
            # read data from multiple tables 
            keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(wuc_table_name), con=conn).Column_name)
            join_clause_1 = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
            join_clause_1 = ' AND '.join(join_clause_1)
            join_clause_2 = ['A.{} = C.{}'.format(ii,ii) for ii in keys]
            join_clause_2 = ' AND '.join(join_clause_2)

            df = pd.read_sql(con=conn, sql="""SELECT A.*, C.Serial_Number, C.Equipment_Designator, B.Action, COALESCE(C.Discrepancy_Narrative,"") Discrepancy_Narrative, 
                COALESCE(C.Work_Center_Event_Narrative,"") Work_Center_Event_Narrative, 
                COALESCE(C.Corrective_Narrative,"") Corrective_Narrative, C.Component_Position_Number FROM {} A 
                JOIN {} B ON {} LEFT JOIN {} C ON {}""".format(wuc_table_name, action_table_name, 
                    join_clause_1, compiled_table_name, join_clause_2))

    elif len(predecessors) == 1:
        # KC135 comparison against NB-BOW
        keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(predecessors[0]), con=conn).Column_name)
        df = pd.read_sql(con=conn, sql="""SELECT * FROM {}""".format(predecessors[0]))        
        df_qpa = pd.DataFrame()

    else:
        raise Exception, "Component should have one, two, or three predecessor components"

    # standardize columns
    df.loc[:,'Parsed_Component_Position'] = ""
    df.loc[:,'Parsed_Component_Position'] = df.loc[:,'Parsed_Component_Position'].astype(str)
    df.loc[:,'Component_Position_Number'] = df.loc[:,'Component_Position_Number'].fillna(0).astype('int64').astype(str)  # no awful 0.0 strings
    
    
    if df_qpa.empty:
        # backwards compatability for KC135
        df = engine_reader(df, libraries)
        keys.append('Parsed_Component_Position')
        return df[keys]
    
    # standardize columns
    df_qpa.Maximum_SN = df_qpa.Maximum_SN.fillna(0)
    df_qpa.Minimum_SN_Inclusive = df_qpa.Minimum_SN_Inclusive.fillna(0)
    df_qpa.Alternate_WUC = df_qpa.Alternate_WUC.astype(str)


    # treat all WUCs differently by running the label picker for each wuc
    for this_wuc in df.Work_Unit_Code.unique():
        
        df_one_wuc = df[df.Work_Unit_Code == this_wuc]
        wuc_qpa = df_qpa[(df_qpa.Work_Unit_Code == this_wuc) | [this_wuc in df_qpa.loc[x,'Alternate_WUC'] for x in range(0,len(df_qpa))]]
        df_one_wuc = label_picker(df_one_wuc,wuc_qpa,this_wuc,libraries)
        df.update(df_one_wuc)
        print('WUC '+ str(this_wuc) + ' complete')

    df.loc[:,'Parsed_Component_Position'] = df.loc[:,'Parsed_Component_Position'].astype(str)

    # change all empty parsed positions to 0
    df.loc[df.Parsed_Component_Position.str.len()==0,'Parsed_Component_Position'] = '0'

    # keep only needed columns to save memory
    keys.append('Parsed_Component_Position')
    df = df[keys]

    return df