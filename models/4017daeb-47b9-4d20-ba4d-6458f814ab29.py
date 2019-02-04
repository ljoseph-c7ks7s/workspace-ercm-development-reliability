from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

one_wuc = Table('one_wuc', metadata, 

    Column('work_unit_code', String(255), primary_key=False, autoincrement=False),
    Column('transaction_date', DateTime, primary_key=False, autoincrement=False),
    Column('discrepancy_narrative', TEXT, primary_key=False, autoincrement=False),
    Column('action_Taken_code', String(255), primary_key=False, autoincrement=False),
)