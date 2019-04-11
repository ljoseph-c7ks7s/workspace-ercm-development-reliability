"""
Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Corrective_Narrative, Discrepancy_Narrative, Component_Position_Number

    Returns:
        Data frame of On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Parsed_Component_Position
"""

def reader(df,libraries):
    pd = libraries["pandas"]
    re = libraries["re"]

    # define fields to check
    checks = ['Corrective_Narrative','Discrepancy_Narrative']

    # for each entry, search fields for component position numbers 
    for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):
            
            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("\#\d+|\# \d+|NO. \d+|NUMBER \d+|\bALL FOUR\b|\bALL 4\b",str(df.loc[i,checks[j]]))
            
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
            df.at[i,'Parsed_Component_Position']=remove
            
            # if empty, check next narrative
            if any(x.isdigit() for x in remove):
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df

def fn(conn, libraries, params, predecessors):

    pd = libraries["pandas"]
    re = libraries["re"]

    for pred in predecessors:
        if 'compiled' in pred:
            compiled_table_name = pred
        else:
            key_table_name = pred

    keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(key_table_name), con=conn).Column_name)
    join_clause = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
    join_clause = ' AND '.join(join_clause)

    df = pd.read_sql(con=conn,sql="""SELECT A.*, B.Discrepancy_Narrative, B.Corrective_Narrative, B.Component_Position_Number FROM identify_r2_drop_atc A 
        LEFT JOIN {} B ON {}""".format(compiled_table_name, join_clause))

    df['Parsed_Component_Position'] = ""
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)
    
    # change all provided,empty positions to 0
    df['Component_Position_Number'] = df['Component_Position_Number'].map(lambda x: 0 if not x.isdigit() else x)
    
    # run the reader function
    reader(df, libraries)
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)    

    #keep only needed columns to save memory
    keys.append('Parsed_Component_Position')
    df=df[keys]
    return df
