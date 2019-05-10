from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

opstempo = Table('opstempo', metadata, 

    Column('start_prediction_date', DateTime, primary_key=True, autoincrement=False),
    Column('owner_MDS', String(30), primary_key=True, autoincrement=False),
    Column('1_month_forecast', Integer, primary_key=False, autoincrement=False),
    Column('2_month_forecast', Integer, primary_key=False, autoincrement=False),
    Column('3_month_forecast', Integer, primary_key=False, autoincrement=False),
    Column('4_month_forecast', Integer, primary_key=False, autoincrement=False),
    Column('5_month_forecast', Integer, primary_key=False, autoincrement=False),
    Column('6_month_forecast', Integer, primary_key=False, autoincrement=False)
)