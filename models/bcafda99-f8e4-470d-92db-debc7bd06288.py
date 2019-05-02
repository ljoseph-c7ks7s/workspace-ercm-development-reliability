from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

qpa = Table('qpa', metadata, 

    Column('Action_Code', String(255), primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=True, autoincrement=False),
    Column('Work_Unit_Code', String(5), primary_key=True, autoincrement=False),
    Column('Block_Number', String(255), primary_key=False, autoincrement=False),
    Column('Start_Date', Date, primary_key=True, autoincrement=False),
    Column('Type_Equipment', String(1), primary_key=False, autoincrement=False),
    Column('Serially_Tracked_Ind', String(1), primary_key=False, autoincrement=False),
    Column('Failure_Limit', Integer, primary_key=False, autoincrement=False),
    Column('Replacement_Ind', String(1), primary_key=False, autoincrement=False),
    Column('NRTS_Ind', String(1), primary_key=False, autoincrement=False),
    Column('Usage_Factor', Integer, primary_key=False, autoincrement=False),
    Column('Action_Limit', Integer, primary_key=False, autoincrement=False),
    Column('Qty_Per_Applic', Integer, primary_key=False, autoincrement=False),
    Column('Special_Inventory', Integer, primary_key=False, autoincrement=False),
    Column('Cat_Of_Failure_Ind', String(1), primary_key=False, autoincrement=False),
    Column('Insp_Requirement', String(255), primary_key=False, autoincrement=False),
    Column('Pub_Date', Date, primary_key=False, autoincrement=False),
    Column('Stop_Date', Date, primary_key=False, autoincrement=False),
    Column('Original_WUC', String(5), primary_key=False, autoincrement=False),
    Column('Cascade_To_New_WUC', String(5), primary_key=False, autoincrement=False),
    Column('Description', TEXT, primary_key=False, autoincrement=False),
    Column('Cascaded_By', String(255), primary_key=False, autoincrement=False),
    Column('Effective_Date', Date, primary_key=False, autoincrement=False),
    Column('Messages', String(255), primary_key=False, autoincrement=False)
)