from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

candidate_wucs_raw_removals = Table('candidate_wucs_raw_removals', metadata, 

    Column('On_Work_Order_Key', Integer, primary_key=True, autoincrement=False),
    Column('On_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Equipment_Designator', String(45), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=False, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
    Column('Job_Control_Number', String(9), primary_key=False, autoincrement=False),
    Column('Command', String(3), primary_key=False, autoincrement=False),
    Column('Geographic_Location', String(4), primary_key=False, autoincrement=False),
    Column('Organization', String(45), primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(5), primary_key=False, autoincrement=False),
    Column('WUC_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Transaction_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Start_Time', Integer, primary_key=False, autoincrement=False),
    Column('Stop_Time', Integer, primary_key=False, autoincrement=False),
    Column('Component_Position_Number', String(3), primary_key=False, autoincrement=False),
    Column('Type_Maintenance_Code', String(1), primary_key=False, autoincrement=False),
    Column('TMC_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Action_Taken_Code', String(1), primary_key=False, autoincrement=False),
    Column('ATC_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('When_Discovered_Code', String(1), primary_key=False, autoincrement=False),
    Column('WDC_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('How_Malfunction_Code', String(3), primary_key=False, autoincrement=False),
    Column('HMAL_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('How_Malfunction_Class_Ind', String(1), primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
)