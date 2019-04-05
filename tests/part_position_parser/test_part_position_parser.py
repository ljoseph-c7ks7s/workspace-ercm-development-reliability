import re
import pandas as pd

checks = ['Corrective_Narrative','Discrepancy_Narrative']

def reader(df):
    # for each entry, search corrective,discrepancy narratives for component position numbers 
    for i in range (0,len(df)):
        j = 0
        parse = []
        while j < len(checks):
            
            # not included here - "ALL (insert number here)","ALL FOUR"
            parse = re.findall("\#\d+|\# \d+|NO. \d+|NUMBER \d+|\bALL FOUR\b|\bALL 4\b",str(df.loc[i,checks[j]]))
            
            # replace 'ALL' matches with numbers
            parse = [x.replace('ALL FOUR','1,2,3,4') for x in parse]
            parse = [x.replace('ALL 4','1,2,3,4') for x in parse]
            
            # keep only numeric digits and comma separators
            nums = re.sub("[^\d,]","",str(parse))
            
            # convert string into list of strings
            split = [x for x in nums.split(',')]
            
            # remove empty strings from list
            clean = filter(None, split)
            
            # convert list of strings into list of ints
            ints = map(int, clean)
            
            # remove all values > 4
            trim = [x for x in ints if x<5]
            
            # convert back to string to remove []
            remove = ','.join(map(str, trim))

            # save values into df
            df.at[i,'Parsed_Component_Position']=remove
            
            # if empty, check next narrative
            if any(x.isdigit() for x in remove):
                j = len(checks)
            else:
                j = j+1
                

            # if no information is found in the narratives, copy in the provided 'Component_Position_Number'
        if df.loc[i,'Parsed_Component_Position'] == str():
            df.loc[i,'Parsed_Component_Position'] = df.loc[i,'Component_Position_Number']

    return df

def fn(df):

    df['Parsed_Component_Position'] = ""
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)
    df['Component_Position_Number'] = df['Component_Position_Number'].astype(str)

    # change all provided,empty positions to 0
    df['Component_Position_Number'] = df['Component_Position_Number'].map(lambda x: 0 if not x.isdigit() else x)
    
    # run the reader function
    reader(df)
    df['Parsed_Component_Position'] = df['Parsed_Component_Position'].astype(str)  

    # keep only needed columns to save memory
    return df


def test():
    df_input = pd.read_csv('ppp.csv')
    df_output = pd.read_csv('ppp_out.csv',dtype={'Discrepancy_Narrative':'str','Corrective_Narrative':'str','Component_Position_Number':'object','Parsed_Component_Position':'object'})
    df = fn(df_input)
    df_input.update(df)
    pd.testing.assert_frame_equal(df_input, df_output)

test()
