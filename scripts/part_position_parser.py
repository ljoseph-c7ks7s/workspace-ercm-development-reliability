def fn(conn=None, libraries=None, params=None, predecessors=None):
    """
    Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

    Returns:
        Data frame of "C 130 REMIS data" primary keys, Corrective_Narrative, WUC_Narrative, discrepancy_narrative, component_position_number, and parsed_component_position

    Side Effects:

    """

    #import bokeh as bk
    pd = libraries["pandas"]
    re = libraries["re"]
    bk = libraries["bokeh"]["plotting"]

    #read in table
    """
    host = 'localhost'
    port = 3306
    user = 'root'
    password = ''
    schema = 'workspace-ercm'
    uri_template_schema = 'mysql://%s:%s@%s:%s/%s'
    uri = uri_template_schema%(user, password, host, port, schema)
    mysql_engine = create_engine(uri)
    conn = mysql_engine.connect()
    """
    df = pd.read_sql(con=conn, sql="SELECT On_Work_Order_Key,On_Maint_Action_Key,Work_Center_Event_Identifier,Sequence_Number,Corrective_Narrative,Discrepancy_Narrative,Component_Position_Number FROM c130_remis_data where (work_unit_code LIKE '22FAA' OR work_unit_code LIKE '42DLA'  OR work_unit_code LIKE '44KB0' OR work_unit_code LIKE '22RBC' OR work_unit_code LIKE '22TBB' OR work_unit_code LIKE '22XCN' OR work_unit_code LIKE '22VDA' OR work_unit_code LIKE '22YAB' OR work_unit_code LIKE '72KA0' OR work_unit_code LIKE '72KH0' OR work_unit_code LIKE '82LC0' OR work_unit_code LIKE '526DA' OR work_unit_code LIKE '32525' OR work_unit_code LIKE '422A0' OR work_unit_code LIKE '453AS' OR work_unit_code LIKE '22GAB' OR work_unit_code LIKE '71GE0' OR work_unit_code LIKE '526DD')")
    
    #remove unwanted WUCs, columns; append empty column
    #df = df[df['Work_Unit_Code'].isin(['22FAA', '42DLA', '44KB0', '22RBC', '22TBB', '22XCN', '22VDA', '22YAB', '72KA0', '72KH0', '82LC0', '526DA', '32525', '422A0', '453AS', '22GAB', '71GE0', '526DD'])].reset_index()
    #col_list = ['On_Work_Order_Key','On_Maint_Action_Key','Work_Center_Event_Identifier','Sequence_Number','Corrective_Narrative','Discrepancy_Narrative','Component_Position_Number']
    #df = df[col_list]
    df['Parsed_Component_Position']= ""

    #search for position info in corr_narr or disc_narr, store in new column
    for i in range (0,len(df)):
        pounds = str()
        if  str(re.findall("\#[1-9]",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("\#[1-9]",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL [1-9]",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL [1-9]",df.loc[i,'Corrective_Narrative']))
            
        elif str(re.findall("ALL FOUR",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL FOUR",df.loc[i,'Corrective_Narrative']))
            
        elif str(re.findall("ALL THREE",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL THREE",df.loc[i,'Corrective_Narrative']))
            
        elif str(re.findall("ALL FIVE",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL FIVE",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL SIX",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL SIX",df.loc[i,'Corrective_Narrative']))
      
        elif str(re.findall("ALL SEVEN",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL SEVEN",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL EIGHT",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL EIGHT",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL NINE",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL NINE",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL TEN",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL TEN",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL ELEVEN",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL ELEVEN",df.loc[i,'Corrective_Narrative']))
        
        elif str(re.findall("ALL TWELVE",df.loc[i,'Corrective_Narrative'])) != '[]':
            pounds = str(re.findall("ALL TWELVE",df.loc[i,'Corrective_Narrative']))
        
        elif  str(re.findall("\#[1-9]",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("\#[1-9]",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL [1-9]",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL [1-9]",df.loc[i,'Discrepancy_Narrative']))
            
        elif str(re.findall("ALL FOUR",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL FOUR",df.loc[i,'Discrepancy_Narrative']))
            
        elif str(re.findall("ALL THREE",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL THREE",df.loc[i,'Discrepancy_Narrative']))
            
        elif str(re.findall("ALL FIVE",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL FIVE",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL SIX",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL SIX",df.loc[i,'Discrepancy_Narrative']))
      
        elif str(re.findall("ALL SEVEN",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL SEVEN",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL EIGHT",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL EIGHT",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL NINE",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL NINE",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL TEN",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL TEN",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL ELEVEN",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL ELEVEN",df.loc[i,'Discrepancy_Narrative']))
        
        elif str(re.findall("ALL TWELVE",df.loc[i,'Discrepancy_Narrative'])) != '[]':
            pounds = str(re.findall("ALL TWELVE",df.loc[i,'Discrepancy_Narrative']))
        
        
        #reformat string for ordering
        string1 = pounds.replace("ALL 2","1,2")
        string1 = string1.replace("ALL 3","1,2,3")
        string1 = string1.replace("ALL 4","1,2,3,4")
        string1 = string1.replace("ALL 5","1,2,3,4,5")
        string1 = string1.replace("ALL 6","1,2,3,4,5,6")
        string1 = string1.replace("ALL 7","1,2,3,4,5,6,7")
        string1 = string1.replace("ALL 8","1,2,3,4,5,6,7,8")
        string1 = string1.replace("ALL 9","1,2,3,4,5,6,7,8,9")
        string1 = string1.replace("THREE","1,2,3")
        string1 = string1.replace("FOUR","1,2,3,4")
        string1 = string1.replace("FIVE","1,2,3,4,5")
        string1 = string1.replace("SIX","1,2,3,4,5,6")
        string1 = string1.replace("SEVEN","1,2,3,4,5,6,7")
        string1 = string1.replace("EIGHT","1,2,3,4,5,6,7,8")
        string1 = string1.replace("NINE","1,2,3,4,5,6,7,8,9")
        string1 = string1.replace("TEN","1,2,3,4,5,6,7,8,9,10")
        string1 = string1.replace("ELEVEN","1,2,3,4,5,6,7,8,9,10,11")
        string1 = string1.replace("TWELVE","1,2,3,4,5,6,7,8,9,10,11,12")
        string1 = string1.replace("BOTH","1,2")
        string1 = string1.replace("\"","")
        string1 = string1.replace("\'","")
        string1 = string1.replace("#","")
        string1 = string1.replace("ALL","")
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
        string1 = string1.replace(",",";")
        df.loc[i,'Parsed_Component_Position']=string1

        #if 'Parsed_Component_Position' is empty, copy in 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']            

    return df