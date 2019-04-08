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

    for pred in predecessors:
        if 'compiled' in pred:
            compiled_table_name = pred
            break

    keys = list(pd.read_sql(sql="SHOW KEYS FROM remis_data", con=conn).Column_name)
    join_clause = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
    join_clause = ' AND '.join(join_clause)

    df = pd.read_sql(con=conn,sql="""SELECT A.*, B.Action_Taken_Code, B.Corrective_Narrative FROM clean_wuc_remove_fom A 
        LEFT JOIN {} B ON {}""".format(compiled_table_name, join_clause))

    # Search for R&R in Corrective Narrative, replace corresponding ATC with "R"
    Rs = df[df['Corrective_Narrative'].str.contains(pat=r"\br2\b|\br2\^d\b|\bremoved and replace|\br 2\b|\br&r\b|\br & r\b|\br and r\b|\br\+r\b|\br2d\b|\br2'd\b", na=False, flags=re.IGNORECASE)].index
    df.loc[Rs,'Action_Taken_Code'] = "R"
    # TODO: consider 'RXR'

    # Remove ATCs we are not interested in
    df = df[df.Action_Taken_Code.str.contains(r'R|P|Q|T|U')]

    keys.append('Action_Taken_Code')
    df = df[keys]
    
    return df    


