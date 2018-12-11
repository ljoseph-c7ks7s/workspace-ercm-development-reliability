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
    df = pd.read_sql(con=conn,sql="SELECT A.*, B.Action_Taken_Code FROM Part_Position_Parser A LEFT JOIN .Identify_R2 B ON A.On_Work_Order_Key=B.On_Work_Order_Key AND A.On_Maint_Action_Key=B.On_Maint_Action_Key AND A.Work_Center_Event_Identifier=B.Work_Center_Event_Identifier AND A.Sequence_Number=B.Sequence_Number AND A.Work_Order_Number=B.Work_Order_Number")


    #Split all entries with ATC = R into ATC = P and ATC = Q for separate removal and replacement entries
    df_Q = df[(df.loc[:,'Action_Taken_Code'] == 'R')]
    df_P = df[(df.loc[:,'Action_Taken_Code'] == 'R')]
    df_P.loc[:,'Action_Taken_Code'] = df_P.loc[:,'Action_Taken_Code'].replace("R","P")
    df_Q.loc[:,'Action_Taken_Code'] = df_Q.loc[:,'Action_Taken_Code'].replace("R","Q")
    df_not_R = df[(df.loc[:,'Action_Taken_Code'] != 'R')]
    df = df_not_R.append([df_Q,df_P])
    
    #Split multiple component positions into multiple entries with one component position
    #Parsed_Component_Position "1,2,3,4" becomes 4 entries with Parsed_Component_Position "1","2","3","4" respectively
    s = df['Parsed_Component_Position'].str.split(',').apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = 'Parsed_Component_Position'
    df = df.drop(['Parsed_Component_Position'],axis=1)
    df = df.join(s)
    
    #delete duplicate entries created where Parsed_Component_Position "4,4" "2,2" etc
    #find entries with duplicated primary key, ATC, PCP
    df["Duplicate"] = df.duplicated(subset = ['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Work_Order_Number','Action_Taken_Code','Parsed_Component_Position'],keep='first')
    #Remove duplicate entries
    df=df[~df['Duplicate']]
    df=df.reset_index(drop=True) 
    
    #Find entries with duplicated primary key, append new 
    df["Duplicate"] = df.duplicated(subset = ['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Work_Order_Number'],keep='first')
#     For each row:
#     if PK is equal to that of previous row, increment New_PK_Index by 1
#     if not, set New_PK_Index to 1
    for i in range(0,len(df)):
        if df.loc[i,'Duplicate']:
            df.loc[i,'Primary_Key_Index'] = int(df.loc[i-1,'Primary_Key_Index'])+1
        else:
            df.loc[i,'Primary_Key_Index'] = str("1")
    
    df=df.drop(['Duplicate'],axis=1)
    df=df.reset_index(drop=True)

    return df