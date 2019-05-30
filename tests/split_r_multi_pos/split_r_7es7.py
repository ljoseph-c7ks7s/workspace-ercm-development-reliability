import pandas as pd
import re
keys = ["On_Maint_Action_Key","Work_Center_Event_Identifier","Sequence_Number","Off_Maint_Action_Key","Work_Order_Number","Depot_Maint_Action_Key","Primary_Key_Index"]

def splitter(df):
	# Split R entries into a P and a Q entry
	df_Q = df[(df.loc[:,'Action_Taken_Code'] == 'R')]
	df_P = df[(df.loc[:,'Action_Taken_Code'] == 'R')]
	df_P.loc[:,'Action_Taken_Code'] = df_P.loc[:,'Action_Taken_Code'].replace("R","P")
	df_Q.loc[:,'Action_Taken_Code'] = df_Q.loc[:,'Action_Taken_Code'].replace("R","Q")
	df_not_R = df[(df.loc[:,'Action_Taken_Code'] != 'R')]
	df = df_not_R.append([df_Q,df_P])
	
	# Split multiple component positions into multiple entries with one component position
	# Parsed_Component_Position "1,2,3,4" becomes 4 entries with Parsed_Component_Position "1","2","3","4" respectively
	s = df['Parsed_Component_Position'].str.split(',').apply(pd.Series, 1).stack()
	s.index = s.index.droplevel(-1)
	s.name = 'Parsed_Component_Position'
	df = df.drop(['Parsed_Component_Position'],axis=1)
	df = df.join(s)
	
	# Delete duplicate entries created where Parsed_Component_Position "4,4" "2,2" etc
	# Find entries with duplicated primary key, ATC, PCP
	cols = list(keys)
	cols.extend(['Action_Taken_Code', 'Parsed_Component_Position'])
	df["Duplicate"] = df.duplicated(subset = cols, keep='first')
	#Remove duplicate entries
	df=df[~df['Duplicate']]
	df=df.reset_index(drop=True) 
	
	# Find entries with duplicated primary key, append new 
	df.sort_values(by=keys, inplace=True)
	df["Duplicate"] = df.duplicated(subset = keys, keep='first')
#	 For each row:
#	 if PK is equal to that of previous row, increment New_PK_Index by 1
#	 if not, set New_PK_Index to 1
	for i in range(0,len(df)):
		if df.loc[i,'Duplicate']:
			df.loc[i,'Primary_Key_Index'] = int(df.loc[i-1,'Primary_Key_Index'])+1
		else:
			df.loc[i,'Primary_Key_Index'] = 1
	
	df=df.drop(['Duplicate'],axis=1)
	df=df.reset_index(drop=True)

	return df


def test():
	df_input = pd.read_csv('split.csv',dtype={'Primary_Key_Index':'int64','Component_Position_Number':'int64'})
	df_output = pd.read_csv('split_out.csv',dtype={"On_Maint_Action_Key":'int64',"Work_Center_Event_Identifier":'int64',"Sequence_Number":'int64',"Off_Maint_Action_Key":'int64',"Work_Order_Number":'int64',"Depot_Maint_Action_Key":'int64',"Primary_Key_Index":'int64','Component_Position_Number':'object','Parsed_Component_Position':'object'})
	df_in = splitter(df_input)
	pd.testing.assert_frame_equal(df_in, df_output)
test()