from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

aircraft_in_depot = Table('aircraft_in_depot', metadata, 

    Column('File_Name', String(255), primary_key=True, autoincrement=False),
    Column('MDS', String(10), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(10), primary_key=True, autoincrement=False),
    Column('Command', String(4), primary_key=False, autoincrement=False),
    Column('Purpose_Code', String(2), primary_key=False, autoincrement=False),
    Column('Assigned_Base', String(255), primary_key=False, autoincrement=False),
    Column('Current_Base', String(255), primary_key=False, autoincrement=False),
    Column('Depot_Input', Date, primary_key=False, autoincrement=False),
    Column('Orig_Sched_Out', Date, primary_key=False, autoincrement=False),
    Column('Sched_Out', Date, primary_key=False, autoincrement=False),
    Column('Forecast_Out', Date, primary_key=False, autoincrement=False)
)