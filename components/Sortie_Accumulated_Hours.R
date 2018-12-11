fn <- function(conn_rmysql, load_path, params_path, component_path, output_file) {
  library(dplyr)
  df_cumulate <- dbGetQuery(conn_rmysql, 'SELECT * FROM compiled_sortie_history_data')
  df_cumulate[df_cumulate[,"Depart_Date"] < as.Date('1950-01-01'), 5] <- df_cumulate[df_cumulate[,"Depart_Date"] < as.Date('1950-01-01'), 8]
  df_cumulate <- as.data.frame(df_cumulate)
  df_cumulate <- df_cumulate[order(df_cumulate$Serial_Number, df_cumulate$Depart_Date),]
  
  df_cumulate <- df_cumulate %>%
    group_by(Serial_Number) %>%
    mutate(Flying_Hours = cumsum(Flying_Hours))
  
  
  df_cumulate$Depart_Date <-  df_cumulate$Depart_Date %>% substr(1,10) %>% as.POSIXct()
  df_cumulate$Depart_Time <- substr(df_cumulate$Depart_Time %>% as.POSIXct(format = "%H:%M:%OS"),12,16)
  df_cumulate$Depart_Date <- as.POSIXct(paste(df_cumulate$Depart_Date, df_cumulate$Depart_Time), format = "%Y-%m-%d %H:%M")
  df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% as.character()
  dbWriteTable(conn_rmysql, name = "sortie_accumulated_hours" , value = df_cumulate, 
               overwrite = TRUE, row.names = FALSE)
}