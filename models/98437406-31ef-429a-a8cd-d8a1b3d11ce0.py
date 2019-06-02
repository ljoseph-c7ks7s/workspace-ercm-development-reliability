from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

split_r_and_multi_pos = Table('split_r_and_multi_pos', metadata, 

    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Primary_Key_Index', Integer, primary_key=True, autoincrement=False),
    Column('Action_Taken_Code', String(64), primary_key=False, autoincrement=False),
    Column('Parsed_Component_Position', String(64), primary_key=False, autoincrement=False),
)