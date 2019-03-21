"""
Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
            e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

        Reads in " On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Corrective_Narrative, Action_Taken_Code "

    Returns:
        Data frame of " On_Maint_Action_Key, Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Action_Taken_Code "
"""
def fn(conn, libraries, params, predecessors):
    pd = libraries["pandas"]
    re = libraries["re"]

    keys = list(pd.read_sql(sql="SHOW KEYS FROM remis_data", con=conn).Column_name)
    join_clause = ['A.{} = B.{}'.format(ii,ii) for ii in keys]
    join_clause = ' AND '.join(join_clause)

    df = pd.read_sql(con=conn,sql="""SELECT A.*, B.Discrepancy_Narrative, B.Corrective_Narrative 
        FROM identify_r2_drop_atc A LEFT JOIN compiled_remis_data B ON {}""".format(join_clause))

    CANNdisc=df[df['Discrepancy_Narrative'].str.contains(pat=r"CANN\b|CANNED|CANN'D|CANIB|CANNIB|CANN:|CANND")]
    CANNcorr=df[df['Corrective_Narrative'].str.contains(pat=r"CANN\b|CANNED|CANN'D|CANIB|CANNIB|CANN:|CANND")]
    CANNdf=pd.concat([CANNdisc,CANNcorr]).drop_duplicates()

    # Where ATC = P, change ATC to T
    Ps=CANNdf[CANNdf['Action_Taken_Code']=="P"].index
    df.loc[Ps,'Action_Taken_Code']="T"

    # Where ATC = Q and CANN involved, change ATC to U
    Qs=CANNdf[CANNdf['Action_Taken_Code']=="Q"].index
    df.loc[Qs,'Action_Taken_Code']="U"

    #Filter dataframe to just R entries
    Rs=CANNdf[CANNdf['Action_Taken_Code']=="R"]
    keys = set(Rs[Rs['Action_Taken_Code']=='R']['Work_Order_Number'])
    #for each Work_Order_Number, check if each corrective narrative is unique
    for key in keys:
        Rkey=Rs[Rs['Work_Order_Number']==key]
        narrs=Rkey['Corrective_Narrative'].unique().tolist()
        if len(narrs)!=len(Rkey):
            #if not all unique, identify which corrective narrative is duplicated and change the two "R" entries into "T" and "U"
            #if there are more than two "R" entries, raise error
            for narr in narrs:
                if len(Rkey[Rkey['Corrective_Narrative']==narr])==2:
                    Rkey['local_index']=Rkey[Rkey['Corrective_Narrative']==narr].reset_index().index
                    df.loc[Rkey[Rkey['local_index']==0].index,'Action_Taken_Code']="T"
                    df.loc[Rkey[Rkey['local_index']==1].index,'Action_Taken_Code']="U"
                elif len(Rkey[Rkey['Corrective_Narrative']==narr])!=1:
                    raise ValueError("Too many duplicated R narratives: Work_Order_Number "+key+" has "+len(Rkey[Rkey['Corrective_Narrative']==narr])+" R's assigned to single corrective narrative")
    
    # Rs=CANNdf[CANNdf['Action_Taken_Code']=="R"]
    # df.loc[Rs,'Action_Taken_Code']="C"
    
    # for ATC=R with some indication of CANN - leave as R for now except above changes
    # could be several things that need more reasearch:
    # 1) cann removal (search narrative for "CANN ___ TO")
    # 2) cann install (search narrative for "CANN ___ FROM")
    #      > "CANN ___ FOR" is unclear. found a case where it was a cann install (kc135 SN 5800000010 part removed and installed into SN 6300008003, WUC 11360, 2015-08-04)
    # 3) true R2 for cause, so 'cann' in narrative is false positive
    # 4) removal for cause but replaced with cann'd part
    #       e.g. c130 sn 0800008606 jcn 173018771 wuc 61ae
    #       and kc135 SN 5800000047 JCN 152778976 wuc 11PAB - actually an ATC=S originally
    # there's also S's sometimes:

    df = df.drop(columns=['Discrepancy_Narrative','Corrective_Narrative'])
    
    return df 