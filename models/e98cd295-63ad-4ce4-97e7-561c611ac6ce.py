from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

rules_list = Table('rules_list', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=False),
    Column('type', String(55), primary_key=False, autoincrement=False),
    Column('level', String(55), primary_key=False, autoincrement=False),
    Column('rule', LONGTEXT, primary_key=False, autoincrement=False),
)