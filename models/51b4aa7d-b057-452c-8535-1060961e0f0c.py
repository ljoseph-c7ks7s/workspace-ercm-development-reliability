from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Float, Date
from sqlalchemy.dialects.mysql import DOUBLE, DECIMAL, TEXT, MEDIUMTEXT, MEDIUMBLOB, TINYINT, LONGTEXT, BINARY, SMALLINT, MEDIUMINT, BIT, TIMESTAMP, TIME
from sqlalchemy import MetaData, Table

metadata = MetaData()

weibull_archive = Table('weibull_archive', metadata, 

    Column('Fit_Date', DateTime, primary_key=False, autoincrement=False),
    Column('Forecast_Start_Date', Date, primary_key=True, autoincrement=False),
    Column('distribution_id', BigInteger, primary_key=True, autoincrement=False),
    Column('interval_parameter_set_id', BigInteger, primary_key=False, autoincrement=False),
    Column('Work_Unit_Code', String(255), primary_key=False, autoincrement=False),
    Column('MDS', String(255), primary_key=False, autoincrement=False),
    Column('Time_Frame', String(255), primary_key=False, autoincrement=False),
    Column('distribution_mean', Float, primary_key=False, autoincrement=False),
    Column('causal_events', Integer, primary_key=False, autoincrement=False),
    Column('censored_events', Integer, primary_key=False, autoincrement=False),
    Column('log_likelihood', Float, primary_key=False, autoincrement=False),
    Column('anderson_darling_adj', Float, primary_key=False, autoincrement=False),
    Column('ks_stat', Float, primary_key=False, autoincrement=False),
    Column('beta_eq_one_pval', Float, primary_key=False, autoincrement=False),
    Column('dist_name', String(255), primary_key=False, autoincrement=False),
    Column('eta', Float, primary_key=False, autoincrement=False),
    Column('eta_se', Float, primary_key=False, autoincrement=False),
    Column('beta', Float, primary_key=False, autoincrement=False),
    Column('beta_se', Float, primary_key=False, autoincrement=False),
    Column('Preferred', TINYINT, primary_key=False, autoincrement=False),
    Column('Range_Check', String(255), primary_key=False, autoincrement=False),
    Column('Domain_Check', String(255), primary_key=False, autoincrement=False),
    Column('__id__', String(255), primary_key=True, autoincrement=False),
)