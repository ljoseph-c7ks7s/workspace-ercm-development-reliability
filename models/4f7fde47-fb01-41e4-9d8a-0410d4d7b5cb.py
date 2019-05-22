from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

domain_check = Table('domain_check', metadata, 

    Column('distribution_id', BigInteger, primary_key=True, autoincrement=False),
    Column('domain_check', String(15), primary_key=False, autoincrement=False)
)