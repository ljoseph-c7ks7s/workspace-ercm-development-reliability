from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

hmal_codes = Table('hmal_codes', metadata, 

    Column('Code', String(45), primary_key=True, autoincrement=False),
    Column('Description', LONGTEXT, primary_key=False, autoincrement=False),
)