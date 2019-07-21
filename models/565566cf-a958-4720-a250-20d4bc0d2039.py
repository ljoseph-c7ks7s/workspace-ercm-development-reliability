from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

location_translation = Table('location_translation', metadata, 

    Column('Base_Name_Snapshot', String(255), primary_key=False, autoincrement=False),
    Column('Base_Name_History', String(255), primary_key=False, autoincrement=False),
    Column('Location_Code', String(4), primary_key=True, autoincrement=False),
    Column('MAJCOM_Display', String(45), primary_key=False, autoincrement=False),
    Column('MAJCOM_Match', String(45), primary_key=False, autoincrement=False)
)