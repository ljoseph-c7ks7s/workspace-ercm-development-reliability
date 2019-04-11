"""
____________________________________________________________________________________________________________________________________

Do not use this for kc135 it crashes studio
____________________________________________________________________________________________________________________________________

Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in "" On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Work_Unit_Code, Work_Center_Event_Narrative, Discrepancy_Narrative, Corrective_Narrative

    Returns:
        Data frame of On_Work_Order_Key, On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number
"""

def fn(conn, libraries, params, predecessors):
    pd = libraries["pandas"]
    re = libraries["re"]
    df = pd.read_sql(con=conn,sql="SELECT A.*, B.Serial_Number, B.Work_Center_Event_Narrative, B.Corrective_Narrative, B.Discrepancy_Narrative FROM wuc_edits A LEFT JOIN compiled_c130_remis_data B ON A.On_Work_Order_Key=B.On_Work_Order_Key AND A.On_Maint_Action_Key=B.On_Maint_Action_Key AND A.Work_Center_Event_Identifier=B.Work_Center_Event_Identifier AND A.Sequence_Number=B.Sequence_Number AND A.Work_Order_Number=B.Work_Order_Number")
    pd = libraries["pandas"]

    print("The number of rows to start is: "+str(len(df)))
    #Import pandas as pd
    #Find all entries in our list of WUCs for analysis 
    keepers = df[df['Work_Unit_Code'].str.contains(pat="22FAA|42DLA|44KB0|22RBC|22TBB|22XCN|22VDA|22YAB|72KA0|72KH0|82LC0|526DA|32525|422A0|453AS|22GAB|71GE0|526DD|41300|49KB0|22VDC|64BAD|5114K|526DA",na=False)].index    
    #Remove all other entries
    df = df.loc[keepers]
    print("The number of rows after removing WUCs is: "+str(len(df)))
    
    #Find all entries without FOM in narrative text
    keepum = df[~(df['Work_Center_Event_Narrative'].str.contains(pat=r"\bF\.O\.M\b|\bFOM\b|f[aeiou]c[aeiou]l+[aeiou]t[aeiou]t"))&
               ~(df['Discrepancy_Narrative'].str.contains(pat=r"\bF\.O\.M\b|\bFOM\b|f[aeiou]c[aeiou]l+[aeiou]t[aeiou]t"))&
               ~(df['Corrective_Narrative'].str.contains(pat=r"\bF\.O\.M\b|\bFOM\b|f[aeiou]c[aeiou]l+[aeiou]t[aeiou]t"))].index
    #Remove all other entries
    df=df.loc[keepum]
    print("The number of rows after removing FOMs is: "+str(len(df)))

    # Find entries without 'entered in error' in corrective narrative
    print("Entered in Error entries to remove: {}".format([df[df['Corrective_Narrative'].str.contains(pat=r'[AEIOU]NT\w*\s+[AEIOU]N\s+ER(R)?[AEIOU]R', na=False)]['Corrective_Narrative'].str.extract(pat=r'([AEIOU]NT\w*\s+[AEIOU]N\s+ER(R)?[AEIOU]R)')][0][0].unique()))
    keepers = df[~df['Corrective_Narrative'].str.contains(pat=r'[AEIOU]NT\w*\s+[AEIOU]N\s+ER(R)?[AEIOU]R', na=False)].index
    #Remove all other entries
    df=df.loc[keepers]
    print("The number of rows after removing ENTERED IN ERROR is: "+str(len(df)))

    # Find entries without 'duplicate' in corrective narrative
    print("Duplicate Entry entries to remove: {}".format([df[df['Corrective_Narrative'].str.contains(pat=r'(WRITE(\s+|-)UP|DISCR\w*)\s+DUPL\w*|DUPL\w*\s+(TAG|ENT\w*|DISCR\w*|WRITE-UP|WRITE UP)', na=False)]['Corrective_Narrative'].str.extract(pat=r'((WRITE(\s+|-)UP|DISCR\w*)\s+DUPL\w*|DUPL\w*\s+(TAG|ENT\w*|DISCR\w*|WRITE-UP|WRITE UP))')][0][0].unique()))
    keepers = df[~df['Corrective_Narrative'].str.contains(pat=r'(WRITE(\s+|-)UP|DISCR\w*)\s+DUPL\w*|DUPL\w*\s+(TAG|ENT\w*|DISCR\w*|WRITE-UP|WRITE UP)', na=False)].index
    #Remove all other entries
    df=df.loc[keepers]
    print("The number of rows after removing DUPLICATE ENTRY is: "+str(len(df)))

    # Find entries with serial numbers
    keepers = df[~df['Serial_Number'].isna()].index
    #Remove all other entries
    df=df.loc[keepers]
    print("The number of rows after removing NULL Serial Numbers is: "+str(len(df)))

    #Remove all columns but primary keys for export
    df=df[['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Work_Order_Number']]
    df=df.reset_index(drop=True)
    return df