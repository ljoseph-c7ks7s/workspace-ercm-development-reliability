def fn(conn, libraries, params, predecessors):
    """
        Merge sortie flight hours and REMIS data, attach accumulated age data to REMIS
    """

    pd = libraries["pandas"]
    np = libraries["numpy"]
    plotting = libraries["bokeh"]["plotting"]
    layouts = libraries["bokeh"]["layouts"]

    if len(predecessors) != 3:
        raise Exception, 'component requires three predecessors'

    for pred in predecessors:
        if 'sortie' in pred:
            sortie_table = pred
        elif 'compiled' in pred:
            remis_table = pred
        else:
            filter_table = pred

    # Filter raw REMIS based on WUC and ATC filters
    # Convert transaction date to timestamp using Start Time
    # primary_key_fields_list = list(pd.read_sql(sql="SHOW KEYS FROM {}".format(filter_table), con=conn).Column_name)
    primary_key_fields_list = ['Work_Order_Number', 'Work_Center_Event_Identifier', 'Sequence_Number'] # hard code list of keys
    join_clause = ['remis.{} = filters.{}'.format(ii,ii) for ii in primary_key_fields_list]
    join_clause = ' AND '.join(join_clause)
    select_clause = ['filters.{}'.format(ii) for ii in primary_key_fields_list]
    select_clause = ', '.join(select_clause)
    # convert transaction date to datetime
    remis_query = """SELECT {}, remis.Serial_Number, DATE_FORMAT(
        CONCAT(transaction_date, " ", LEFT(LPAD(start_time, 4, '0'), 2), ":", RIGHT(LPAD(start_time, 4, '0'),2), ":00"), "%%Y-%%m-%%d %%T"
        ) Transaction_Date FROM {} remis JOIN {} filters ON {}""".format(select_clause, remis_table, filter_table, join_clause)

    df_remis = pd.read_sql(con=conn,sql=remis_query, parse_dates=["Transaction_Date"])
    df_sortie = pd.read_sql(con=conn,sql="""SELECT Serial_Number, Depart_Date, Flying_Hours, 
        Sorties_Flown, Total_Landings, Full_Stop_Landings FROM {}""".format(sortie_table), parse_dates=["Depart_Date"])

    # find most recent sortie depart date before each remis transaction date (by serial number)
    # loop through SNs and use merge_asof to find nearest depart date before the transaction dates
    df_sns = {}
    for sn in df_remis.Serial_Number.unique():
        
        df_sortie_subset = df_sortie[df_sortie.Serial_Number==sn]\
        .loc[:, ['Depart_Date','Flying_Hours', 'Sorties_Flown','Total_Landings','Full_Stop_Landings']]\
        .sort_values('Depart_Date')

        df_remis_single_sn = pd.merge_asof(df_remis[df_remis.Serial_Number==sn].sort_values('Transaction_Date'), 
                                           df_sortie_subset, left_on='Transaction_Date', right_on='Depart_Date')
        
        df_sns[sn] = df_remis_single_sn

    df_remis = pd.concat(df_sns.values())

    # drop records without flight hour info
    df_remis = df_remis[~df_remis['Flying_Hours'].isna()]

    df_remis.rename(columns={"Flying_Hours":"Current_Operating_Time"}, inplace=True)

    # select columns for export
    cols_to_return = list(primary_key_fields_list)
    cols_to_return.extend(['Current_Operating_Time', 'Sorties_Flown', 'Total_Landings','Full_Stop_Landings'])
    
    # plot accumulated flight hours by serial number and date
    p = plotting.figure(title="Accumulated Flight Hours by Serial Number and Maintenance Date", x_axis_type='datetime')
    p.xaxis.axis_label = 'Maintenance Transaction Date'
    p.yaxis.axis_label = 'Accumulated Aircraft Flight Hours Since Sirst Sortie (Starting 2004)'

    for name, group in df_remis.groupby('Serial_Number'):
        p.line(x=group.Transaction_Date, y=group.Current_Operating_Time, alpha=0.5)

    plotting.save(p)

    return df_remis[cols_to_return]