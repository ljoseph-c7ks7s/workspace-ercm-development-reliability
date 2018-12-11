fn <- function(conn_rmysql, load_path, params_path, component_path, output_file) {
  library(dplyr)
  library(lubridate)
  ##load data for usage ##
  df_cumulate <- dbGetQuery(conn_rmysql, 'SELECT * FROM ercm.sortie_accumulated_hours')
  df_i <- dbGetQuery(conn_rmysql, 'SELECT * FROM ercm.clean_wuc_remove_fom AS c  INNER JOIN compiled_c130_remis_data AS r
                     ON r.On_Work_Order_Key = c.On_Work_Order_Key
                     AND r.On_Maint_Action_Key = c.On_Maint_Action_Key
                     AND r.Work_Center_Event_Identifier = c.Work_Center_Event_Identifier
                     AND r.Sequence_Number = c.Sequence_Number
                     AND r.Work_Order_Number = c.Work_Order_Number')
  df_i <- df_i[, !duplicated(colnames(df_i))]
  
  
  df_i <- as.data.frame(df_i)
  
  df_i$Serial_Number <- trimws(df_i$Serial_Number, which = "both")
  df_cumulate$Serial_Number <- trimws(df_cumulate$Serial_Number, which = "both")
  
  ##Edit Sortie Data
  ##Find all of the columns without unique items & cleaning
  
  df_phase1 <- df_i %>% select(c(Work_Unit_Code, On_Component_Serial_Number,
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
  
  
  ##Limit serial numbers to those associated with the WUC in the study
  df_cumulate <- dplyr::filter(df_cumulate, Serial_Number %in% df_phase1$Serial_Number)
  
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
  
  ##Note: Serial_Number == NA is omitted because it could not be serialized/analyzed##
  ##Get entries that do not need to be changed
  data_reserve <- dplyr::filter(df_phase1, !is.na(Current_Operating_Time))
  
  df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% ymd_hms()
  df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% as.character()
  
  date_check <- df_cumulate[,c('Depart_Date','Serial_Number')] %>% 
    as.data.frame() %>%
    unique()
  
  
  ##Finding the closest date to the Transaction Date (they were all the same day)
  data_reserve$Transaction_Date <- lubridate::ymd(data_reserve$Transaction_Date)
  new_date <- c()
  for(i in 1:nrow(data_reserve)){
    data_check <- filter(date_check, Serial_Number == data_reserve[i,"Serial_Number"])
    new_date <- rbind(new_date, data_check[which.min(abs(difftime(data_reserve[i,'Transaction_Date'],data_check[,1], units = 'days'))),1]
                      %>% as.character())
  }
  
  data_reserve <- filter(data_reserve, Serial_Number %in% date_check$Serial_Number)
  data_reserve <- cbind(data_reserve, new_date)
  
  ##Isolate Sortie data with serial numbers identical to those we are confirming flight hours against
  sortie_ver <- df_cumulate[,c('Flying_Hours', 'Serial_Number', 'Depart_Date', 
                               'Total_Landings', 'Full_Stop_Landings')]
  colnames(sortie_ver) <- c('Flying_Hours', 'Serial_Number', 'new_date', 
                            'Total_Landings', 'Full_Stop_Landings')
  sortie_ver$new_date <- as.Date(sortie_ver$new_date)
  
  ## Merge data sets by serial number and new date so we can get the associated flight hours
  ##merge results in 284 results, due to not all serial numbers being present in previous data frame
  data_reserve$new_date <- data_reserve$new_date %>% as.Date()
  merged_ver <- merge(sortie_ver, data_reserve, by= c('Serial_Number','new_date'))
  
  ##Defined a new column that is the difference in flight hours
  merged_ver$flight_diff <- merged_ver$Current_Operating_Time- merged_ver$Flying_Hours
  merged_ver$flight_diff <- as.numeric(merged_ver$flight_diff)
  adjustment <- aggregate(merged_ver[, 'flight_diff'], list(merged_ver$Serial_Number), mean)
  colnames(adjustment) <- c("Serial_Number", "Mean_Adj")
  
  df_cumulate_adj <- merge(df_cumulate, adjustment, by = 'Serial_Number')
  
  df_cumulate_plane <- df_cumulate %>% filter(!Serial_Number %in% df_cumulate_adj$Serial_Number)
  df_cumulate_plane$Mean_Adj <- rep(0, nrow(df_cumulate_plane))
  
  df_cumulate_adj <- df_cumulate_adj %>% as.data.frame()
  df_cumulate_plane <- df_cumulate_adj %>% as.data.frame()
  
  df_cumulated <- rbind(df_cumulate_adj, df_cumulate_plane) 
  df_cumulated$Flying_Hours <- df_cumulated$Flying_Hours + df_cumulated$Mean_Adj
  df_cumulated <- df_cumulated %>% select(-Mean_Adj)
  
  ##Create the different tables
  ##Adjusted Cumulated Hours
  dbWriteTable(conn_rmysql, name = "current_sortie_date_and_adjusted_flying_hours", value = df_cumulated, 
               overwrite = TRUE, row.names = FALSE)
}

