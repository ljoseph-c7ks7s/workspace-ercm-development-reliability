library(lubridate)
library(dplyr)
library(DBI)
library(RMySQL)
library(RODBC)
library(sqldf)
library(tidyr)
library(readxl)
##Read in Necessary files
con <- dbConnect(drv = MySQL(),
                 dbname="ercm",
                 username="root",
                 password="",
                 host="localhost",
                 port=3306)
df_i <- dbGetQuery(con, 'SELECT * FROM c130_remis_data ')
df_i <- as.data.frame(df_i)

df_full <- dbGetQuery(con, 'SELECT * FROM ercm.sortie_merged')
df_cumulate <- as.data.frame(df_full)
dbDisconnect(con)
df_full[df_full[,"Depart_Date"] < as.Date('1950-01-01'), 5] <- df_full[df_full[,"Depart_Date"] < as.Date('1950-01-01'), 8]

C_130_CBM_sheet1 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx") %>% 
  as.data.frame()
C_130_CBM_sheet2 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx", sheet = 2)%>% 
  as.data.frame()
C_130_CBM_sheet3 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx", sheet = 3)%>% 
  as.data.frame()


C_130_CBM_components_and_systems <- bind_rows(C_130_CBM_sheet2, C_130_CBM_sheet1,  C_130_CBM_sheet3)


##Edit Sortie Data
##Find all of the columns without unique items & cleaning
track <- c()
for(i in 1:ncol(df_i)){
  if(length(unique(df_i[,i])) == 1|length(unique(df_i[,i]))== 2){
    track <- c(track, i)
  }
}

df_clean <- df_i[,-c("Record_Identifier", "Block_Number", "Activity_Identifier", 
                     "Install_Lot_Number", "Install_Location_Identifier", 
                     "Remove_Lot_Number", "Remove_Location_Identifier", 
                     "On_Base_Turn_In_Doc_Number", "Column_for_Asterisks" )]

##Filter down to WUC's in the study##
df_phase1 <- dplyr::filter(df_clean, Work_Unit_Code %in% 
                             C_130_CBM_components_and_systems$WUC)

##Limit serial numbers to those associated with the WUC in the study
df_cumulate_match <- dplyr::filter(df_cumulate, Serial_Number %in% df_phase1$Serial_Number)
df_cumulate_match <- df_cumulate_match[order(df_cumulate_match$Serial_Number, 
                                             df_cumulate_match$Depart_Date, df_cumulate_match$Depart_Time),]
df_cumulate_match$Flying_Hours <- as.numeric(df_cumulate_match$Flying_Hours)

##OH NO A FOR LOOP- get cumulative flying hours by Serial Number ##
##df_cumulate is the sortie data with the hours accumulated by serial number
for(i in 1:nrow(df_cumulate_match)-1){
  if(identical(df_cumulate_match[i,2], df_cumulate_match[i+1, 2])){
    df_cumulate_match[i+1,10] <-df_cumulate_match[i+1,10]+ df_cumulate_match[i,10] 
  }else{
    df_cumulate_match[i+1,10] <- df_cumulate_match[i+1,10]
  }
}
df_cumulate <- df_cumulate_match

##Fix the fill-in##
##Change 0 to NA
df_phase1$Current_Operating_Time[df_phase1$Current_Operating_Time == 0] <- NA

##Get entries that do not need to be changed
data_reserve <- dplyr::filter(df_phase1, !is.na(Current_Operating_Time))

##Get entries that do need to be filled in 
data_edit <- dplyr::filter(df_phase1, is.na(Current_Operating_Time)) ##From REMIS
data_edit$Transaction_Date <- lubridate::ymd(data_edit$Transaction_Date) ##Change Date format

##Isolate the dates of interst to check against for closest date
date_check <- lubridate::ymd_hms(df_cumulate$Depart_Date) %>% 
  as.data.frame() %>% 
  unique()
date_check <- date_check[,1] %>% ymd()

##Generate a new vector with the closest date in Sortie to the Transaction Date
new_date <- c()
for(i in 1:nrow(data_edit)){
  new_date <- rbind(new_date, date_check[which.min(abs(difftime(data_edit[i,'Transaction_Date'],date_check, units = 'days')))]
                    %>% as.character())
}
data_edit <- cbind(data_edit, new_date)
data_edit$new_date <- lubridate::ymd(data_edit$new_date)

