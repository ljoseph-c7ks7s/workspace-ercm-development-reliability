from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

joined_data = Table('joined_data', metadata, 

    Column('Work_Unit_Code', String(45), primary_key=False, autoincrement=False),
    Column('On_Component_Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('On_Component_Part_Number', String(255), primary_key=False, autoincrement=False),
    Column('Equipment_Designator', String(255), primary_key=False, autoincrement=False),
    Column('Serial_Number', String(255), primary_key=False, autoincrement=False),
    Column('Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('Performing_Geographic_Location', String(255), primary_key=False, autoincrement=False),
    Column('Transaction_Date', Date, primary_key=False, autoincrement=False),
    Column('Start_Time', Integer, primary_key=False, autoincrement=False),
    Column('Work_Center_Code', String(255), primary_key=False, autoincrement=False),
    Column('When_Discovered_Code', String(255), primary_key=False, autoincrement=False),
    Column('How_Malfunction_Code', Integer, primary_key=False, autoincrement=False),
    Column('Action_Taken_Code', String(255), primary_key=False, autoincrement=False),
    Column('Removal_Cause', String(255), primary_key=False, autoincrement=False),
    Column('Type_Maintenance_Code', String(255), primary_key=False, autoincrement=False),
    Column('Current_Operating_Time', Float, primary_key=False, autoincrement=False),
    Column('Component_Position_Number', String(45), primary_key=False, autoincrement=False),
    Column('Corrective_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Discrepancy_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Work_Center_Event_Narrative', TEXT, primary_key=False, autoincrement=False),
    Column('Depart_Date', TEXT, primary_key=False, autoincrement=False),
    Column('Depart_Time', TEXT, primary_key=False, autoincrement=False),
    Column('Flying_Hours_Last_Sortie', Float, primary_key=False, autoincrement=False),
    Column('Sorties_Flown_Last_Sortie', Float, primary_key=False, autoincrement=False),
    Column('Total_Landings_Last_Sortie', Float, primary_key=False, autoincrement=False),
    Column('Full_Stop_Landings_Last_Sortie', Float, primary_key=False, autoincrement=False),
    Column('On_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Center_Event_Identifier', Integer, primary_key=True, autoincrement=False),
    Column('Sequence_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Off_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Work_Order_Number', BigInteger, primary_key=True, autoincrement=False),
    Column('Depot_Maint_Action_Key', Integer, primary_key=True, autoincrement=False),
    Column('Primary_Key_Index', Integer, primary_key=True, autoincrement=False)
)