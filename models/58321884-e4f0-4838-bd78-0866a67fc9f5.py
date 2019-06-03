from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

wuc_list_qpa = Table('wuc_list_qpa', metadata, 

    Column('Work_Unit_Code', String(5), primary_key=False, autoincrement=False),
    Column('Alternate_WUC', String(45), primary_key=False, autoincrement=False),
    Column('MDS', String(7), primary_key=False, autoincrement=False),
    Column('Minimum_SN_Inclusive', String(10), primary_key=False, autoincrement=False),
    Column('Maximum_SN', String(10), primary_key=False, autoincrement=False),
    Column('QPA', Integer, primary_key=False, autoincrement=False),
    Column('QPA_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Clues', String(255), primary_key=False, autoincrement=False),
    Column('Names', String(255), primary_key=False, autoincrement=False)
)