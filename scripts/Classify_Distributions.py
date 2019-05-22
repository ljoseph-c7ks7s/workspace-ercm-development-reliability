def fn(conn, libraries, params, predecessors):
    """
    Classify distributions if we'll use them to make forecasts or not
    
    objectives: 
        1) use the most specific distributions provided they're supported by enough data 
            and are significantly different that their peer distributions
        2) use weibull distribution unless the distribution fails the beta=1 test

    for each work unit code we can select either Any MDS or both C130H and C130J
    for each MDS we can select one time frame

    Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
        e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

    Returns:
        denormalized distribution results with:
            1) whether we should use it or not
            2) result of range check
            3) result of domain check
    """
    pd = libraries["pandas"]

    preferred_distributions = params.get('preferred_distributions')

    # iterate through component list
    for pred in predecessors:
        if 'dist' in pred:
            weibull_table_name = pred
        elif 'domain' in pred:
            dc_table_name = pred
        else:
            rc_table_name = pred

    # load data from distributions and checks
    df_dist = pd.read_sql(sql="""SELECT dd.*, rc.Range_Check, dc.Domain_Check FROM {} dd JOIN {} rc ON rc.distribution_id = dd.distribution_id
        JOIN {} dc ON dc.distribution_id = dd.distribution_id""".format(weibull_table_name, rc_table_name, dc_table_name), 
        con=conn)

    df_dist['Preferred'] = 0
    df_dist.loc[df_dist.distribution_id.isin(preferred_distributions), 'Preferred'] = 1

    return df_dist
