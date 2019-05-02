from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import LONGTEXT, BIGINT
from sqlalchemy import MetaData, Table

metadata = MetaData()

on_equipment_maintenance = Table('on_equipment_maintenance', metadata,

    Column('On_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BIGINT, primary_key=True, autoincrement=False),
    Column('Off_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Order_Number', BIGINT, primary_key=True, autoincrement=False),
    Column('Depot_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Unit_Code', String(45)),
    Column('WUC_Rule', String(255))
    )