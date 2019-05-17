"""
Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in "" On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Action_Taken_Code, Parsed_Component_Position

    Returns:
        Data frame of On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Primary_Key_Index, Action_Taken_Code, Parsed_Component_Position
"""

def fn(conn, libraries, params, predecessors):
    pd = libraries["pandas"]
    re = libraries["re"]

    for pred in predecessors:
        if 'position' in pred:
            pred_position = pred
        else:
            pred_atc = pred
    
    atc_field = 'Action'
    
    keys = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(pred), con=conn).Column_name)
    join_clause = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
    join_clause = ' AND '.join(join_clause)

    df = pd.read_sql(con=conn,sql="""SELECT A.*, B.{} Action_Taken_Code FROM {} A 
        LEFT JOIN {} B ON {}""".format(atc_field, pred_position, pred_atc, join_clause))

    # Split all entries with ATC = R into ATC = P and ATC = Q for separate removal and replacement entries
    # take explicit dataframe copies, update subsets, then recombine
    df_Q = df[df['Action_Taken_Code'] == 'R'].copy()  
    df_P = df[df['Action_Taken_Code'] == 'R'].copy()
    df_not_R = df[df['Action_Taken_Code'] != 'R'].copy()
    df_Q['Action_Taken_Code'] = df_Q['Action_Taken_Code'].str.replace('R', 'Q')
    df_P['Action_Taken_Code'] = df_P['Action_Taken_Code'].str.replace('R', 'P')
    df = df_not_R.append([df_Q, df_P], ignore_index=False)  # duplicted records have same index in result

    # Split all entries with ATC = TU into ATC = T and ATC = U for separate CANN removal and replacement entries
    df_U = df[df['Action_Taken_Code'] == 'TU'].copy()
    df_T = df[df['Action_Taken_Code'] == 'TU'].copy()
    df_not_TU = df[df['Action_Taken_Code'] != 'TU'].copy()
    df_U['Action_Taken_Code'] = df_U['Action_Taken_Code'].replace('TU', 'U')
    df_T['Action_Taken_Code'] = df_T['Action_Taken_Code'].replace('TU', 'T')
    df = df_not_TU.append([df_U, df_T], ignore_index=False)

    # Split all entries with ATC = CC (replace with used part) into ATC = P and ATC = IU
    df_IU = df[df['Action_Taken_Code'] == 'CC'].copy()
    df_P = df[df['Action_Taken_Code'] == 'CC'].copy()
    df_not_CC = df[df['Action_Taken_Code'] != 'CC'].copy()
    df_IU['Action_Taken_Code'] = df_IU['Action_Taken_Code'].replace('CC', 'IU')
    df_P['Action_Taken_Code'] = df_P['Action_Taken_Code'].replace('CC', 'P')
    df = df_not_CC.append([df_IU, df_P])
    
    ## Split all entries with ATC = SW (swapped) into ATC = T and ATC = IU for all identified parts: 1 record into 4
    # if there's only one identified position for a swap, switch to ATC='O' to ignore
    df.loc[(df['Action_Taken_Code'] == 'SW') & \
           (df['Parsed_Component_Position'].\
            apply(lambda x: True if len(set(x.split(','))) == 1 else False)), 
          'Action_Taken_Code'] = 'O'
    # similar pattern to above
    df_IU = df[df['Action_Taken_Code'] == 'SW'].copy()
    df_T = df[df['Action_Taken_Code'] == 'SW'].copy()
    df_not_SW = df[df['Action_Taken_Code'] != 'SW'].copy()
    df_IU['Action_Taken_Code'] = df_IU['Action_Taken_Code'].str.replace('SW', 'IU')
    df_T['Action_Taken_Code'] = df_T['Action_Taken_Code'].str.replace('SW', 'T')
    df = df_not_SW.append([df_IU, df_T], ignore_index=False)

    # Split remaining multiple component positions into multiple entries with one component position
    # Parsed_Component_Position "1,2,3,4" becomes 4 entries with Parsed_Component_Position "1", "2", "3", "4" respectively
    s = df['Parsed_Component_Position'].str.split(',').apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = 'Parsed_Component_Position'
    df = df.drop(['Parsed_Component_Position'], axis=1)
    df = df.join(s)
    
    # delete duplicate entries created where Parsed_Component_Position "4,4" "2,2" etc
    # find entries with duplicated primary key, ATC, PCP
    cols = list(keys)
    cols.extend(['Action_Taken_Code', 'Parsed_Component_Position'])
    df['Duplicate'] = df.duplicated(subset = cols, keep='first')
    # Remove duplicate entries
    df = df[~df['Duplicate']]
    df = df.reset_index(drop=True) 
    
    # Find entries with duplicated primary key, append new 
    df.sort_values(by=keys, inplace=True)
    df['Duplicate'] = df.duplicated(subset = keys, keep='first')
    # For each row:
    #  if PK is equal to that of previous row, increment New_PK_Index by 1
    #  if not, set New_PK_Index to 1
    for i in range(0,len(df)):
        if df.loc[i, 'Duplicate']:
            df.loc[i, 'Primary_Key_Index'] = int(df.loc[i-1, 'Primary_Key_Index'])+1
        else:
            df.loc[i, 'Primary_Key_Index'] = 1
    
    df = df.drop(['Duplicate'],axis=1)
    df = df.reset_index(drop=True)

    return df