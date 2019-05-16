from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import LONGTEXT, BIGINT
from sqlalchemy import MetaData, Table

metadata = MetaData()

remis_prp4127 = Table('remis_prp4127', metadata,

    Column('Record_id', BIGINT, primary_key=True, autoincrement=True),
    Column('Record_Type', String(12)),
    Column('Equipment_Designator', String(12)),
    Column('Type_Equipment', String(1)),
    Column('Block_Number', Integer),
    Column('Standard_Reporting_Designator', String(3)),
    Column('Federal_Supply_Classification', Integer),
    Column('Serial_Number', String(45)),
    Column('Current_Operating_Time', Float),
    Column('Job_Control_Number', String(9)),
    Column('Command', String(3)),
    Column('Geographic_Location', String(4)),
    Column('Organization', String(45)),
    Column('TCTO_Data_Code', String(12)),
    Column('Work_Unit_Code', String(45)),
    Column('Component_Part_Number', String(45)),
    Column('Component_Serial_Number', String(45)),
    Column('Component_Position_Number', Integer),
    Column('Type_Maintenance_Code', String(1)),
    Column('Action_Taken_Code', String(6)),
    Column('When_Discovered_Code', String(3)),
    Column('How_Malfunction_Code', Integer),
    Column('How_Malfunction_Class_Ind', Integer),
    Column('AFTO_Form_350_Tag_Number', Integer),
    Column('Work_Center_Event_Identifier', Integer),
    Column('Sequence_Number', BIGINT),
    Column('Transaction_Date', Date),
    Column('Start_Time', Integer),
    Column('Stop_Time', Integer),
    Column('Performing_Geographic_Location', String(4)),
    Column('Work_Center_Code', String(12)),
    Column('Crew_Size', Integer),
    Column('Units', Integer),
    Column('Labor_Manhours', Float),
    Column('On_Base_Turn_In_Doc_Number', String(45)),
    Column('On_Equip_Work_Center_Event_Id', Integer),
    Column('On_Equip_Sequence_Number', Integer),
    Column('Activity_Identifier', String(12)),
    Column('Maintenance_Priority', String(12)),
    Column('Maintainer_Name', String(45)),
    Column('Documenter_Name', String(45)),
    Column('On_Component_Part_Number', String(45)),
    Column('On_Component_Serial_Number', String(45)),
    Column('Installed_Equipment_Designator', String(45)),
    Column('Installed_Serial_Number', String(45)),
    Column('Installed_CAGE_Code', String(12)),
    Column('Installed_Lot_Number', String(15)),
    Column('Installed_Type_Equipment', String(1)),
    Column('Installed_Work_Unit_Code', String(12)),
    Column('Installed_Location_Identifier', String(12)),
    Column('Installed_Current_Operating_Time', Float),
    Column('Installed_Prev_Operating_Time', Float),
    Column('Removed_Equipment_Designator', String(45)),
    Column('Removed_Serial_Number', String(45)),
    Column('Removed_CAGE_Code', String(12)),
    Column('Removed_Lot_Number', String(15)),
    Column('Removed_Type_Equipment', String(1)),
    Column('Removed_Work_Unit_Code', String(45)),
    Column('Removed_Location_Identifier', String(12)),
    Column('Removed_Current_Operating_Time', Float),
    Column('Removed_Prev_Operating_Time', Float),
    Column('Installed_EI_Equip_Designator', String(45)),
    Column('Installed_EI_Serial_Number', String(45)),
    Column('Installed_EI_SRD', String(3)),
    Column('Installed_EI_Type_Equipment', String(1)),
    Column('Installed_EI_Work_Unit_Code', String(45)),
    Column('Installed_EI_Comp_Part_Number', String(45)),
    Column('Installed_EI_Comp_Serial_Number', String(45)),
    Column('Discrepancy_Narrative', LONGTEXT),
    Column('Work_Center_Event_Narrative', LONGTEXT),
    Column('Corrective_Action_Narrative', LONGTEXT),
    Column('WUC_Narrative', LONGTEXT),
    Column('Installed_EI_WUC_Narrative', LONGTEXT),
    Column('Installed_WUC_Narrative', LONGTEXT),
    Column('Removed_WUC_Narrative', LONGTEXT)
    )