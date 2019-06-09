from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

label_22gab_action = Table('label_22gab_action', metadata, 

    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Action', String(255), primary_key=False, autoincrement=False),
)