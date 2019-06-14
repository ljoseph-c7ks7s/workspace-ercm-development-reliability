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
    df_eng = df_eng.copy()

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
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b|HDD ?\d+", x))

        # replace 'ALL' matches with numbers
        df.loc[:, 'parse'] = df['parse'].apply(lambda x: [str(ii).replace('ALL FOUR', '1,2,3,4').replace('ALL 4', '1,2,3,4') for ii in x])

        # keep only numeric digits and comma separators
        df.loc[:, 'nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 4, duplicates and sort
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<5]))))

        # convert back to string to remove []
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)))

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


def cp_navplt(df_cp_navplt,libraries):
    df_cp_navplt = df_cp_navplt.copy()


    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check. Use j to iterate through this list.
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    # for each entry, search fields for component position numbers 
    # indexer = list(df.index.values)
    # for i in indexer:
    #     j = 0
    #     parse = []
    #     while j < len(checks):

    #         # search narratives for given patterns
    #         parse = re.findall(r"C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))
            
    #         # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
    #         parse = re.sub(r"[^\w,]","",str(parse))            
            
    #         # correct parsed labels
    #         parse = parse.replace('CPIT','PIT')
    #         parse = parse.replace(',PIT','')
    #         parse = parse.replace('PIT,','')
    #         parse = parse.replace('PIT','')
    #         parse = parse.replace('PILT','PILOT')
    #         parse = parse.replace('PLT','PILOT')
    #         parse = parse.replace('PT','PILOT')
    #         parse = parse.replace('CPLT','CP')
    #         parse = parse.replace('CPT','CP')
    #         parse = parse.replace('CPILOT','CP')
    #         parse = parse.replace('COPILOT','CP')
    #         parse = parse.replace('PILOT','NAV')
    #         parse = parse.replace('CP','COPILOT')
            
    #         # remove duplicates and sort
    #         parse = parse.strip()
    #         parse = parse.split(',')
    #         parse = list(set(parse))
    #         parse.sort()
            
    #         # convert back to string to remove []
    #         parse = ','.join(map(str, parse))

    #         # save values into df
    #         df.loc[i,'Parsed_Component_Position']=parse

    #         # if empty, check next narrative
    #         if df.loc[i,'Parsed_Component_Position'] != "":
    #             j = len(checks)
    #         else:
    #             j = j+1

    #             # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    #     if df.loc[i,'Parsed_Component_Position']==str(''):
    #         df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    # search narratives for given patterns

    def extract_positions_single_narr_cp_navplt(df, col):           

        # search narratives for given patterns
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"C?O?\W?PI?L?O?T|C\W?P|NAV", str(x)))

        # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
        df.loc[:, 'alpha'] = df.parse.apply(lambda x: re.sub(r"[^\w,]","",str(x)))

        # correct parsed labels
        parse_list = [('CPIT','PIT'), (',PIT',''),('PIT,',''), ('PIT',''), ('PILT','PILOT'), ('PLT','PILOT'), ('PT','PILOT'),('CPLT','CP'),('CPT','CP'), ('CPILOT','CP'), ('COPILOT','CP'),('PILOT','NAV'), ('CP','COPILOT')]
        for tup in parse_list:
            df.loc[:, 'alpha'] = df.alpha.apply(lambda x: x.replace(tup[0],tup[1]))

        # remove duplicates and sort
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: sorted(list(set(x.strip().split(',')))))

        # convert back to string to remove []
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: ','.join(map(str, x)))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['alpha']

        df.drop(['parse','alpha'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    
    for j in checks:
        if df_cp_navplt.loc[df_cp_navplt.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_cp_navplt(df_cp_navplt.loc[df_cp_navplt.Parsed_Component_Position.str.len()==0].copy(), j)
        df_cp_navplt.update(df_sub)

    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_cp_navplt.loc[df_cp_navplt.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_cp_navplt.loc[df_cp_navplt.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']

    return df_cp_navplt


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
            parse = re.findall(r"C?O?\W?PI?L?O?T|C\W?P",str(df.loc[i,checks[j]]))
            
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


def pilot_cp_nav(df_pilot_cp_nav,libraries):
    df_pilot_cp_nav = df_pilot_cp_nav.copy()

    pd = libraries['pandas']
    re = libraries['re']
    
    # define fields to check. Use j to iterate through this list.
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']


    #     # for each entry, search fields for component position numbers
    #     indexer = list(df.index.values)
    #     for i in indexer:
    # #     for i in range (0,len(df)):
    #         j = 0
    #         parse = []
    #         while j < len(checks):

    #             # search narratives for given patterns
    #             parse = re.findall("C?O?\W?PI?L?O?T|C\W?P|NAV",str(df.loc[i,checks[j]]))

    #             # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
    #             parse = re.sub(r"[^\w,]","",str(parse))

    #             # correct parsed labels
    #             parse = parse.replace('OPI','PI')
    #             parse = parse.replace('CPIT','PIT')
    #             parse = parse.replace(',PIT','')
    #             parse = parse.replace('PIT,','')
    #             parse = parse.replace('PIT','')
    #             parse = parse.replace('PILT','PILOT')
    #             parse = parse.replace('PLT','PILOT')
    #             parse = parse.replace('PT','PILOT')
    #             parse = parse.replace('CPILOT','COPILOT')
    #             parse = parse.replace('CPLT','COPILOT')
    #             parse = parse.replace('CPT','COPILOT')
    #             parse = parse.replace('CP','COPILOT')

    #             # remove duplicates and sort
    #             parse = parse.strip()
    #             parse = parse.split(',')
    #             parse = list(set(parse))
    #             parse.sort()

    #             # convert back to string to remove []
    #             parse = ','.join(map(str, parse))

    #             # save values into df
    #             df.loc[i,'Parsed_Component_Position']=parse

    #             # if empty, check next narrative
    #             if df.loc[i,'Parsed_Component_Position'] != "":
    #                 j = len(checks)
    #             else:
    #                 j = j+1


    def extract_positions_single_narr_pilot_cp_nav(df, col):           

        # search narratives for given patterns
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"C?O?\W?PI?L?O?T|C\W?P|NAV", str(x)))

        # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
        df.loc[:, 'alpha'] = df.parse.apply(lambda x: re.sub(r"[^\w,]","",str(x)))

        # correct parsed labels
        parse_list = [('OPI','PI'), ('CPIT','PIT'), (',(PIT',''), ('PIT',''), ('PILT','PILOT'), ('PLT','PILOT'), ('PT','PILOT'), ('CPILOT','COPILOT'), ('CPLT','COPILOT'), ('CPT','COPILOT'), ('CP','COPILOT')]
        for tup in parse_list:
            df.loc[:, 'alpha'] = df.alpha.apply(lambda x: x.replace(tup[0],tup[1]))

        # remove duplicates and sort
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: sorted(list(set(x.strip().split(',')))))

        # convert back to string to remove []
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: ','.join(map(str, x)))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['alpha']

        df.drop(['parse','alpha'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]


    
    for j in checks:
        if df_pilot_cp_nav.loc[df_pilot_cp_nav.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_pilot_cp_nav(df_pilot_cp_nav.loc[df_pilot_cp_nav.Parsed_Component_Position.str.len()==0].copy(), j)
        df_pilot_cp_nav.update(df_sub)

    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_pilot_cp_nav.loc[df_pilot_cp_nav.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_pilot_cp_nav.loc[df_pilot_cp_nav.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']

    return df_pilot_cp_nav


def INU(df_inu, libraries):
    df_inu = df_inu.copy()

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
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"\#\d+|\# \d+|NO. \d+|NUMBER \d+|1 AND 2|1 \& 2|\#!", str(x)))
        
        # replace 'AND' matches with numbers
        df.loc[:, 'parse'] = df['parse'].apply(lambda x: [str(ii).replace('1 AND 2','1,2').replace('1 & 2','1,2').replace('#!','1') for ii in x])

        # keep only numeric digits and comma separators
        df.loc[:, 'nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: [ii for ii in x.split(',')])
        # remove empty strings from list
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: filter(None, x))
        # convert list of strings into list of ints
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: map(int, x))

        # remove all values > 2, duplicates and sort
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<3]))))
        
        # convert back to string to remove []
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)).strip())

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
            
            # search narratives for given patterns
            pcoparse = re.findall(r"C?[0O]?\W?(?<!AUTO)(?<!AUTO )PI?L?O?T|C\W?P",str(df.loc[i,checks[j]]))
            locparse = re.findall(r"\bUPP?E?R\b|\bLO?WW?E?R\b|\bTOP\b|\bBOTTOM\b|\bA\W?D\W?I\b|\bH\W?S\W?I\b|\bF\W?D\W?I\b",str(df.loc[i,checks[j]]))
            allparse = re.findall(r"ALL 4|4 NEW",str(df.loc[i,checks[j]]))
            
            # if all 4, label and break
            if allparse:
                df.loc[i,'Parsed_Component_Position'] = 'COPILOT_ADI,COPILOT_HSI,PILOT_ADI,PILOT_HSI'
                break
            
            # search for clues in next narrative if search returns incomplete
            elif pcoparse and not locparse:
                try:
                    locparse = re.findall(r"\bUPP?E?R\b|\bLO?WW?E?R\b|\bTOP\b|\bBOTTOM\b|\bADI\b|\bHSI\b|\bF\W?D\W?I\b",str(df.loc[i,checks[j+1]]))
                except:
                    locparse = []
            
            elif not pcoparse and locparse:
                try:
                    pcoparse = re.findall(r"C?[0O]?\W?(?<!AUTO)(?<!AUTO )PI?L?O?T|C\W?P",str(df.loc[i,checks[j+1]]))
                except:
                    pcoparse = []

