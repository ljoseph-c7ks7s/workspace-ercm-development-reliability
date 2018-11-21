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
df_full[df_full[,"Depart_Date"] < as.Date('1950-01-01'), 5] <- df_full[df_full[,"Depart_Date"] < as.Date('1950-01-01'), 8]
df_cumulate <- as.data.frame(df_full)
dbDisconnect(con)


C_130_CBM_sheet1 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx") %>% 
  as.data.frame()
C_130_CBM_sheet2 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx", sheet = 2)%>% 
  as.data.frame()
C_130_CBM_sheet3 <- read_excel("P:/External Projects/3134 - eRCM/Software - Models - Analyses - Data/C-130 CBM components and systems.xlsx", sheet = 3)%>% 
  as.data.frame()


C_130_CBM_components_and_systems <- bind_rows(C_130_CBM_sheet2, C_130_CBM_sheet1,  C_130_CBM_sheet3)

df_i$Serial_Number <- trimws(df_i$Serial_Number, which = "both")
df_cumulate$Serial_Number <- trimws(df_cumulate$Serial_Number, which = "both")

##Edit Sortie Data
##Find all of the columns without unique items & cleaning
track <- c()
for(i in 1:ncol(df_i)){
  if(length(unique(df_i[,i])) == 1|length(unique(df_i[,i]))== 2){
    track <- c(track, i)
  }
}

df_clean <- df_i %>% select(c(Work_Unit_Code, On_Component_Serial_Number,
                              On_Component_Part_Number, Equipment_Designator,
                              Serial_Number, Geographic_Location, 
                              Performing_Geographic_Location, Transaction_Date,
                              Work_Center_Code, When_Discovered_Code, 
                              How_Malfunction_Code, Action_Taken_Code, 
                              Type_Maintenance_Code, Current_Operating_Time, 
                              Component_Position_Number, Corrective_Narrative, 
                              Discrepancy_Narrative, Work_Center_Event_Narrative))

##Filter down to WUC's in the study##
df_phase1 <- dplyr::filter(df_clean, Work_Unit_Code %in% 
                             C_130_CBM_components_and_systems$WUC)

##Limit serial numbers to those associated with the WUC in the study
df_cumulate <- dplyr::filter(df_cumulate, Serial_Number %in% df_phase1$Serial_Number)
df_cumulate <- df_cumulate[order(df_cumulate$Serial_Number, 
                                             df_cumulate$Depart_Date, df_cumulate$Depart_Time),]
df_cumulate$Flying_Hours <- as.numeric(df_cumulate$Flying_Hours)

##OH NO A FOR LOOP- get cumulative flying hours by Serial Number ##
##df_cumulate is the sortie data with the hours accumulated by serial number##
for(i in 1:nrow(df_cumulate)-1){
  if(identical(df_cumulate[i,2], df_cumulate[i+1, 2])){
    df_cumulate[i+1,10] <-df_cumulate[i+1,10]+ df_cumulate[i,10] 
  }else{
    df_cumulate[i+1,10] <- df_cumulate[i+1,10]
  }
}

##Fix the fill-in##
##Change 0 to NA##
df_phase1$Current_Operating_Time[df_phase1$Current_Operating_Time == 0] <- NA

##Find first entry in Sortie Data##
first <- df_full %>%
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

df_first <- c()
for(i in 1:nrow(first)){
  check_me <- dplyr::filter(remainder, Serial_Number == first[i,'Serial_Number'])
  after_sortie_df <- dplyr::filter(check_me, Transaction_Date < first[i,'Depart_Date'])
  df_first <- rbind(df_first, after_sortie_df)
}

df_first <- filter(df_first, !is.na(Current_Operating_Time))

df_append <- c()
for(i in 1:nrow(first)){
  check_me <- dplyr::filter(remainder, Serial_Number == first[i,'Serial_Number'])
  after_sortie_df <- dplyr::filter(check_me, Transaction_Date >= first[i,'Depart_Date'])
  df_append <- rbind(df_append, after_sortie_df)
}

##append the two together##
##Note: Serial_Number == NA is omitted because it could not be serialized/analyzed##
df_phase1 <- df_append

##Get entries that do not need to be changed
data_reserve <- dplyr::filter(df_phase1, !is.na(Current_Operating_Time))

