from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

labeled_multiclass_removal_id = Table('labeled_multiclass_removal_id', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=False),
    Column('Labels_File_Name', String(255), primary_key=False, autoincrement=False),
    Column('REMIS_File_Name', String(255), primary_key=False, autoincrement=False),
    Column('Model_Name', String(255), primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(5), primary_key=False, autoincrement=False),
    Column('Transaction_Date', Date, primary_key=False, autoincrement=False),
    Column('Geographic_Location', String(4), primary_key=False, autoincrement=False),
    Column('Action_Taken_Code', String(1), primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', LONGTEXT, primary_key=False, autoincrement=False),
    Column('train_test', String(45), primary_key=False, autoincrement=False),
    Column('label', String(45), primary_key=False, autoincrement=False),
    Column('prediction', String(45), primary_key=False, autoincrement=False),
    Column('Matches', String(5), primary_key=False, autoincrement=False)
)