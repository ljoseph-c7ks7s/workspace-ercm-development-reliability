from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table, UniqueConstraint

metadata = MetaData()

calculate_tow = Table('calculate_tow', metadata, 

    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('WUC', String(45), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('EI_MDS', String(255), primary_key=False, autoincrement=False),
    Column('Component_Position_Number', Integer, primary_key=False, autoincrement=False),
    Column('INSTALL_DT', Date, primary_key=False, autoincrement=False),
    Column('INSTALL_TIME', Integer, primary_key=False, autoincrement=False),
    Column('INSTALL_LOC', String(255), primary_key=False, autoincrement=False),
    Column('TSN', Float, primary_key=False, autoincrement=False),
    Column('ATC', String(255), primary_key=False, autoincrement=False),
    Column('CORR_NARR', TEXT, primary_key=False, autoincrement=False),
    Column('DISCREP_NARR', TEXT, primary_key=False, autoincrement=False),
    Column('WCE_NARR', TEXT, primary_key=False, autoincrement=False),
    Column('REMOVAL_DT', Date, primary_key=False, autoincrement=False),
    Column('REMOVAL_TIME', Integer, primary_key=False, autoincrement=False),
    Column('REMOVAL_LOC', String(255), primary_key=False, autoincrement=False),
    Column('REMOVAL_HOWMAL', Integer, primary_key=False, autoincrement=False),
    Column('WHEN_DISC_CODE', String(255), primary_key=False, autoincrement=False),
    Column('TOW', Float, primary_key=False, autoincrement=False),

    UniqueConstraint('WUC', 'Serial_Number', 'Component_Position_Number', 'INSTALL_DT', name='wuc-sn-posn-install-dt')
)