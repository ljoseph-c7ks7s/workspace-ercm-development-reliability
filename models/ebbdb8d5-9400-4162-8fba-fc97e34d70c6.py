from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

c130_g081_sortie_data = Table('c130_g081_sortie_data', metadata, 

    Column('Command', String(4), primary_key=False, autoincrement=False),
    Column('Possessing_Org', String(9), primary_key=False, autoincrement=False),
    Column('MDS', String(6), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(15), primary_key=True, autoincrement=False),
    Column('Mission_Number', String(20), primary_key=False, autoincrement=False),
    Column('Mission_Symbol', String(4), primary_key=False, autoincrement=False),
    Column('Depart_ICAO', String(4), primary_key=False, autoincrement=False),
    Column('Depart_Date', DateTime, primary_key=True, autoincrement=False),
    Column('Depart_Time', TIME, primary_key=True, autoincrement=False),
    Column('Land_ICAO', String(4), primary_key=False, autoincrement=False),
    Column('Land_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Land_Time', TIME, primary_key=False, autoincrement=False),
    Column('Flying_Hours', Float, primary_key=False, autoincrement=False),
    Column('Sorties', Integer, primary_key=False, autoincrement=False),
    Column('Total_Landings', Integer, primary_key=False, autoincrement=False),
    Column('Full_Stop_Landings', Integer, primary_key=False, autoincrement=False),
    Column('Purpose_Possession_Code', String(2), primary_key=False, autoincrement=False),
    Column('Update_By_BASE', String(4), primary_key=False, autoincrement=False),
    Column('Update_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Update_Time', Integer, primary_key=False, autoincrement=False),
) 