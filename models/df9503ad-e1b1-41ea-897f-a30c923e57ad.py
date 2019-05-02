from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

predictive_twins = Table('predictive_twins', metadata, 

    Column('MDS', String(15), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=True, autoincrement=False),
    Column('Current_Aircraft_TSN', Float, primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(5), primary_key=True, autoincrement=False),
    Column('Position', String(45), primary_key=True, autoincrement=False),
    Column('Last_Install_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Last_Install_TSN', Float, primary_key=False, autoincrement=False),
    Column('Lost_Position', TINYINT, primary_key=False, autoincrement=False),
    Column('Current_TOW', Float, primary_key=False, autoincrement=False)
)