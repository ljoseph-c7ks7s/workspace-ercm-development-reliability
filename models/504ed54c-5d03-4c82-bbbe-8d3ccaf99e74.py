from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

what_data = Table('what_data', metadata, 

    Column('mds', String(255), primary_key=False, autoincrement=False),
    Column('year', Integer, primary_key=False, autoincrement=False),
    Column('count', BigInteger, primary_key=False, autoincrement=False),
)