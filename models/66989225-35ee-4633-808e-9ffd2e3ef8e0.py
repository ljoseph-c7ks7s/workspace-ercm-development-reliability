from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

labels_import = Table('labels_import', metadata, 

    Column('__id', BigInteger, primary_key=True, autoincrement=True),
    Column('File_Name', String(255), primary_key=False, autoincrement=False),
    Column('On_Maint_Action_Key', Integer, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=False, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('Off_Maint_Action_Key', Integer, primary_key=False, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('Depot_Maint_Action_Key', Integer, primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('Job_Control_Number', String(255), primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('Transaction_Date', Date, primary_key=False, autoincrement=False),
    Column('Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
    Column('Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('ATC_Description', TEXT, primary_key=False, autoincrement=False),
    Column('How_Malfunction_Code', Integer, primary_key=False, autoincrement=False),
    Column('How_Malfunction_Class_Ind', Integer, primary_key=False, autoincrement=False),
    Column('HMAL_Description', TEXT, primary_key=False, autoincrement=False),
    Column('Type_Maintenance_Code', String(255), primary_key=False, autoincrement=False),
    Column('TM_Description', TEXT, primary_key=False, autoincrement=False),
    Column('When_Discovered_Code', String(255), primary_key=False, autoincrement=False),
    Column('WD_Description', TEXT, primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Action', String(255), primary_key=False, autoincrement=False),
    Column('Position', String(255), primary_key=False, autoincrement=False),
    Column('Removal_Cause', String(255), primary_key=False, autoincrement=False),
)