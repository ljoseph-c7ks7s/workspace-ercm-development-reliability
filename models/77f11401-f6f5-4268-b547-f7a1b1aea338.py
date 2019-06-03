from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

last_sortie = Table('last_sortie', metadata, 

    Column('MDS', String(255), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=True, autoincrement=False),
    Column('Mission_Number', String(255), primary_key=False, autoincrement=False),
    Column('Sortie_Number', Integer, primary_key=False, autoincrement=False),
    Column('Depart_ICAO', String(255), primary_key=False, autoincrement=False),
    Column('Depart_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Depart_Time', TIME, primary_key=False, autoincrement=False),
    Column('Land_ICAO', String(255), primary_key=False, autoincrement=False),
    Column('Land_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Land_Time', TIME, primary_key=False, autoincrement=False),
    Column('Flying_Hours', Float, primary_key=False, autoincrement=False),
    Column('Sorties_Flown', Integer, primary_key=False, autoincrement=False),
    Column('Total_Landings', Integer, primary_key=False, autoincrement=False),
    Column('Full_Stop_Landings', Integer, primary_key=False, autoincrement=False),
    Column('Sortie_Date', DateTime, primary_key=False, autoincrement=False),
    Column('__id__', String(255), primary_key=True, autoincrement=False)
)