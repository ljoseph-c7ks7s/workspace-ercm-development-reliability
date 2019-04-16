from Range_Check import range_check

import pandas as pd

libraries = {'pandas':pd}

y = [0.15,0.16,0.17,0.19]
outdf = pd.DataFrame(index=[0],columns={'range_check'})

def test():	
	max_range = 0.3
	df_input = pd.read_csv('input.csv')
	df_output = pd.read_csv('output.csv')

	for i in range(0,4):
		Y = y[i]
		df = range_check(df_input,libraries,Y,max_range)
		outdf.iloc[0] = df_output.iloc[i]
		pd.testing.assert_frame_equal(df,outdf)
test()