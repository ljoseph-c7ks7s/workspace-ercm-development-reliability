from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

opstempo_archive = Table('opstempo_archive', metadata, 

    Column('forecast_generation_date', DateTime, primary_key=False, autoincrement=False),
    Column('start_prediction_date', DateTime, primary_key=True, autoincrement=False),
    Column('owner', String(255), primary_key=True, autoincrement=False),
    Column('MDS', String(255), primary_key=True, autoincrement=False),
    Column('forecast_method', String(255), primary_key=False, autoincrement=False),
    Column('forecast_1_month', Integer, primary_key=False, autoincrement=False),
    Column('forecast_2_months', Integer, primary_key=False, autoincrement=False),
    Column('forecast_3_months', Integer, primary_key=False, autoincrement=False),
    Column('forecast_4_months', Integer, primary_key=False, autoincrement=False),
    Column('forecast_5_months', Integer, primary_key=False, autoincrement=False),
    Column('forecast_6_months', Integer, primary_key=False, autoincrement=False),
    Column('__id__', String(255), primary_key=True, autoincrement=False),
)