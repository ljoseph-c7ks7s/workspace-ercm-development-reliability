from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

interval_data_for_plots = Table('interval_data_for_plots', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=False),
    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('TOW', Float, primary_key=False, autoincrement=False),
    Column('REMOVAL_Cause', String(255), primary_key=False, autoincrement=False),
    Column('Causal', TINYINT, primary_key=False, autoincrement=False),
    Column('Removed_Last_5_Years', TINYINT, primary_key=False, autoincrement=False),
    Column('Removed_Last_10_Years', TINYINT, primary_key=False, autoincrement=False),
)