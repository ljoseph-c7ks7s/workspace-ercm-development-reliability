def fn(conn, libraries, params, predecessors):
    """
        Remove duplicates
            use posting date to resolve which to keep
        
        Trim string columns

        Remove all-null columns
    """
     
    pd = libraries["pandas"]
    plotting = libraries["bokeh"]["plotting"]
    io = libraries["bokeh"]["io"]

    df = pd.read_sql(sql="""SELECT * FROM {} p WHERE Work_Order_Number IS NOT NULL AND 
        Sequence_Number IS NOT NULL AND Work_Center_Event_Identifier IS NOT NULL""".format(predecessors[0]), 
        con=conn,
        parse_dates='Posting_Date')
    original_row_count = df.shape[0]

    # Latest Posting Date at the start
    df.sort_values(by='Posting_Date', ascending=False, inplace = True)
    
    df.drop_duplicates(subset=['Work_Order_Number','Work_Center_Event_Identifier','Sequence_Number'],
                   keep='first', 
                   inplace=True)

    print('\nremoved {} of {} records'.format(original_row_count-df.shape[0], original_row_count))

    df_months = df.set_index('Posting_Date').groupby(pd.Grouper(freq='M')).size().reset_index()
    df_months.rename(columns={'Posting_Date':'Posting_Month', 0:'correction_count'}, inplace=True)

    p = plotting.figure(title="Corrections Across Time", 
        x_axis_type="datetime"
        )
    p.xaxis.axis_label = 'Posting Date'
    p.yaxis.axis_label = 'Corrections'
    p.title.text_font_size = '18pt'
    p.xaxis.axis_label_text_font_size = '12pt'
    p.yaxis.axis_label_text_font_size = '12pt'
    p.toolbar.logo = None
    p.line(x=df_months.Posting_Month,
        y=df_months.correction_count
        )

    io.save(p)

    return df