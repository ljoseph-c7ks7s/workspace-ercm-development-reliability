from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

ercm_wuc_list = Table('ercm_wuc_list', metadata, 

    Column('MDS', String(45), primary_key=False, autoincrement=False),
    Column('System', String(255), primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('MESL', String(1), primary_key=False, autoincrement=False),
    Column('WUC_Noun', String(255), primary_key=False, autoincrement=False),
    Column('IPB_Description', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Item_Name', String(255), primary_key=False, autoincrement=False),
    Column('Part_Number', String(255), primary_key=False, autoincrement=False),
    Column('NSN', String(255), primary_key=False, autoincrement=False),
    Column('Transactions_2018', String(255), primary_key=False, autoincrement=False),
    Column('QPA', LONGTEXT, primary_key=False, autoincrement=False),
    Column('Notes', LONGTEXT, primary_key=False, autoincrement=False)
)