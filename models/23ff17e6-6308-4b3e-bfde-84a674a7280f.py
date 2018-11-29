from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

work_unit_codes = Table('work_unit_codes', metadata, 

    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('WUC_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Count', BigInteger, primary_key=False, autoincrement=False),
)