# clean and standardize labels

            # keep only alphabetical characters
            pcoparse = re.sub(r"[^\w,]","",str(pcoparse))
            locparse = re.sub(r"[^\w,]","",str(locparse))
            
            
            # correct pcoparse
            pcoparse = pcoparse.replace('C0','CO')
            pcoparse = pcoparse.replace('CPLT','COPILOT')
            pcoparse = pcoparse.replace('CPT','COPILOT')
            pcoparse = pcoparse.replace('CPILOT','COPILOT')
            pcoparse = pcoparse.replace('CP','COPILOT')
            pcoparse = pcoparse.replace('PLT','PILOT')
            pcoparse = pcoparse.replace('PT','PILOT')            
            
            # correct locparse
            locparse = locparse.replace('TOP','UPPER')
            locparse = locparse.replace('BOTTOM','LOWER')
            locparse = locparse.replace('LWR','LOWER')
            locparse = locparse.replace('LOWWER','LOWER')
            locparse = locparse.replace('UPR','UPPER')
            locparse = locparse.replace('UPPER','ADI')
            locparse = locparse.replace('LOWER','HSI')
            locparse = locparse.replace('FDI','ADI')
            

            # remove duplicates and sort
            pcoparse = pcoparse.split(',')
            pcoparse = list(set(pcoparse))
            pcoparse.sort()
            locparse = locparse.split(',')
            locparse = list(set(locparse))
            locparse.sort()
            
            # combine non-empty lists (top),(pilot,copilot) -> (pilot_top,copilot_top)
            if pcoparse and locparse:
                crossed = [str(x)+str('_')+str(y) for x in pcoparse for y in locparse]

                # convert back to string to remove []                       
                crossed = ','.join(map(str, crossed)).rstrip(',')
            
            # if first or last character is _ then cross multiply wrong
            if crossed[0]==str('_') or crossed[-1]==str('_'):
                crossed = str('')
                
            # save values into df
            df.loc[i,'Parsed_Component_Position']=crossed

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                
            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = str('0')
            

    return df


