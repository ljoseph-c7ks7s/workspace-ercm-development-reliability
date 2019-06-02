from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

sub_population_for_labeling = Table('sub_population_for_labeling', metadata, 

    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Discrepancy_Narrative', LONGTEXT),
    Column('Work_Center_Event_Narrative', LONGTEXT),
    Column('Corrective_Narrative', LONGTEXT)
)