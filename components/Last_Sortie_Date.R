fn <- function(conn_rmysql, load_path, params_path, component_path, output_file) {
  library(dplyr)
  ##import model
  df_cumulated <- dbGetQuery(conn_rmysql, 'SELECT * FROM ercm.current_sortie_date_and_adjusted_flying_hours')
  
  ##find last date
  df_sortie_last <- df_cumulated %>%
  group_by(Serial_Number) %>%
  arrange(desc(Depart_Date)) %>%
  slice(1L)
  
  ##Current Sortie Dates
  dbWriteTable(conn_rmysql, name = "last_sortie_date", value = df_sortie_last, 
             overwrite = TRUE, row.names = FALSE)
}