from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

multinomial_comparison_6 = Table('multinomial_comparison_6', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=False),
    Column('model_name', String(255), primary_key=False, autoincrement=False),
    Column('label', String(45), primary_key=False, autoincrement=False),
    Column('metric', String(45), primary_key=False, autoincrement=False),
    Column('value', Float, primary_key=False, autoincrement=False),
    Column('train_test', String(15), primary_key=False, autoincrement=False),
)