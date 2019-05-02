from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

single_weibull_quantiles = Table('single_weibull_quantiles', metadata, 

    Column('type', String(45), primary_key=True, autoincrement=False),
    Column('quantile', Float, primary_key=True, autoincrement=False),
    Column('time', Float, primary_key=False, autoincrement=False),
    Column('lcl', Float, primary_key=False, autoincrement=False),
    Column('ucl', Float, primary_key=False, autoincrement=False)
)