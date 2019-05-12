from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

hyd_pump_for_export = Table('hyd_pump_for_export', metadata, 

    Column('File_Name', String(255)),
    Column('On_Maint_Action_Key', Integer),
    Column('Work_Center_Event_Identifier'),
    Column('Sequence_Number', BigInteger),
    Column('Off_Maint_Action_Key', Integer),
    Column('Work_Order_Number', BigInteger),
    Column('Depot_Maint_Action_Key', Integer),
    Column('Equipment_Designator', String(9)),
    Column('Serial_Number', String(45)),
    Column('Job_Control_Number', String(9)),
    Column('Work_Unit_Code', String(45)),
    Column('Transaction_Date', Date),
    Column('Geographic_Location', String(4)),
    Column('Current_Operating_Time', Float),
    Column('Action_Taken_Code', String(6)),
    Column('ATC_Description', Text),
    Column('How_Malfunction_Code', Integer),
    Column('How_Malfunction_Class_Ind', Integer),
    Column('HMAL_Description', Text),
    Column('Type_Maintenance_Code', String(1)),
    Column('TM_Description', Text),
    Column('When_Discovered_Code', String(3)),
    Column('WD_Description', Text),
    Column('Discrepancy_Narrative', LONGTEXT),
    Column('Work_Center_Event_Narrative', LONGTEXT),
    Column('Corrective_Narrative', LONGTEXT)
)