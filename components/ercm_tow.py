import os
from datetime import date
from itertools import groupby
from collections import defaultdict

from ercm_tow_resource import queries as qry
from src.components.component import Component

class eRCM_TOW(Component):

    def __init__(self):
        super(eRCM_TOW, self).__init__()
        #self.add_parameter('eisys', '')
        self.add_parameter('Work_Unit_Code', '')
        self.add_parameter('source_table', '')
    
    def extract(self):
        # current/last-recorded component hours - for suspensions
        #self.eng_hrs = self.select_map(qry.eng_hrs, 'esn')
        
        # query maintenance records and nha_hours
        self.wuc_records = self.select_dicts(qry.fetch_wuc, params=(self.get_parameter('Work_Unit_Code'),))
        
        #need assy level? not sure if trying to gather any hierarchy info, and don't see where it would come from
        #self.assy_lvl = self.get_assembly_level(self.get_parameter('WUC'))
        

    # def get_assembly_level(self, wuc):
        # results = self.select(qry.assy_lvl, (wuc, self.get_parameter('eisys')))
        # try:
            # return results.first().ASSY_LVL
        # except AttributeError:
            # return 2
    
    def _is_install(self, record):
        #return record['COPY'] == 3 and not record['RCODE']
        return record['Action_Taken_Code'] == 'Q' or record['Action_Taken_Code'] == 'U'

    def _is_removal(self, record):
        #return record['COPY'] == 1 and not record['RCODE']
        return record['Action_Taken_Code'] == 'P' or record['Action_Taken_Code'] == 'T'
    
    #def _is_repair(self, record):
        #return record['COPY'] == 2 and record['RCODE'] not in ('A', 'U')

    #def _is_loss(self, record):
        #return record['COPY'] == 3 and record['RCODE']
    
    #def _get_current_age(self, record):
        #return self.eng_hrs.get(record['Serial_Number'], [{'tsn':0}])[0]['tsn']
        #need to handle if this doesn't exist?? get it from an nha??
    
    def _start_tow_record(self, record):
        self.tow_record = defaultdict(list)
        self.tow_record['Work_Unit_Code'] = record['Work_Unit_Code']
        self.tow_record['Serial_Number'] = record['Serial_Number']
        #self.tow_record['PN'] = record.get('PN')
        self.tow_record['Equipment_Designator'] = record['Equipment_Designator']
        #self.tow_record['NHA_SN'] = record['Install_EI_Serial_Number']
        self.tow_record['Component_Position_Number'] = record['Component_Position_Number']
        self.tow_record['Work_Order_Number'] = record['Work_Order_Number']
        self.tow_record['Sequence_Number'] = record['Sequence_Number']
        self.tow_record['Work_Center_Event_Identifier'] = record['Work_Center_Event_Identifier']
        self.tow_record['INSTALL_Transaction_Date'] = record['Transaction_Date']
        #self.tow_record['INSTALL_TIME'] = record['Start_Time']
        self.tow_record['INSTALL_Geographic_Location'] = record['Geographic_Location']
        self.tow_record['INSTALL_TSN'] = record['Current_Operating_Time']
        self.tow_record['INSTALL_Action_Taken_Code'] = record['Action_Taken_Code']
        self.tow_record['Corrective_Narrative'] = record['Corrective_Narrative']
        self.tow_record['Discrepancy_Narrative'] = record['Discrepancy_Narrative']
        self.tow_record['Work_Center_Event_Narrative'] = record['Work_Center_Event_Narrative']
        self.tow_record['Last_FH'] = record['Flying_Hours_Last_Sortie']
    
    def _add_removal_to_tow_record(self, record):
        if self.tow_record.get('REMOVAL_Transaction_Date'):
            time_between_removals = record['Current_Operating_Time'] - self.tow_record['INSTALL_TSN'] - self.tow_record['TOW']
            if time_between_removals > 0:
                self.log.debug('multiple removals in a single interval with > 0 time between')
                self.log.debug("time added since record's first removal: {}".format(time_between_removals))
                self.multiple_removals_nonzero_tow += 1
            else:
                self.multiple_removals_zero_tow += 1
            #self.log.debug(repr(self.tow_record))
        self.tow_record['REMOVAL_Transaction_Date'] = record['Transaction_Date']
        self.tow_record['REMOVAL_Action_Taken_Code'] = record['Action_Taken_Code']
        #self.tow_record['REMOVAL_TIME'] = record['Start_Time']
        self.tow_record['REMOVAL_Geographic_Location'] = record['Geographic_Location']
        self.tow_record['REMOVAL_How_Malfunction_Code'] = record['How_Malfunction_Code']
        self.tow_record['REMOVAL_When_Discovered_Code'] = record['When_Discovered_Code']
        self.tow_record['REMOVAL_Cause'] = record['Removal_Cause']
        self.tow_record['TOW'] = max(0, record['Current_Operating_Time'] - self.tow_record['INSTALL_TSN'])
    
    def record_tow_record(self, record=None):
        if hasattr(self, 'tow_record'):
                        
            #self.tow_record['CONSQ_DT'] = ';'.join(self.tow_record['CONSQ_DT'])
            #self.tow_record['CONSQ_COPY'] = ';'.join(self.tow_record['CONSQ_COPY'])
            #self.tow_record['CONSQ_RCODE'] = ';'.join(self.tow_record['CONSQ_RCODE'])
            #self.tow_record['CONSQ_UIC'] = ';'.join(self.tow_record['CONSQ_UIC'])
            #self.tow_record['CONSQ_IACT_CD'] = ';'.join(self.tow_record['CONSQ_IACT_CD'])

            if 'TOW' not in self.tow_record:
                # still-installed (suspension); estimate current age and location
                #current_tsn = self._get_current_age(self.tow_record)
                self.tow_record['TOW'] = max(0, self.tow_record['Last_FH'] - self.tow_record['INSTALL_TSN'])

            self.tow_record['REMOVAL_TSN'] = self.tow_record['INSTALL_TSN'] + self.tow_record['TOW']
            self.tow_record.pop('Last_FH')
            self.tow_records.append(dict(self.tow_record))
            del self.tow_record
    
    def _process_sn_group(self, (sn, sn_group)):

        map(self._process_sn_station_group, groupby(sn_group, key=lambda x: x['Component_Position_Number']))

    def _process_sn_station_group(self, (station, sn_station_group)):
        for r in sn_station_group:
            if self._is_install(r) and not hasattr(self, 'tow_record'):
                self._start_tow_record(r)
            elif self._is_removal(r) and hasattr(self, 'tow_record'):
                self._add_removal_to_tow_record(r)
            #elif (self._is_repair(r) or self._is_loss(r)) and hasattr(self, 'tow_record'):
                #self._add_consq_to_tow_record(r)
            elif self._is_install(r) and hasattr(self, 'tow_record'):
                if 'TOW' not in self.tow_record:
                    # multiple installs in a row without a removal. start interval over
                    time_between_installs = r['Current_Operating_Time'] - self.tow_record['INSTALL_TSN']
                    if time_between_installs > 0:
                        self.log.debug('multiple installs in a single interval with > 0 time between')
                        self.log.debug("time added since record's first install: {}".format(time_between_installs))
                        self.multiple_installs_nonzero_tow += 1
                    else:
                        self.multiple_installs_zero_tow += 1
                    #self.log.debug(repr(self.tow_record))
                    self._start_tow_record(r)
                else:
                    # end of proper tow record
                    self.record_tow_record(r)
                    self._start_tow_record(r)

        self.record_tow_record()

    def transform(self):

        self.multiple_installs_zero_tow = 0
        self.multiple_installs_nonzero_tow = 0
        self.multiple_removals_zero_tow = 0
        self.multiple_removals_nonzero_tow = 0

        self.tow_records = []
        map(self._process_sn_group, groupby(self.wuc_records, key=lambda x: x['Serial_Number']))

        self.log.debug("multiple_installs_zero_tow: {}".format(self.multiple_installs_zero_tow))
        self.log.debug("multiple_installs_nonzero_tow: {}".format(self.multiple_installs_nonzero_tow))
        self.log.debug("multiple_removals_zero_tow: {}".format(self.multiple_removals_zero_tow))
        self.log.debug("multiple_removals_nonzero_tow: {}".format(self.multiple_removals_nonzero_tow))

        self.write_tsv(self.name, self.tow_records, self.field_names)

    def load(self):

        self.load_text(self.get_filename())

    def tearDown(self):

        # delete any intermediate tab file
        if os.path.isfile(self.get_filename()):
            os.remove(self.get_filename())
