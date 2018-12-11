"""
Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in "" On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Corrective_Narrative, Action_Taken_Code

    Returns:
        Data frame of On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Action_Taken_Code
"""

def fn(conn, libraries, params, predecessors):
    pd = libraries["pandas"]
    re = libraries["re"]    
    df = pd.read_sql(con=conn,sql="SELECT A.*, B.Action_Taken_Code, B.Corrective_Narrative FROM Clean_WUC_Remove_FOM A LEFT JOIN Compiled_C130_REMIS_Data B ON A.On_Work_Order_Key=B.On_Work_Order_Key AND A.On_Maint_Action_Key=B.On_Maint_Action_Key AND A.Work_Center_Event_Identifier=B.Work_Center_Event_Identifier AND A.Sequence_Number=B.Sequence_Number AND A.Work_Order_Number=B.Work_Order_Number")


    #Search for R&R in Corrective Narrative, replace corresponding ATC with "R"
    Rs = df[df['Corrective_Narrative'].str.contains(pat="r2 |removed and replace| r 2 |r&r |r & r |r and r |r+r |r2d ",flags=re.IGNORECASE)].index
    df.loc[Rs,'Action_Taken_Code'] = "R"

    #Search for R&R at beginning of Corrective Narrative, replace corresponding ATC with "R"
    Rs = df[df['Corrective_Narrative'].str.startswith("r 2 ","R 2 ")].index
    df.loc[Rs,'Action_Taken_Code'] = "R"

    df=df[['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Work_Order_Number','Action_Taken_Code']]
    return df    

