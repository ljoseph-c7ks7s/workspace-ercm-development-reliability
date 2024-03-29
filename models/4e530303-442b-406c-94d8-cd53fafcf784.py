from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

remove_left_censored = Table('remove_left_censored', metadata, 

    Column('id', BigInteger, primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=False, autoincrement=False),
    Column('Component_Position_Number', Integer, primary_key=False, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('On_Work_Order_Key', Integer, primary_key=False, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=False, autoincrement=False),
    Column('On_Maint_Action_Key', Integer, primary_key=False, autoincrement=False),
    Column('INSTALL_Transaction_Date', Date, primary_key=False, autoincrement=False),
    Column('INSTALL_Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('TSN', Float, primary_key=False, autoincrement=False),
    Column('INSTALL_Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('REMOVAL_Transaction_Date', Date, primary_key=False, autoincrement=False),
    Column('REMOVAL_Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_How_Malfunction_Code', Integer, primary_key=False, autoincrement=False),
    Column('When_Discovered_Code', String(255), primary_key=False, autoincrement=False),
    Column('TOW', Float, primary_key=False, autoincrement=False),
)