from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

assigned_location = Table('assigned_location', metadata, 

    Column('Equipment_Designator', String(12), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=True, autoincrement=False),
    Column('Acceptance_Date', Date, primary_key=False, autoincrement=False),
    Column('Termination_Date', Date, primary_key=False, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
    Column('Assigned_Organization', String(12), primary_key=False, autoincrement=False),
    Column('Assigned_Command', String(3), primary_key=False, autoincrement=False),
    Column('Assigned_Geographic_Location_Name', String(45), primary_key=False, autoincrement=False),
    Column('Assigned_Geographic_Location_Code', String(4), primary_key=False, autoincrement=False),
    Column('Assigned_Start_Date', Date, primary_key=True, autoincrement=False),
    Column('Assigned_Stop_Date', Date, primary_key=False, autoincrement=False),
)