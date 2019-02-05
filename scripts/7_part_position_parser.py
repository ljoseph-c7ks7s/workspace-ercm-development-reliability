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


    #For each entry, search corrective,discrepancy narratives for component position numbers 
    for i in range (0,len(df)):
    pounds = []

    #For each entry, search corrective narrative for component position numbers
        if re.findall("\#[1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("\#[1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\#[1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("\#[1-9][0-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bALL [1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("ALL [1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bALL [1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("ALL [1-9][0-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bALL FOUR",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("ALL FOUR",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bALL THREE",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("ALL THREE",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bNO [1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("NO [1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bNO [1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("NO [1-9][0-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bNO. [1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("NO. [1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\bNO. [1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("NO. [1-9][0-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\# [1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("\# [1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("\# [1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds = re.findall("\# [1-9][0-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("NUMBER [1-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds =  re.findall("NUMBER [1-9]",df.loc[i,'Corrective_Narrative'])

        elif re.findall("NUMBER [1-9][0-9]",df.loc[i,'Corrective_Narrative']) != []:
                pounds =  re.findall("NUMBER [1-9][0-9]",df.loc[i,'Corrective_Narrative'])
            
    #if no information is found in the corrective narrative, search discrepancy narrative
        elif re.findall("\#[1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("\#[1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\#[1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("\#[1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bALL [1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("ALL [1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bALL [1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("ALL [1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bALL FOUR",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("ALL FOUR",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bALL THREE",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("ALL THREE",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bNO [1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("NO [1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bNO [1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("NO [1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bNO. [1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("NO. [1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\bNO. [1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("NO. [1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\# [1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("\# [1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("\# [1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds = re.findall("\# [1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("NUMBER [1-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds =  re.findall("NUMBER [1-9]",df.loc[i,'Discrepancy_Narrative'])

        elif re.findall("NUMBER [1-9][0-9]",df.loc[i,'Discrepancy_Narrative']) != []:
                pounds =  re.findall("NUMBER [1-9][0-9]",df.loc[i,'Discrepancy_Narrative'])

    #reformat string for ordering
    string1 = str(pounds)
    string1 = string1.replace("ALL 3","1,2,3")
    string1 = string1.replace("ALL 4","1,2,3,4")
    string1 = string1.replace("ALL THREE","1,2,3")
    string1 = string1.replace("ALL FOUR","1,2,3,4")
    string1 = string1.replace("\"","")
    string1 = string1.replace("\'","")
    string1 = string1.replace("#","")
    string1 = string1.replace("NUMBER","")
    string1 = string1.replace("NO.","")
    string1 = string1.replace("NO","")
    string1 = string1.replace(" ","")
    string1 = string1.replace("[","")
    string1 = string1.replace("]",",")
    string1 = string1.strip(',')

    #order numbers and reformat for output
    string1 = str(sorted(string1.split(',')))
    string1 = string1.replace("[","")
    string1 = string1.replace("\'","")
    string1 = string1.replace(" ","")
    string1 = string1.replace("]","")
    df.loc[i,'Parsed_Component_Position']=string1

    #if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']
    return df

def fn(conn, libraries, params, predecessors):

    pd = libraries["pandas"]
    re = libraries["re"]
    df = pd.read_sql(con=conn,sql="SELECT A.*, B.Discrepancy_Narrative, B.Corrective_Narrative, B.Component_Position_Number FROM clean_wuc_remove_fom A LEFT JOIN compiled_c130_remis_data B ON A.On_Work_Order_Key=B.On_Work_Order_Key AND A.On_Maint_Action_Key=B.On_Maint_Action_Key AND A.Work_Center_Event_Identifier=B.Work_Center_Event_Identifier AND A.Sequence_Number=B.Sequence_Number AND A.Work_Order_Number=B.Work_Order_Number")
    df['Parsed_Component_Position']= ""
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)

    #change all provided,empty positions to 0
    df['Component_Position_Number'] = df['Component_Position_Number'].map(lambda x: 0 if not x.isdigit() else x)
    
    #run the reader function
    reader(df,libraries)
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    
    #remove any non-numeric characters captured at A or B
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].map(lambda x: x[:-1] if not x[-1:].isdigit() else x)
    

    #keep only needed columns to save memory
    df=df[['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Work_Order_Number','Parsed_Component_Position']]
    return df
