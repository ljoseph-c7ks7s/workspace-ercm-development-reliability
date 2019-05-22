from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

weibull_quantiles = Table('weibull_quantiles', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('distribution_id', BigInteger, primary_key=True, autoincrement=False),
    Column('type', String(45), primary_key=True, autoincrement=False),
    Column('quantile', Float, primary_key=True, autoincrement=False),
    Column('time', Float, primary_key=False, autoincrement=False),
    Column('lcl', Float, primary_key=False, autoincrement=False),
    Column('ucl', Float, primary_key=False, autoincrement=False)
)