##Get the flight hours for REMIS DATA
sortie_mergeset <- dplyr::filter(df_cumulate, Serial_Number %in% data_edit$Serial_Number)
sortie_mergeset <- sortie_mergeset[,c('Flying_Hours', 'Serial_Number', 'Depart_Date')]
colnames(sortie_mergeset) <- c('Flying_Hours', 'Serial_Number', 'new_date')
sortie_mergeset$new_date <- ymd_hms(sortie_mergeset$new_date)

merged_set <- merge(sortie_mergeset, data_edit, by= c('Serial_Number','new_date'))
merged_set$Current_Operating_Time <- merged_set$Flying_Hours
merged_set <- merged_set %>% select(-Flying_Hours)
merged_set <- merged_set[,c(3:8,1,9:75,2)]


##Validation/Fixing##
##Finding the closest date to the Transaction Date (they were all the same day)
data_reserve$Transaction_Date <- lubridate::ymd(data_reserve$Transaction_Date)
new_date <- c()
for(i in 1:nrow(data_reserve)){
  new_date <- rbind(new_date, date_check[which.min(abs(difftime(data_reserve[i,'Transaction_Date'],date_check, units = 'days')))]
                    %>% as.character())
}
data_reserve <- cbind(data_reserve, new_date)
data_reserve$new_date <- lubridate::ymd(data_reserve$new_date)

##Isolate Sortie data with serial numbers identical to those we are confirming flight hours against
sortie_ver <- dplyr::filter(df_cumulate, Serial_Number %in% data_reserve$Serial_Number)
sortie_ver <- sortie_ver[,c('Flying_Hours', 'Serial_Number', 'Depart_Date')]
colnames(sortie_ver) <- c('Flying_Hours', 'Serial_Number', 'new_date')
sortie_ver$new_date <- ymd_hms(sortie_ver$new_date)

## Merge data sets by serial number and new date so we can get the associated flight hours
##merge results in 284 results, due to not all serial numbers being present in previous data frame
data_reserve$new_date <- data_reserve$new_date %>% ymd()
merged_ver <- merge(sortie_ver, data_reserve, by= c('Serial_Number','new_date'))

##Defined a new column that is the difference in flight hours
merged_ver$flight_diff <- merged_ver$Current_Operating_Time- merged_ver$Flying_Hours
merged_ver$flight_diff <- as.numeric(merged_ver$flight_diff)
adjustment <- aggregate(merged_ver[, 'flight_diff'], list(merged_ver$Serial_Number), mean)
colnames(adjustment) <- c("Serial_Number", "Mean_Adj")

##Merged data_edit with adjustment so that we could get the desired adjustement
##Added adjustment to current operating time (which is the Flight_Hours)
fixed_merge <- merge(merged_set, adjustment, by = "Serial_Number")
fixed_merge$Current_Operating_Time <- fixed_merge$Current_Operating_Time + fixed_merge$Mean_Adj
fixed_merge <- select(fixed_merge, -Mean_Adj)

unfixed_merge <- dplyr::filter(merged_set, !Serial_Number %in% fixed_merge$Serial_Number)

merged_set <- rbind(fixed_merge, unfixed_merge) ##Adjusted for the mean difference and everything!!


C130_corrected <- rbind(data_reserve, merged_set) ##Transaction Date Filled-in using Sortie

##Isolate to only Interval Data
interested <- c( "Q", "R", "P", "T", "U")
df_interval <- dplyr::filter(C130_corrected, Action_Taken_Code %in% interested)
df_interval_PQ <- dplyr::filter(df_interval, Action_Taken_Code != "R")

df_interval_R <- dplyr::filter(C130_corrected, Action_Taken_Code == "R")

df_interval_P <-df_interval_R
df_interval_Q <-df_interval_R

df_interval_P$Action_Taken_Code <- rep("P", nrow(df_interval_P))
df_interval_Q$Action_Taken_Code <- rep("Q", nrow(df_interval_Q))

df_interval <- rbind(df_interval_PQ, df_interval_P, df_interval_Q)
unique(df_interval$Action_Taken_Code)