def engine_double(df_eng_dbl,libraries):
    df_eng_dbl = df_eng_dbl.copy()

    pd = libraries['pandas']
    re = libraries['re']

    # define fields to check. Use j to iterate through this list
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    #     # for each entry, search fields for component position numbers
    #     indexer = list(df.index.values)
    #     for i in indexer:
    #         j = 0
    #         parse = []
    #         while j < len(checks):

    #             # search narratives for given patterns
    #             parse = re.findall(r"\#?\W?\d\W?[AB]\W?B?|[^R]\d(?: ENG)?(?:INE)?(?: FADEC)? ?[AB]\W?B?",str(df.loc[i,checks[j]]))

    #             # keep only alphanumeric and comma separators
    #             parse = re.sub(r"[^\w,]","",str(parse))

    #             # ensure number 1, 2, 3, or 4
    #             if parse != str(''):
    #                 if (int(parse[0])>4) | (int(parse[0])==0):
    #                     parse = str('')
    #                 try:
    #                     if parse[1].isdigit():
    #                         parse = ''
    #                 except:
    #                     parse = parse

    #             # grab digit in 1AB to convert to 1A,1B
    #             try:
    #                 digit = parse[0]
    #             except:
    #                 digit = ''


    #             # correct parsed labels
    #             parse = parse.replace('ENG','')
    #             parse = parse.replace('INE','')
    #             parse = parse.replace('FADEC','')
    #             parse = parse.replace('BB','B')
    #             parse = parse.replace('AB',str('A,')+str(digit)+str('B'))

    #             parse = parse.split(',')
    #             trim = list(set(parse))
    #             trim.sort()

    #             # convert back to string to remove []
    #             parse = ','.join(map(str, trim))

    #             # save values into df
    #             df.loc[i,'Parsed_Component_Position']=parse

    #             # if empty, check next narrative
    #             if df.loc[i,'Parsed_Component_Position'] != "":
    #                 j = len(checks)
    #             else:
    #                 j = j+1


    # # if no information is found in the narratives, search for A/B in narratives and copy in the provided 'Component_Position_Number'
    #         if df.loc[i,'Parsed_Component_Position'] == str(''):
    #             if df.loc[i,'Component_Position_Number'] != str('0'):

    #                 j = 0
    #                 parse = []
    #                 while j < len(checks):

    #                     parse = re.findall(r"FADEC [AB]\W?B?",str(df.loc[i,checks[j]]))

    #                     # keep only alphanumeric and comma separators
    #                     parse = re.sub(r"[^\w,]","",str(parse))

    #                     digit = str(df.loc[i,'Component_Position_Number'])
    #                     parse = parse.replace('FADEC','')
    #                     parse = parse.replace('BB','B')
    #                     parse = parse.replace('AB',str('A,')+str(digit)+str('B'))

    #                     # if empty, check next narrative
    #                     if parse != str(''):
    #                         j = len(checks)
    #                         df.loc[i,'Parsed_Component_Position']=str(df.loc[i,'Component_Position_Number'])+str(parse)
    #                     else:
    #                         j = j+1


    def extract_positions_single_narr_eng_dbl(df, col):
        # loop through found elements within a narrative and apply transforming logic
        
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"\#?\W?\d\W?[AB]\W?B?|[^R]\d(?: ENG)?(?:INE)?(?: FADEC)? ?[AB]\W?B?", str(x)))
        df.loc[:, 'parse'] = df.parse.apply(lambda l: [re.sub(r"[^\w,]","",str(ii)) for ii in l])

        # if the first letter is a non-digit or a zero then drop it
        df.loc[:, 'parse'] = df['parse'].apply(lambda l: [x if len(ii)<2 else ii[1:] if re.search(r"[A-Z0]", ii[0]) else ii for ii in l])

        # if the first letter is a digit and is > 4 then drop the entire label
        df.loc[df.parse.str.len()>0, 'parse'] = \
            df.loc[df.parse.str.len()>0, 'parse'].apply(lambda l: [ii for ii in l if len(ii)>0 and ii[0].isdigit() and int(ii[0]) < 5])
            
        # now if the first letter is a non-digit then drop the entire piece
        # also if the first letter is a digit and > 4 then drop the entire piece
        check_second_letter = lambda x: True if len(x) < 2 else False if str(x[1]).isdigit() else True

        df.loc[df.parse.str.len()>0, 'parse'] = \
            df.loc[df.parse.str.len()>0, 'parse'].apply(lambda l: filter(check_second_letter, l))
            
        # correct parsed labels
        parse_list = [('ENG',''), ('INE',''), ('FADEC',''), ('BB','B')]
        for w, v in parse_list:
            df.loc[:, 'parse'] = df['parse'].apply(lambda l: [ii.replace(w, v) for ii in l])
            
        # special correction for cases like '4AB'
        df.loc[:, 'parse'] = df.parse.apply(lambda l: [ii.replace('AB','A,{}B'.format(ii[0])) if len(ii)>0 else ii for ii in l])

        # remove duplicates and sort
        # some items are complex, with items w/in items, e.g. ['1A,1B', '2A,2B', '3B', '3A', '4A,4B']
        #   need to flatten these
        df.loc[:, 'parse'] = df.parse.apply(lambda l: sorted(list(set([kk for jj in (ii.split(',') for ii in l) for kk in jj]))))

        # remove empties
        df.loc[:, 'parse'] = df.parse.apply(lambda l: filter(None, l))

        # convert back to string to remove []
        df.loc[:, 'parse'] = df.parse.apply(lambda x: ','.join(x))

        # save values into dataframe
        df.loc[:,'Parsed_Component_Position'] = df['parse']

        df.drop(['parse'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    for j in checks:

        if df_eng_dbl.loc[df_eng_dbl.Parsed_Component_Position.str.len()==0].empty:
                # if all positions have been found then do nothing
                break
        
        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_eng_dbl(df_eng_dbl.loc[df_eng_dbl.Parsed_Component_Position.str.len()==0].copy(), j)
        df_eng_dbl.update(df_sub)

    ##########
    # if no information is found in the narratives, 
    #  search for A/B in narratives and copy in the provided 'Component_Position_Number' (if it exists)
    def extract_positions_single_narr_eng_dbl_fallback(df, col):

        # if no information is found in the narratives, 
        #  search for A/B in narratives and copy in the provided 'Component_Position_Number' (if it exists)
        df.loc[:, 'parse'] = ''
        df.loc[(df.Parsed_Component_Position.str.len()==0) & 
           (df.Component_Position_Number.apply(lambda x: False if len(str(x)) < 1 else False if str(int(x))=='0' else True)), 'parse'] = \
            df.loc[(df.Parsed_Component_Position.str.len()==0) & 
               (df.Component_Position_Number.apply(lambda x: False if len(str(x)) < 1 else False if str(int(x))=='0' else True)), col].apply(lambda x: re.findall(r"FADEC [AB]\W?B?", str(x)))

        # keep only alphanumeric and comma separators (drop plus, slash, etc.)
        df.parse = df.parse.apply(lambda l: [re.sub(r"[^\w,]","",str(ii)) for ii in l])

        # correct parsed labels
        parse_list = [('FADEC',''), ('BB','B')]
        for w, v in parse_list:
            df.loc[:, 'parse'] = df['parse'].apply(lambda l: [ii.replace(w, v) for ii in l])
            
        # special correction for cases like 'AB' - need component position so apply over entire row
        df.loc[:, 'parse'] = df.apply(axis=1, 
                               func=lambda row: [ii.replace('AB','A,{}B'.format(row.Component_Position_Number)) if len(ii)>0 else ii for ii in row.parse])

        # add in position
        df.loc[:, 'parse'] = df.apply(axis=1,
                              func=lambda row: row.parse if len(row.parse)<1 else ["{}{}".format(row.Component_Position_Number, ii) for ii in row.parse])

        # combine into single string
        # remove duplicates and sort
        # some items are complex, with items w/in items, e.g. ['1A,1B', '2A,2B', '3B', '3A', '4A,4B']
        #   need to flatten these
        df.loc[:, 'parse'] = df.parse.apply(lambda l: sorted(list(set([kk for jj in (ii.split(',') for ii in l) for kk in jj]))))

        # remove empties
        df.loc[:, 'parse'] = df.parse.apply(lambda l: filter(None, l))

        # convert back to string to remove []
        df.loc[:, 'parse'] = df.parse.apply(lambda x: ','.join(x))

        # save values into dataframe
        df.loc[:,'Parsed_Component_Position'] = df['parse']

        df.drop(['parse'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]


    for j in checks:
        if df_eng_dbl.loc[df_eng_dbl.Parsed_Component_Position.str.len()==0].empty:
                # if all positions have been found then do nothing
                break
        
        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_eng_dbl_fallback(df_eng_dbl.loc[df_eng_dbl.Parsed_Component_Position.str.len()==0].copy(), j)
        df_eng_dbl.update(df_sub)

    # if still empty, fill with 0
    df_eng_dbl.loc[df_eng_dbl.Parsed_Component_Position.str.len() < 1, 'Parsed_Component_Position'] = '0'

    return df_eng_dbl


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


def FQI(df_fqi,libraries):
    df_fqi = df_fqi.copy()

    pd = libraries['pandas']
    re = libraries['re']
    
    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']

    # for each entry, search fields for component position numbers 
 #    indexer = list(df.index.values)
 #    for i in indexer:
    # #     for i in range (0,len(df)):
 #        j = 0
 #        parse = []
 #        while j < len(checks):

 #            # search narratives for given patterns
 #            parse = re.findall(r"(?:R\/?[HT]|RIGHT|L\/?[HT]|LEFT|LFT|RGT|R|L)\.? (?:HAND )?(?:AUX|EXT)",str(df.loc[i,checks[j]]))
 #            parsenum = re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+",str(df.loc[i,checks[j]]))

 #            # keep only alphanumeric chars and comma separators
 #            parse = re.sub(r"[^\w,]","",str(parse))
 #            parsenum = re.sub(r"[^\d,]","",str(parsenum))
            
 #            # convert strings into list of strings
 #            split = [x for x in parsenum.split(',')]
 #            parse = [x for x in parse.split(',')]

    # # handle parsenum/split
 #            # remove all int values > 4
 #                # remove empty strings from list
 #            clean = filter(None, split)
            
 #                # convert list of strings into list of ints
 #            ints = map(int, clean)
            
 #                # remove all values > 4
 #            trim = [x for x in ints if x<5]
            
 #            # remove duplicates and sort
 #            trim = list(set(trim))
 #            trim.sort()
        
    # # handle parse
 #            # convert back to string with only alphabetical, 1-4 labels
 #            parse = re.sub(r"[^\w,^\d]","",str(parse))
 #            parse = parse.lstrip(',').rstrip(',')
            
 #            # correct parsed labels
 #            parse = parse.replace("HAND","")
 #            parse = parse.replace("RH","RH_")
 #            parse = parse.replace("RT","RH_")
 #            parse = parse.replace("RIGHT","RH_")
 #            parse = parse.replace("RGT","RH_")
 #            parse = parse.replace("LH","LH_")
 #            parse = parse.replace("LT","LH_")
 #            parse = parse.replace("LEFT","LH_")
 #            parse = parse.replace("LFT","LH_")
 #            parse = parse.replace("LEX","LH_EX")
 #            parse = parse.replace("REX","RH_EX")
 #            parse = parse.replace("LAUX","LH_AUX")
 #            parse = parse.replace("RAUX","RH_AUX")
            
 #            # remove duplicates and sort
 #            parse = parse.split(',')
 #            parse = list(set(parse))
 #            parse.sort()
            
    # # concatenate alphabetical labels to numeric positions to get single parsed list
 #            trim = trim+parse

 #            # convert back to string to remove []                       
 #            trim = ','.join(map(str, trim)).rstrip(',')
            
            
 #            # save values into df
 #            df.loc[i,'Parsed_Component_Position']=trim

 #            # if empty, check next narrative
 #            if df.loc[i,'Parsed_Component_Position'] != "":
 #                j = len(checks)
 #            else:
 #                j = j+1
                

    def extract_positions_single_narr_fqi(df, col):

        # search narratives for given patterns
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"(?:R\/?[HT]|RIGHT|L\/?[HT]|LEFT|LFT|RGT|R|L)\.? (?:HAND )?(?:AUX|EXT)", str(x)))
        df.loc[:, 'parsenum'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+", str(x)))

        # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
        df.loc[:, 'alpha'] = df.parse.apply(lambda x: re.sub(r"[^\w,^\d]","",str(x)))
        df.loc[:, 'num'] = df.parsenum.apply(lambda x: re.sub(r"[^\d,]","",str(x)))

        # convert strings into list of strings
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: x.split(','))
        df.loc[:, 'num'] = df.num.apply(lambda x: x.split(','))

        # remove empty strings from list, convert list of strings into list of ints, remove all values > 4 and < 1, remove duplicates and sort
        df.loc[:, 'num'] = df.num.apply(lambda x: map(int,filter(None, x)))

        df.loc[:, 'num'] = df.num.apply(lambda x: sorted(list(set([ii for ii in x if ii<5 and ii>0]))))

        # strip commas
        df.loc[:, 'alpha'] = df.alpha.apply(lambda l: [x.lstrip(',').rstrip(',') for x in l])

        # correct parsed labels
        parse_list = [("HAND",""), ("RH","RH_"), ("RT","RH_"), ("RIGHT","RH_"), ("RGT","RH_"), ("LH","LH_"), ("LT","LH_"), ("LEFT","LH_"), ("LFT","LH_"), ("LEX","LH_EX"), ("REX","RH_EX"), ("LAUX","LH_AUX"), ("RAUX","RH_AUX")]
        for tup in parse_list:
            df.loc[:, 'alpha'] = df.alpha.apply(lambda l: [x.replace(tup[0],tup[1]) for x in l])

        # remove duplicates and sort
        df.loc[:, 'alpha'] = df.alpha.apply(lambda l: sorted(list(set(l))))

        # concatenate alphabetical labels to numeric positions to get single parsed list (flatten list)
        df.loc[:, 'trim'] = df.apply(axis=1, func=lambda row: [kk for jj in (row.alpha, row.num) for kk in jj])

        # convert back to string to remove []
        df.loc[:, 'trim'] = df['trim'].apply(lambda x: ','.join(map(str, x)).lstrip(',').rstrip(','))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['trim']

        df.drop(['parse', 'parsenum','alpha', 'num'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]

    
    for j in checks:
        if df_fqi.loc[df_fqi.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_fqi(df_fqi.loc[df_fqi.Parsed_Component_Position.str.len()==0].copy(), j)
        df_fqi.update(df_sub)

    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_fqi.loc[df_fqi.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_fqi.loc[df_fqi.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']


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
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER |ECBU ?)\d+", x))

        # only SW entries can have multiple positions
        df.loc[(df.Action!='SW') & (df.parse.str.len()!=0), 'parse'] = df.loc[(df.Action!='SW') & (df.parse.str.len()!=0), 'parse'].apply(lambda x: x[0])

        # keep only numeric digits and comma separators
        df.loc[:, 'nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 13, duplicates and sort
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<14]))))

        # convert back to string to remove []
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)))

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


