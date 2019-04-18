"""

Args:
		conn: connection to database for read access
		libraries: dictionary of libraries; access by name
			e.g. pd = libraries['pandas'] or stats = libraries['scipy']['stats']
		params: dictionary of additional parameters from component config
		predecessors: list of predecessor component names

		Reads in single_weibull_quantiles data

	Returns:
		table with single column 'range_check' and values pass/fail
"""

def range_check(df,libraries,Y,max_range):
	pd = libraries["pandas"]

	# initialize output dataframe
	out = pd.DataFrame(index=[0],columns={'range_check'})

	# compute and test spreads
	CI_spread_Y = df.loc[int(Y*100)-1]['ucl']-df.loc[int(Y*100)-1]['lcl']
	CI_spread_compY = df.loc[100-int(Y*100)-1]['ucl']-df.loc[100-int(Y*100)-1]['lcl']

	
	if (CI_spread_Y or CI_spread_compY) > max_range:
		out.iloc[0]['range_check'] = 'Fail'
	else:
		out.iloc[0]['range_check'] = 'Pass'
	return out


def fn(conn, libraries, params, predecessors):
	pd = libraries["pandas"]

	# load data
	query = "SELECT * FROM %s WHERE type='quantile_ci'" % predecessors[0]
	df = pd.read_sql(sql = query, con = conn)

	# grab parameter values
	Y = params['Y']
	max_range = params['max_range']
	
	df_out = range_check(df,libraries,Y,max_range)

	return df_out