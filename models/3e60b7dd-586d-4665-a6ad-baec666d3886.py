from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

sort_rules_list = Table('sort_rules_list', metadata, 

    Column('level', String(55), primary_key=False, autoincrement=False),
    Column('rule', LONGTEXT, primary_key=False, autoincrement=False),
)