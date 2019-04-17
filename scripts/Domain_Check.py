def domain_check(tm, wq, X, libraries):
    """ Calculates window value columns to determine what periods a flight record could be grouped into.
    Example: '2016-01-04' would return window values '2015-11-01', '2015-12-01', '2016-01-01'.
    Args:
        tm: date frame from previous function
        wq: currently only works where period = 3. Long-term, will try and make dynamic based on this value
        X: quantile for domain check (note: converted to percentage)
        libraries: dictionary of libraries; access by name
    Returns:
       windowed: data frame with window values where record is active
    """
    pd = libraries['pandas']

    # initialize output dataframe
    out = pd.DataFrame(index=[0], columns={'domain_check'})

    # compute fleet90_75 NOTE: this may require debug due to weird dict issue
    fleet90_75 = tm['Average_Flying_Hours'].quantile(X * .01)

    # keep only relevant columns from weibull quantiles
    wq = wq[['quantile', 'time']]

    # sort by quantile ascending and reset the index for later iteration
    wq_sort = wq.sort_values(by=['quantile'], axis=0).reset_index()

    # create an empty list for tracking incremental time
    incremental_time = []

    # convert the time column to a list
    time_list = list(wq_sort['time'])

    for i in range(1, len(time_list)):
        if i == 0:
            increment = time_list[i]
            incremental_time.append(increment)
        else:
            increment = time_list[i] - time_list[i - 1]
            incremental_time.append(increment)

    # compute min_inc_time
    min_inc_time = min(incremental_time)

    # determine if it fails the domain check
    if min_inc_time > fleet90_75:
        out.iloc[0]['domain_check'] = 'Fail'
    else:
        out.iloc[0]['domain_check'] = 'Pass'

    print("Domain check COMPLETE")

    return out


def fn(conn, libraries, params, predecessors):
    """
    Args:
        conn: connection to database for read access
        libraries: dictionary of libraries; access by name
        e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
        params: dictionary of additional parameters from component config (optional)
        predecessors: list of predecessor component names

    Returns:
        domain check results
    """
    pd = libraries["pandas"]

    # iterate through component list
    for pred in predecessors:
        if 'weibull' in pred:
            weibull_table_name = pred
        else:
            three_month_table_name = pred

    # load data from three month flight history collector
    query1 = "SELECT * FROM %s" % three_month_table_name
    three_month_flight_history = pd.read_sql(sql=query1, con=conn)

    # load data from single weibull quantities
    query2 = "SELECT * FROM %s WHERE type='tow_ci'" % weibull_table_name
    single_weibull_quantiles = pd.read_sql(sql=query2, con=conn)

    # grab parameter values
    X = params['X']  # default is 75
    df_out = domain_check(three_month_flight_history, single_weibull_quantiles, X, libraries)

    return df_out
