from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

wuc_list = Table('wuc_list', metadata, 

    Column('Platform', String(55), primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(5), primary_key=False, autoincrement=False),
    Column('WUC_Noun', String(55), primary_key=False, autoincrement=False),
    Column('Notes', LONGTEXT, primary_key=False, autoincrement=False),
)