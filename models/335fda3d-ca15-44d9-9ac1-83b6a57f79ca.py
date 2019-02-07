from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

ercm_wuc_list = Table('ercm_wuc_list', metadata, 

    Column('Work_Unit_Code', String(5), primary_key=False, autoincrement=False),
    Column('WUC_Noun', String(30), primary_key=False, autoincrement=False),
    Column('WUC_NIIN', String(9), primary_key=False, autoincrement=False),
    Column('WUC_Part_Number', String(25), primary_key=False, autoincrement=False),
    Column('System_Noun', String(70), primary_key=False, autoincrement=False),
    Column('System_WUC', String(5), primary_key=False, autoincrement=False),
    Column('MDS', String(5), primary_key=False, autoincrement=False),
    Column('Notes', LONGTEXT, primary_key=False, autoincrement=False),
)