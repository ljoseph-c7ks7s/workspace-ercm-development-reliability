def fn(conn, libraries, params, predecessors):
    """
        some of the wuc cells in the wuc list spreadsheet  have multiple wucs, like "22YFA/22YZA".  
        split these into multiple records so that each WUC gets its own row and all else is the same
        copies from Thomas's Split R Multi Position script
    """
    pd = libraries["pandas"]
    re = libraries["re"]

    df = pd.read_sql(con=conn,sql="""SELECT * FROM {}""".format(predecessors[0]))
 
    # applying the Series function creates new columns for each item in the list
    # stack creates a new row index with one value for each column
    s_wuc_split = df.Work_Unit_Code.apply(lambda x: x.split('/\n')).apply(pd.Series, 1).stack()

    # drop the new row-number index
    s_wuc_split.index = s_wuc_split.index.droplevel(-1)

    # assign a name, which will become the new column name when merged with the dataframe
    s_wuc_split.name = 'Work_Unit_Code'
    
    # drop original WUC and replace it with the new one
    df.drop(['Work_Unit_Code'], axis=1, inplace=True)
    df = df.join(s_wuc_split)
    
    return df
