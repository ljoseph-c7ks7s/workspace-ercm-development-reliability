def fn(conn, libraries, params, predecessors):
    """
    Classify distributions if we'll use them to make forecasts or not
    
    objectives: 
        1) use the most specific distributions provided they're supported by enough data 
            and are significantly different that their peer distributions
        2) use weibull distribution unless the distribution fails the beta=1 test

    for each work unit code we can select either Any MDS or both C130H and C130J
    for each MDS we can select one time frame

    # TODO: support more than 2 MDS and other covariates

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

    preferred_distributions = params.get('preferred_distributions', False)

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

    # add preferred column, initially all false
    df_dist['Preferred'] = 0
    
    # save given preferred distributions if supplied
    if preferred_distributions:  # empty list is false as well

        df_dist.loc[df_dist.distribution_id.isin(preferred_distributions), 'Preferred'] = 1

        return df_dist

    ## otherwise perform automated classification
    # save original df for saving at the end
    df_dist_to_return = df_dist.copy()

    ## first replace weibulls with exponentials if beta test doesn't pass
    # can do this for all wucs at once
    removed_distributions_weibull_test = 0
    for ips in list(df_dist.interval_parameter_set_id.unique()):
        df_dist_one_ips = df_dist.loc[(df_dist.interval_parameter_set_id == ips), :].copy()
        if df_dist_one_ips.loc[(df_dist_one_ips.dist_name == 'weibull'), 'beta_eq_one_pval'].iloc[0] > 0.05:
            removed_distributions_weibull_test += 1
            df_dist.drop(df_dist_one_ips.loc[(df_dist_one_ips.dist_name == 'weibull'), :].index[0], axis=0, inplace=True)
        else:
            df_dist.drop(df_dist_one_ips.loc[(df_dist_one_ips.dist_name == 'exponential'), :].index[0], axis=0, inplace=True)
    print('removed {} weibull distributions for failing the beta=1 check (will use exponential)'.format(removed_distributions_weibull_test))

    # add columns to df to help SE comparisons
    # using 2 as approximation for 2-sided 95% confidence intervals
    #  (assuming normality of estimate, which is iffy)
    df_dist['eta_se_upper_ci'] = df_dist.apply(lambda row: row.eta + 2*row.eta_se, axis=1)
    df_dist['eta_se_lower_ci'] = df_dist.apply(lambda row: row.eta - 2*row.eta_se, axis=1)

    def exclude_based_on_time_frame(df):
        # returns indices to exclude based on ruled out by time frame / time period

        # use 5 years if 5 years is different than both 10 years and all years
        # use 10 years if above check doesn't pass and if 10 years is different than all years

        def compare_10_and_s04(df_s04, df_10yr):

            if df_s04.eta == df_10yr.eta:
                diff_10_s04 = False
            elif df_s04.eta > df_10yr.eta: 
                if df_s04.eta_se_lower_ci < df_10yr.eta_se_upper_ci:
                    diff_10_s04 = False
                else:
                    diff_10_s04 = True
            elif df_s04.eta < df_10yr.eta:
                if df_s04.eta_se_upper_ci > df_10yr.eta_se_lower_ci:
                    diff_10_s04 = False
                else:
                    diff_10_s04 = True
            
            if diff_10_s04:
                use = 'Removed_Last_10_Years'
            else: 
                use = 'Since 04'
            return use

        # if a WUC doesn't have any removals in the last 5 or 10 years there won't be a Weibull
        #   we have to catch these instances and handle them separately

        # retrieve one-row dfs as series
        df_s04 = df.loc[df.Time_Frame == 'Since 04', :].iloc[0]
        if len(df.loc[df.Time_Frame == 'Removed_Last_10_Years', :]) > 0:
            df_10yr = df.loc[df.Time_Frame == 'Removed_Last_10_Years', :].iloc[0]
        else:
            use = 'Since 04'
            print('WUC {} using {} because no other time frames'.format(df.Work_Unit_Code.iloc[0], use))
            assert df[df.Time_Frame != use].empty
            return df[df.Time_Frame != use].index
        if len(df.loc[df.Time_Frame == 'Removed_Last_5_Years', :]) > 0:
            df_5yr = df.loc[df.Time_Frame == 'Removed_Last_5_Years', :].iloc[0]
        else:
            use = compare_10_and_s04(df_s04, df_10yr)
            print('WUC {} using {}'.format(df.Work_Unit_Code.iloc[0], use))
            # return indices to exclude
            return df[df.Time_Frame != use].index


        if df_10yr.eta > df_5yr.eta: # e.g 2000 and 1500
            if df_10yr.eta_se_lower_ci < df_5yr.eta_se_upper_ci:  # e.g. 1800 & 1700
                diff_5_10 = False
            else:
                diff_5_10 = True
        elif df_10yr.eta < df_5yr.eta:
            if df_10yr.eta_se_upper_ci > df_5yr.eta_se_lower_ci:
                diff_5_10 = False
            else:
                diff_5_10 = True
        else:
            diff_5_10 = False
        if diff_5_10:
            # compare 5 and s04
            if df_s04.eta > df_5yr.eta: 
                if df_s04.eta_se_lower_ci < df_5yr.eta_se_upper_ci:
                    diff_5_s04 = False
                else:
                    diff_5_s04 = True
            elif df_s04.eta < df_5yr.eta:
                if df_s04.eta_se_upper_ci > df_5yr.eta_se_lower_ci:
                    diff_5_s04 = False
                else:
                    diff_5_s04 = True
            else:
                diff_5_s04 = False

        if diff_5_10 and diff_5_s04:
            use = 'Removed_Last_5_Years'
        else:
            # disqualify 5
            # compare 10 and s04
            use = compare_10_and_s04(df_s04, df_10yr)
            
        
        print('WUC {} using {}'.format(df.Work_Unit_Code.iloc[0], use))
        
        # return indices to exclude
        return df[df.Time_Frame != use].index

    def exclude_based_on_mds(df):
        # if J and H are different, use both. 
        #  otherwise, use MDS 
        #  (assume checks were made already to make sure there are both MDS)
        
        # returns indices to exclude based on ruled out by MDS

        # retrieve one-row dfs as series
        df_mds = df.loc[df.MDS != 'Any MDS']
        df_a = df_mds.iloc[0, :]
        df_b = df_mds.iloc[1, :]

        if df_b.eta > df_a.eta: # e.g 2000 and 1500
            if df_b.eta_se_lower_ci < df_a.eta_se_upper_ci:  # e.g. 1800 & 1700
                diff_a_b = False
            else:
                diff_a_b = True
        elif df_b.eta < df_a.eta:
            if df_b.eta_se_upper_ci > df_a.eta_se_lower_ci:
                diff_a_b = False
            else:
                diff_a_b = True
        else:
            diff_a_b = False
        
        if diff_a_b:
            print('WUC {} splitting by MDS'.format(df.Work_Unit_Code.iloc[0]))
            # return indices to exclude
            return df[df.MDS == 'Any MDS'].index
        else: 
            print('WUC {} not splitting by MDS'.format(df.Work_Unit_Code.iloc[0]))
            # return indices to exclude
            return df[df.MDS != 'Any MDS'].index

    # now loop through distributions and check Time Range and MDS
    for w in list(df_dist.Work_Unit_Code.unique()):
        
        df_single_wuc = df_dist.loc[df_dist.Work_Unit_Code == w, :].copy()

        # remove the unused rows from All MDS and any specific MDS
        indices_to_exclude = exclude_based_on_time_frame(df_single_wuc)
        df_single_wuc.drop(indices_to_exclude, axis=0, inplace=True)

        #  now compare MDS, but only if there are distributions to compare 
        #  (more than 2 distributions, which would be one-speicific WUC + Any MDS)
        if df_single_wuc[df_single_wuc.MDS != 'Any MDS'].shape[0] > 1:
            # compare MDS
            indices_to_exclude = exclude_based_on_mds(df_single_wuc)
            df_single_wuc.drop(indices_to_exclude, axis=0, inplace=True)
        else:
            # drop the specific-MDS distribution
            print('WUC {} has single MDS - use Any MDS'.format(df_single_wuc.iloc[0].Work_Unit_Code))
            df_single_wuc.drop(df_single_wuc[df_single_wuc.MDS != 'Any MDS'].index, axis=0, inplace=True)

        # distributions that remain are preferred
        df_single_wuc.Preferred = 1
        df_dist_to_return.update(df_single_wuc)

    return df_dist_to_return