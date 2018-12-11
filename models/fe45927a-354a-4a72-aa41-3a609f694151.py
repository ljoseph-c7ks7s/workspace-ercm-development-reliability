from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

current_operating_time = Table('current_operating_time', metadata, 

    Column('On_Work_Order_Key', Integer, primary_key=True, autoincrement=False),
    Column('On_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', Integer, primary_key=True, autoincrement=False),
    Column('Work_Order_Number', Integer, primary_key=True, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
)