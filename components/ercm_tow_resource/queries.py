# current component hours - used for suspensions
eng_hrs = (
'SELECT a.esn, greatest(a.eng_hrs, a.eng_hrs+(b.hstr_hrs - a.hstr_hrs)) as tsn '
'FROM '
'(SELECT left(hstrec_raw.NHA_SN, 9) as esn, hstrec_raw.SN as hstr_sn, hstrec_raw.NHA_HRS as eng_hrs, hstrec_raw.TSN as hstr_hrs FROM hstrec_raw '
'JOIN '
'(SELECT left(NHA_SN, 9) as esn, max(DATE_2410) as dt FROM hstrec_raw GROUP BY left(NHA_SN, 9)) x '
'ON x.esn=left(hstrec_raw.NHA_SN, 9) and x.dt=hstrec_raw.DATE_2410) a '
'JOIN (SELECT left(hs_193.SN, 9) as esn, hs_193.HSTR_SN as hstr_sn, hs_193.HSTR_HRS as hstr_hrs FROM hs_193 '
'JOIN '
'(SELECT left(SN, 9) as SN, max(DATE_193) as dt FROM army_aviation.hs_193 WHERE HSTR_HRS is not Null group by left(SN, 9)) x '
'ON x.dt = hs_193.DATE_193 and x.SN = left(hs_193.SN, 9)) b '
'ON b.esn = a.esn and b.hstr_sn = a.hstr_sn'
)

# select transactional maintenance data. 
# if removal and install on same day: 
#       order by any removal first, then any install.  w/in those codes, order by causal removal and used install last (w/in removal and install order) 
#       so they're saved in the interval
fetch_wuc = """SELECT * FROM stage_data_for_tow 
WHERE Work_Unit_Code = %s AND Action_Taken_Code in ('P', 'Q', 'T', 'U', 'IU') 
ORDER BY Serial_Number, Component_Position_Number, Transaction_Date, 
CASE WHEN Action_Taken_Code = 'T' then 1
			  WHEN Action_Taken_Code = 'P' then 2
              WHEN Action_Taken_Code IN ('Q', 'U') then 3
              WHEN Action_Taken_Code = 'IU' then 4
END, 
Work_Order_Number, Sequence_Number, Work_Center_Event_Identifier, On_Maint_Action_Key, Off_Maint_Action_Key, Depot_Maint_Action_Key"""