def CCU(df_ccu,libraries):
    df_ccu = df_ccu.copy()

    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative','Work_Center_Event_Narrative']
    
    #     # for each entry, search fields for component position numbers
    #     indexer = list(df.index.values)
    #     for i in indexer:
    # #     for i in range (0,len(df)):
    #         j = 0
    #         parse = []
    #         while j < len(checks):

    #             # search narratives for given patterns
    #             parse = re.findall(r"\d+A\d+|CENTER CONSOL|CNTR CONSOL|RTP|AUG(?:MENTED)? (?:(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L)?|(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L",str(df.loc[i,checks[j]]))

    #             # keep only alphabetical chars and comma separators
    #             parse = re.sub(r"[^\w,]","",str(parse))
    #             parse = re.sub(r"[\d]","",str(parse))

    #             # correct parsed labels
    #             parse = parse.replace('CUROSR','CURSOR')
    #             parse = parse.replace('CURSOR','CURSOR_')
    #             parse = parse.replace('CNTRL','CONTROL')
    #             parse = parse.replace('CNTL','CONTROL')
    #             parse = parse.replace('CNT','CONTROL')
    #             parse = parse.replace('CNTR','CONTROL')
    #             parse = parse.replace('CONTRL','CONTROL')
    #             parse = parse.replace('CNTROL','CONTROL')
    #             parse = parse.replace('PANEL','')
    #             parse = parse.replace('PNL','')
    #             parse = parse.replace('PANL','')
    #             parse = parse.replace('PNEL','')
    #             parse = parse.replace('CURSOR_CONTROL','CENTER')
    #             parse = parse.replace('CNTR','CENTER')
    #             parse = parse.replace('CONSOL','')
    #             parse = parse.replace('AUGMENTED','UG_CREW')
    #             parse = parse.replace('AUG','UG_CREW')
    #             parse = parse.replace('RTP','OTHER')
    #             parse = parse.replace('A','OTHER')
    #             parse = parse.replace('UG_CREW','AUG')
    #             parse = parse.replace('AUGCENTER','AUG')

    #             # remove duplicates and sort
    # #             parse = parse.strip()
    #             parse = parse.split(',')
    #             parse = list(set(parse))
    #             parse.sort()

    #             # convert back to string to remove []
    #             parse = ','.join(map(str, parse))

    #             # save values into df
    #             df.loc[i,'Parsed_Component_Position']=parse

    #             # if empty, check next narrative
    #             if df.loc[i,'Parsed_Component_Position'] != "":
    #                 j = len(checks)
    #             else:
    #                 j = j+1
                

    def extract_positions_single_narr_ccu(df, col):

        # search narratives for given patterns
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"\d+A\d+|CENTER CONSOL|CNTR CONSOL|RTP|AUG(?:MENTED)? (?:(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L)?|(?:CURSOR|CUROSR) CO?NTR?O?L? PA?NE?L", str(x)))

        # keep only alphabetical chars and comma separators to fix C-P, C/P etc.
        df.loc[:, 'alpha'] = df.parse.apply(lambda x: re.sub(r"[^A-Z,]","",str(x)))

        # correct parsed labels
        parse_list = [('CUROSR','CURSOR'), ('CURSOR','CURSOR_'), ('CNTRL','CONTROL'), ('CONTL','CONTROL'), ('CNTL','CONTROL'), ('CNT','CONTROL'), ('CNTR','CONTROL'), ('CONTRL','CONTROL'), ('CNTROL','CONTROL'), 
            ('PANEL',''), ('PNL',''), ('PANL',''), ('PNEL',''), ('CURSOR_CONTROL','CENTER'), ('CNTR','CENTER'), ('CONSOL',''), ('AUGMENTED','UG_CREW'), ('AUG','UG_CREW'), ('RTP','OTHER'),
            ('A','OTHER'), ('UG_CREW','AUG'), ('AUGCENTER','AUG')]
        
        for tup in parse_list:
            df.loc[:, 'alpha'] = df.alpha.apply(lambda x: x.replace(tup[0],tup[1]))

        # remove duplicates and sort
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: sorted(list(set(x.strip().split(',')))))

        # convert back to string to remove []
        df.loc[:, 'alpha'] = df.alpha.apply(lambda x: ','.join(map(str, x)))

        # save values into df
        df.loc[:,'Parsed_Component_Position'] = df['alpha']

        df.drop(['parse','alpha'], axis=1, inplace=True)

        # return matches
        return df[df.Parsed_Component_Position.str.len()>0]


    
    for j in checks:
        if df_ccu.loc[df_ccu.Parsed_Component_Position.str.len()==0].empty:
            # if all positions have been found then do nothing
            break

        # send df subset that has no matches to get a match
        df_sub = extract_positions_single_narr_ccu(df_ccu.loc[df_ccu.Parsed_Component_Position.str.len()==0].copy(), j)
        df_ccu.update(df_sub)

    # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
    df_ccu.loc[df_ccu.Parsed_Component_Position.str.len()==0, 'Parsed_Component_Position'] = \
        df_ccu.loc[df_ccu.Parsed_Component_Position.str.len()==0, 'Component_Position_Number']

    return df_ccu