##Get entries that do need to be filled in 
data_edit <- dplyr::filter(df_phase1, is.na(Current_Operating_Time)) ##From REMIS
data_edit$Transaction_Date <- lubridate::ymd(data_edit$Transaction_Date) ##Change Date format

##Isolate the dates of interst to check against for closest date
df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% ymd_hms()
df_cumulate$Depart_Date <- df_cumulate$Depart_Date %>% as.character()

date_check <- df_cumulate[,c('Depart_Date','Serial_Number')] %>% 
  as.data.frame() %>%
  unique()
date_check$Depart_Date <- date_check$Depart_Date %>% ymd()

##Generate a new vector with the closest date in Sortie to the Transaction Date
new_date <- c()
for(i in 1:nrow(data_edit)){
  data_check <- filter(date_check, Serial_Number == data_edit[i,"Serial_Number"])
  new_date <- rbind(new_date, data_check[which.min(abs(difftime(data_edit[i,'Transaction_Date'],data_check[,1], units = 'days'))),1]
                    %>% as.character())
}

data_edit <- filter(data_edit, Serial_Number %in% date_check$Serial_Number)
data_edit <- cbind(data_edit, new_date)
data_edit$new_date <- as.Date(data_edit$new_date)



##Get the flight hours for REMIS DATA
#sortie_mergeset <- dplyr::filter(df_cumulate, Serial_Number %in% data_edit$Serial_Number)
sortie_mergeset <- df_cumulate[,c('Flying_Hours', 'Serial_Number', 'Depart_Date', 
                                  'Total_Landings', 'Full_Stop_Landings')]
colnames(sortie_mergeset) <- c('Flying_Hours', 'Serial_Number', 'new_date', 
                               'Total_Landings', 'Full_Stop_Landings')
sortie_mergeset$new_date <- as.Date(sortie_mergeset$new_date)

merged_set <- merge(sortie_mergeset, data_edit, by= c('Serial_Number','new_date'))
merged_set$Current_Operating_Time <- merged_set$Flying_Hours
merged_set <- merged_set %>% select(-Flying_Hours)



##Validation/Fixing##
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
data_reserve$new_date<- lubridate::ymd(data_reserve$new_date)

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

##Merged data_edit with adjustment so that we could get the desired adjustment
##Added adjustment to current operating time (which is the Flight_Hours)
fixed_merge <- merge(merged_set, adjustment, by = "Serial_Number")
fixed_merge$Current_Operating_Time <- fixed_merge$Current_Operating_Time + fixed_merge$Mean_Adj
fixed_merge <- select(fixed_merge, -Mean_Adj)

unfixed_merge <- dplyr::filter(merged_set, !Serial_Number %in% fixed_merge$Serial_Number)

merged_set <- rbind(fixed_merge, unfixed_merge) ##Adjusted for the mean difference and everything!!

##Edit data_reserve to have adjusted flight instead of current hours##
merged_ver <- merge(merged_ver, adjustment, by= "Serial_Number")
merged_ver$Current_Operating_Time <- merged_ver$Flying_Hours + merged_ver$Mean_Adj
merged_ver <- select(merged_ver, -c('Mean_Adj', 'Flying_Hours', 'flight_diff'))
merged_ver <- select(merged_ver, -'new_date')
df_first$Full_Stop_Landings <- rep(NA, nrow(df_first))
df_first$Total_Landings <- rep(NA, nrow(df_first))
data_reserve <- rbind(merged_ver, df_first)

merged_set <- select(merged_set, -'new_date')
C130_corrected <- rbind(merged_set, merged_ver) ##Transaction Date Filled-in using Sortie




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

##Label Events
df_interval_causal <- filter(df_interval, Action_Taken_Code == "Q")
df_interval_suspension <- filter(df_interval, Action_Taken_Code != "Q")

df_interval_causal$Event <- rep("Causal", nrow(df_interval_causal))
df_interval_suspension$Event <- rep("Suspension", nrow(df_interval_suspension))
df_interval <- rbind(df_interval_causal, df_interval_suspension)

df_interval <- df_interval %>%
  arrange(Transaction_Date, Serial_Number, Work_Unit_Code, 
          Component_Position_Number, desc(Action_Taken_Code))

