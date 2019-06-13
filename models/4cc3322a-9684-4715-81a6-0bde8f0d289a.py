from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table, UniqueConstraint

metadata = MetaData()

remove_unk_position_number = Table('remove_unk_position_number', metadata, 

    
    Column('Work_Unit_Code', String(45), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=False, autoincrement=False),
    Column('Component_Position_Number', String(45), primary_key=False, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=False, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=False, autoincrement=False),
    Column('INSTALL_Transaction_Date', Date, primary_key=False, autoincrement=False),
    #Column('INSTALL_TIME', Integer, primary_key=False, autoincrement=False),
    Column('INSTALL_TSN', Float, primary_key=False, autoincrement=False),
    Column('INSTALL_Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('INSTALL_Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('REMOVAL_Transaction_Date', Date, primary_key=False, autoincrement=False),
    #Column('REMOVAL_TIME', Integer, primary_key=False, autoincrement=False),
    Column('REMOVAL_TSN', Float, primary_key=False, autoincrement=False),
    Column('REMOVAL_Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_How_Malfunction_Code', Integer, primary_key=False, autoincrement=False),
    Column('REMOVAL_When_Discovered_Code', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_Cause', String(255), primary_key=False, autoincrement=False),
    Column('TOW', Float, primary_key=False, autoincrement=False),
    Column('spans_unknown_install', TINYINT, primary_key=False, autoincrement=False),
    Column('spans_unknown_removal', TINYINT, primary_key=False, autoincrement=False),
    Column('unk_removal_date_earliest', Date, primary_key=False, autoincrement=False),
    Column('unk_removal_tsn_earliest', Float, primary_key=False, autoincrement=False),
    Column('true_install_date', Date, primary_key=False, autoincrement=False),
    Column('true_install_tsn', Float, primary_key=False, autoincrement=False),
    Column('id', BigInteger, primary_key=True, autoincrement=True)
)