def APU(df_apu,libraries):
    df_apu = df_apu.copy()

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
        df.loc[:, 'parse'] = df[col].apply(lambda x: re.findall(r"(?:\# ?|NO\.? |NUMBER )\d+|\bALL FOUR\b|\bALL 4\b", x))
        df.loc[:, 'parseapu'] = df[col].apply(lambda x: re.findall(r"APU", x))

        # keep only numeric digits and comma separators
        df.loc[:, 'nums'] = df['parse'].apply(lambda x: re.sub(r"[^\d,]","",str(x)))
        # convert string into list of strings
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: x.split(','))
        # remove empty strings from list
        # convert list of strings into list of ints
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: map(int, filter(None, x)))

        # remove all values > 4, duplicates and sort
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: sorted(list(set([ii for ii in x if ii<5]))))

        # add APU back into label
        df.loc[:, 'parseapu'] = df['parseapu'].apply(lambda x: list(set(x)))
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: map(str, x))
        df.loc[:, 'nums'] = df.apply(lambda row: row.nums + row.parseapu, 
                              axis=1)
        
        # convert back to string to remove []
        df.loc[:, 'nums'] = df['nums'].apply(lambda x: ','.join(map(str, x)).strip())

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


def VD(df,libraries):
    
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
            parse = re.findall(r"GEAR ?BOX|G[\/]?B|COMP(?:R[E ]SSOR)?|TURBINE?|GVIB|CVIB|TVIB",str(df.loc[i,checks[j]]))
            parsenum = re.findall(r"(?:\# ?|NO\.? ?|NUMBER |ENG(?:INE)? )\d+| ALL 4| ALL FOUR",str(df.loc[i,checks[j]]))
            
            # if we find string position but not numeric position (or vice versa), search the next narrative for a numeric/string position
            if parse and not parsenum:
                try:
                    parsenum = re.findall(r"(?:\# ?|NO\.? ?|NUMBER |ENG(?:INE)? )\d+|\bALL 4|\bALL FOUR",str(df.loc[i,checks[j+1]]))
                except:
                    parsenum = []
            if parsenum and not parse:
                try:
                    parse = re.findall(r"GEAR ?BOX|G[\/]?B|COMP(?:R[E ]SSOR)?|TURBINE?|GVIB|CVIB|TVIB",str(df.loc[i,checks[j+1]]))
                except:
                    parse = []
        
            # if both numeric and string found, standardize labels and save. Otherwise iterate through checks.
            if parsenum and parse:
            
            
                parsenum = [x.replace('ALL FOUR','1,2,3,4') for x in parsenum]
                parsenum = [x.replace('ALL 4','1,2,3,4') for x in parsenum]
                # keep only alphanumeric chars and comma separators
                
                
                parse = re.sub(r"[^\w,]","",str(parse))
                parsenum = re.sub(r"[^\d,]","",str(parsenum))

                # convert strings into list of strings
                split = [x for x in parsenum.split(',')]
                parse = [x for x in parse.split(',')]

        # handle parsenum/split

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
                parse = parse.replace("GB","GEARBOX")
                parse = parse.replace("GVIB","GEARBOX")
                parse = parse.replace("TVIB","TURBINE")
                parse = parse.replace("CVIB","COMPRESSOR")
                parse = parse.replace("COMPR SSOR","COMPRESSOR")
                parse = parse.replace("COMPRESSOR","C")
                parse = parse.replace("COMP","C")
                parse = parse.replace("TURBINE","T")
                parse = parse.replace("TURBIN","T")
                parse = parse.replace("GEARBOX","G")

                # remove duplicates and sort
                parse = parse.split(',')
                parse = list(set(parse))
                parse.sort()

        # concatenate alphabetical labels to numeric positions to get single parsed list

                # generate cross product for numbers and strings
                # 1,2 and gearbox,compressor -> gearbox_1,gearbox_2,compressor_1,compressor_2
                crossed = [str(y)+str(x) for x in parse for y in trim]

                # convert back to string to remove []                       
                crossed = ','.join(map(str, crossed)).rstrip(',')


                # save values into df
                df.loc[i,'Parsed_Component_Position']=crossed

            # if empty, check next narrative
            if df.loc[i,'Parsed_Component_Position'] != "":
                j = len(checks)
            else:
                j = j+1
                
            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position']==str(''):
            df.loc[i,'Parsed_Component_Position'] = str('0')
            

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
            
        elif qpa_i.Names=='pilot_adi,pilot_hsi,copilot_adi,copilot_hsi':
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

        elif qpa_i.Names=='1-4 ; compressor,gearbox,turbine':
            df_i = VD(df_thisqpa,libraries)
        
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