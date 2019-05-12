from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

current_operating_time = Table('current_operating_time', metadata, 

    Column('On_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Off_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Depot_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
    Column('Sorties_Flown', Integer, primary_key=False, autoincrement=False),
    Column('Total_Landings', Integer, primary_key=False, autoincrement=False),
    Column('Full_Stop_Landings', Integer, primary_key=False, autoincrement=False)
)