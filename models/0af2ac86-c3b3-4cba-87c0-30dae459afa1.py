from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

three_month_fh_collector = Table('three_month_fh_collector', metadata, 

    Column('Three_Month_Start_Date', DateTime, primary_key=True, autoincrement=False),
    Column('Average_Flying_Hours', Float, primary_key=False, autoincrement=False),
)