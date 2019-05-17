from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

assigned_location_snapshot = Table('assigned_location_snapshot', metadata, 

    Column('Equipment_Designator', String(12), primary_key=True, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=True, autoincrement=False),
    Column('MAJCOM', String(5), primary_key=False, autoincrement=False),
    Column('Assigned_Base', String(45), primary_key=False, autoincrement=False)
)