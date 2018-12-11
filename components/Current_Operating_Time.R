fn <- function(conn_rmysql, load_path, params_path, component_path, output_file) {
  library(dplyr)
  library(lubridate)
  df_phase1 <- dbGetQuery(conn_rmysql, 'SELECT * FROM ercm.clean_wuc_remove_fom AS c  INNER JOIN compiled_c130_remis_data AS r
                     ON r.On_Work_Order_Key = c.On_Work_Order_Key
                   AND r.On_Maint_Action_Key = c.On_Maint_Action_Key
                   AND r.Work_Center_Event_Identifier = c.Work_Center_Event_Identifier
                   AND r.Sequence_Number = c.Sequence_Number
                   AND r.Work_Order_Number = c.Work_Order_Number')
  df_phase1 <- df_phase1[, !duplicated(colnames(df_phase1))]
  df_cumulate <- dbGetQuery(conn_rmysql, 'SELECT * FROM current_sortie_date_and_adjusted_flying_hours')
  
  df_phase1 <- df_phase1 %>% select(c(Work_Unit_Code, On_Component_Serial_Number,
                                 On_Component_Part_Number, Equipment_Designator,
                                 Serial_Number, Geographic_Location, 
                                 Performing_Geographic_Location, Transaction_Date,
                                 Start_Time, Work_Center_Code, When_Discovered_Code, 
                                 How_Malfunction_Code, Action_Taken_Code, 
                                 Type_Maintenance_Code, Current_Operating_Time, 
                                 Component_Position_Number, Corrective_Narrative, 
                                 Discrepancy_Narrative, Work_Center_Event_Narrative,
                                 On_Work_Order_Key, On_Maint_Action_Key, 
                                 Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number))
  
  ##Fix the fill-in##
  ##Change 0 to NA##
  df_phase1$Current_Operating_Time[df_phase1$Current_Operating_Time == 0] <- NA
  
  ##Find first entry in Sortie Data##
  first <- df_cumulate %>%
    group_by(Serial_Number) %>%
    arrange(Depart_Date) %>%
    slice(1L)
  first <- first %>% as.data.frame()
  df_phase1$Transaction_Date <- df_phase1$Transaction_Date %>%
    as.Date()
  first$Depart_Date <- first$Depart_Date %>%
    as.Date()
  
  ##Get Data After Sortie Starts
  SN_fix <- c('9600008153', '9600008154')
  remainder <- df_phase1 %>%
    filter(!Serial_Number %in% SN_fix)
  
  
  df_phase1 <- c()
  for(i in 1:nrow(first)){
    check_me <- dplyr::filter(remainder, Serial_Number == first[i,'Serial_Number'])
    after_sortie_df <- dplyr::filter(check_me, Transaction_Date >= first[i,'Depart_Date'])
    df_phase1 <- rbind(df_phase1, after_sortie_df)
  }
  
  df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% ymd_hms()
  df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% as.character()
  
  date_check <- df_cumulate[,c('Depart_Date','Serial_Number')] %>% 
    as.data.frame() %>%
    unique()
  
  
  ##Finding the closest date to the Transaction Date (they were all the same day)
  df_phase1$Transaction_Date <- lubridate::ymd(df_phase1$Transaction_Date)
  new_date <- c()
  for(i in 1:nrow(df_phase1)){
    data_check <- filter(date_check, Serial_Number == df_phase1[i,"Serial_Number"])
    new_date <- rbind(new_date, data_check[which.min(abs(difftime(df_phase1[i,'Transaction_Date'],data_check[,1], units = 'days'))),1]
                      %>% as.character())
  }
  
  df_phase1 <- filter(df_phase1, Serial_Number %in% date_check$Serial_Number)
  df_phase1 <- cbind(df_phase1, new_date)
  
  sortie_mergeset <- df_cumulate[,c('Flying_Hours', 'Serial_Number', 'Depart_Date', 
                                    'Total_Landings', 'Full_Stop_Landings')]
  colnames(sortie_mergeset) <- c('Flying_Hours', 'Serial_Number', 'new_date', 
                                 'Total_Landings', 'Full_Stop_Landings')
  df_phase1_FH <- merge(df_phase1, sortie_mergeset, by= c('Serial_Number','new_date')) 
  df_phase1_FH$Current_Operating_Time <- df_phase1_FH$Flying_Hours
  current_op_time <- df_phase1_FH %>% select(c(On_Work_Order_Key, On_Maint_Action_Key, 
                                               Work_Center_Event_Identifier, Sequence_Number, Work_Order_Number, Current_Operating_Time))
  dbWriteTable(conn_rmysql, name = "current_operating_time", value = current_op_time, 
               overwrite = TRUE, row.names = FALSE)

}