library(dplyr)
library(tidyr)
library(tibble)
library(lubridate)
library(ggplot2)
library(ggridges)
library(RMySQL)
library(foreign)
library(stringr)
library(ggmap)
library(geosphere)
library(purrr)
SERVER = "127.0.0.1"
PORT = 3307
db = "ercm"
USER_NAME = "root"
PASSWORD = "root"
CLOCKWORK_BLUE <- "#1198B9"
DARK_BLUE <- "#08596d"

conn_rmysql <- dbConnect(drv = MySQL(), dbname = db, username = USER_NAME, password = PASSWORD, host = SERVER, port = PORT)

# extract and clean -------------------------------------------------------

df_sortie <- dbGetQuery("select mds, serial_number, depart_icao, depart_date,depart_time, land_icao, land_date,land_time, flying_hours, total_landings, full_stop_landings from compiled_sortie_history_data order by depart_date, depart_time", 
                        con=conn_rmysql) %>% tibble::as_tibble()
df_sortie$depart_date <- ymd_hms(df_sortie$depart_date) %>% ymd()
df_sortie$land_date <- ymd_hms(df_sortie$land_date) %>% ymd()
df_sortie <- df_sortie %>% filter(depart_date > ymd("2000-01-01"))

df_remis <- dbGetQuery("select equipment_designator, serial_number, job_control_number, on_work_order_key, on_maint_action_key, work_center_event_identifier, sequence_number, 
transaction_date, start_time, stop_time, command, geographic_location, performing_geographic_location, work_unit_code, wuc_narrative,
component_position_number, type_maintenance_code, action_taken_code, when_discovered_code, how_malfunction_code, how_malfunction_class_ind
discrepancy_narrative, corrective_narrative, work_center_event_narrative, labor_manhours
from compiled_c130_remis_data order by transaction_date", con=conn_rmysql) %>% tibble::as_tibble()
df_remis$transaction_date <- ymd(df_remis$transaction_date)

#icao_lookup <- foreign::read.dbf("/home/travis/Documents/projects/c130_demo/data/wld_trs_airports_wfp.dbf", as.is = TRUE) %>% as.tibble() %>%
#  filter(!is.na(icao)) %>% select(icao, latitude, longitude)
# better data at
# https://openflights.org/data.html#airport
icao_lookup <- readr::read_csv("/home/travis/Documents/projects/c130_demo/data/icao_lookup.csv") %>%
  filter(!is.na(icao)) %>% filter(icao, latitude, longitude)

# eda ---------------------------------------------------------------------

# histogram of sorties per serial number
df_sortie %>% count(serial_number) %>% ggplot(aes(x=n)) + geom_histogram(boundary=0, binwidth = 250) + ggtitle("serial numbers with x sorties")

# sorties per serial number by platform type
df_sortie %>% count(serial_number, mds) %>% ggplot(aes(x=n)) + geom_histogram(boundary=0, binwidth = 250) + facet_wrap(~mds)
df_sortie %>% count(serial_number, mds) %>% ggplot(aes(x=n, colour = mds)) + geom_freqpoly(boundary=0, binwidth = 250) + ggtitle("serial numbers with x sorties by MDS")

# sorties by date by platform type
df_sortie %>% count(year = year(depart_date), mds) %>% ggplot(aes(y=n, x=year, colour = mds)) + geom_line() + ggtitle("sorties by MDS and year")

# manual flights per day, manually grouped by month
# geom_bar stat=count automatically plots rowcount per x
df_sortie %>% mutate(depart_month = floor_date(depart_date, "month")) %>% ggplot(aes(depart_month)) + geom_bar(stat="count")
# grouped by year
df_sortie %>% mutate(depart_year = floor_date(depart_date, "year")) %>% ggplot(aes(depart_year)) + geom_bar(stat="count")
# sum flight hours by year
# geom_bar stat=identity automatically plots numbers as they are (using specified y as height)
df_sortie %>% mutate(depart_year = floor_date(depart_date, "year")) %>% group_by(depart_year) %>%
  summarize(yearly_flight_hours=sum(flying_hours)) %>% ggplot(aes(x = depart_year, y = yearly_flight_hours)) + geom_bar(stat = "identity")

## icao data
# how many sortie depart locations match in our dataset? (fewer than half for the data dot world dataset. most for other data set)
df_sortie %>% left_join(x=., y=select(icao_lookup, icao) %>% mutate(lookup_exists=TRUE), by = c("depart_icao"="icao")) %>% count(lookup_exists)
df_sortie %>% left_join(x=., y=select(icao_lookup, icao) %>% mutate(lookup_exists=TRUE), by = c("depart_icao"="icao")) %>% count(depart_icao, lookup_exists) %>% arrange(desc(n))

# join all with icao
df_sortie <- df_sortie %>% left_join(x=., y=select(icao_lookup, icao, d_lat=latitude, d_long=longitude), by = c("depart_icao"="icao")) %>% 
  left_join(x=., y=select(icao_lookup, icao, l_lat=latitude, l_long=longitude), by = c("land_icao"="icao"))

#map <- get_openstreetmap(sortie_borders, zoom = 2,)
mapWorld <- borders("world", colour="gray70", fill="gray70") # create a layer of borders
# departs
df_sortie %>% group_by(depart_icao,d_lat,d_long) %>% 
  summarise(avg_hrs=mean(flying_hours)) %>% drop_na() %>% ggplot(aes(x=d_long,y=d_lat,size=n)) + 
  mapWorld + geom_point(col="midnightblue", alpha=1/2) + ggtitle("Departures")
# landings
df_sortie %>% count(l_lat,l_long) %>% drop_na() %>% ggplot(aes(x=l_long,y=l_lat,size=n)) + 
  mapWorld + geom_point(col="midnightblue", alpha=1/2) + ggtitle("Landings")

# distance traveled (default is meters)
system.time(df_sortie <- df_sortie %>% mutate(dist = purrr::pmap_dbl(.l = list(.$d_long, .$d_lat, .$l_long, .$l_lat), ~ distm(x = c(..1, ..2), y=c(..3, ..4), fun=distHaversine))))
df_sortie$dist <- df_sortie$dist*0.000621371 # miles per meter
df_sortie %>% drop_na() %>% ggplot(aes(x=dist)) + geom_freqpoly(binwidth=100)
df_sortie %>% drop_na() %>% ggplot(aes(x=dist)) + geom_histogram(binwidth=100)
df_sortie %>% drop_na() %>% ggplot(aes(x=dist,col=mds)) + geom_freqpoly(binwidth=100)

# time-of-day
df_sortie %>% ggplot(aes(x=depart_time)) + geom_histogram(boundary=0, binwidth=100) + ggtitle('departs')
df_sortie %>% ggplot(aes(x=land_time)) + geom_histogram(boundary=0, binwidth=100) + ggtitle('lands')
rbind(tibble(times=df_sortie$depart_time, type="depart"), tibble(times=df_sortie$land_time, type="lands")) %>% 
  ggplot(aes(x=times, col=type)) + geom_freqpoly(binwidth=100)
# add time to dates
df_sortie <- df_sortie %>% mutate(d_datetime = purrr::map(.x = .$depart_time, .f = ~ paste(sprintf("%02d", floor(./100)), sprintf("%02d",. %% 100), sep=":")),
                                  l_datetime = purrr::map(.x = .$land_time, .f = ~ paste(sprintf("%02d", floor(./100)), sprintf("%02d",. %% 100), sep=":"))) %>% 
  unnest() %>% mutate(d_datetime = ymd_hm(paste(depart_date, d_datetime)),
                      l_datetime = ymd_hm(paste(land_date, l_datetime)))

hist(df_sortie$flying_hours)

# average flight hours per sortie by icao
df_sortie %>% group_by(depart_icao) %>% summarize(avg_flying_hours=mean(flying_hours))
df_sortie %>% group_by(depart_icao) %>% summarize(avg_flying_hours=mean(flying_hours)) %>% pull(avg_flying_hours) %>% hist

# aggregate flight hours
df_sortie %>% group_by(depart_date) %>% summarize(flying_hours = sum(flying_hours)) %>% 
  ggplot(aes(x=depart_date, y=flying_hours)) + geom_line() + ggtitle("flying hours per day") + geom_smooth()

df_sortie %>% group_by(depart_date) %>% summarize(flying_hours = sum(flying_hours)) %>% mutate(accrued_flying_hours = cumsum(flying_hours)) %>%  
  ggplot(aes(x=depart_date, y=accrued_flying_hours/1e6)) + geom_line() + ggtitle("accrued flight hours") + ylab("Millions of Flying Hours") + xlab("Date")

## histograms
# sortie
p1 <- df_sortie %>% ggplot(aes(x=flying_hours)) + geom_histogram(stat = "bin", boundary = 0, binwidth = 1, fill=DARK_BLUE, color="white") + theme_classic() +
  scale_y_continuous(name="Count of Flights", labels=scales::comma) + xlab("Flying Hours") + ggtitle("Flying Hours per Sortie") + theme(axis.text=element_text(size=13))
# day and serial number
p2 <- df_sortie %>% group_by(serial_number, depart_date) %>% summarise(flying_hours = sum(flying_hours)) %>% 
  ggplot(aes(x=flying_hours)) + geom_histogram(stat = "bin", boundary = 0, binwidth = 1, fill=DARK_BLUE, color="white") + theme_classic() +
  scale_y_continuous(name="Count of Flights", labels=scales::comma) + xlab("Flying Hours") + ggtitle("Flying Hours per Aircraft Per Day, non-zero") +
  theme(axis.text=element_text(size=13))
# month and serial number
p3 <- df_sortie %>% mutate(mo = floor_date(depart_date, "months")) %>% group_by(serial_number, mo) %>% summarise(flying_hours = sum(flying_hours)) %>% 
  ggplot(aes(x=flying_hours)) + geom_histogram(stat = "bin", boundary = 0, binwidth = 10, fill=DARK_BLUE, color="white") + theme_classic() +
  scale_y_continuous(name="Count of Flights", labels=scales::comma) + xlab("Flying Hours") + ggtitle("Flying Hours per Aircraft Per Month, non-zero") +
  theme(axis.text=element_text(size=13))
# year and serial number
p4 <- df_sortie %>% mutate(mo = floor_date(depart_date, "years")) %>% group_by(serial_number, mo) %>% summarise(flying_hours = sum(flying_hours)) %>% 
  ggplot(aes(x=flying_hours)) + geom_histogram(stat = "bin", boundary = 0, binwidth = 50, fill=DARK_BLUE, color="white") + theme_classic() +
  scale_y_continuous(name="Count of Flights", labels=scales::comma) + xlab("Flying Hours") + ggtitle("Flying Hours per Aircraft Per Year, non-zero") +
  theme(axis.text=element_text(size=13))

plot_grid(p1, p2, p3, p4)

# single sn ---------------------------------------------------------------

# single SN
sn = "0200000314"
df_sortie_1_sn <- df_sortie %>% filter(serial_number == sn)

df_remis <- dbGetQuery(gsub(pattern='{{}}', replacement=sn, x="select equipment_designator, serial_number, job_control_number, on_work_order_key, on_maint_action_key, work_center_event_identifier, sequence_number, 
transaction_date, start_time, stop_time, command, geographic_location, performing_geographic_location, work_unit_code, wuc_narrative,
component_position_number, type_maintenance_code, action_taken_code, when_discovered_code, how_malfunction_code, how_malfunction_class_ind
discrepancy_narrative, corrective_narrative, work_center_event_narrative, labor_manhours
from c130_remis_data where serial_number = '{{}}' order by transaction_date", fixed=TRUE), con=conn_rmysql) %>% tibble::as_tibble()
df_remis$transaction_date <- ymd(df_remis$transaction_date)

# find month
df_sortie$Depart_Month <- floor_date(df_sortie$Depart_Date, "month")
df_remis$transaction_month <- floor_date(df_remis$transaction_date, "month")

sorties_per_month <- df_sortie %>% count(Depart_Month)
maintenance_hrs_per_month <- df_remis %>% group_by(transaction_month) %>% summarize(labor_hours = sum(labor_manhours))

df_remis %>% group_by(transaction_date) %>% summarize(labor_hours = sum(labor_manhours)) %>%
  ggplot(aes(x=transaction_date, y = labor_hours)) + geom_point()

# find days with some maintenance, days with some sortie
min_date <- min(min(df_remis$transaction_date), min(df_sortie$Depart_Date))
max_date <- max(max(df_remis$transaction_date), max(df_sortie$Depart_Date))
date_range <- tibble(date_range=seq(min_date, max_date, by="days"))
plot_df <- date_range %>% left_join(
    df_sortie %>% count(Depart_Date) %>% rename(items=n), by = c("date_range"="Depart_Date")) %>%
  mutate(type="sorties") %>%
  rbind(date_range %>% 
    left_join(df_remis %>% count(transaction_date) %>% rename(items=n), by = c("date_range"="transaction_date")) %>%
      mutate(type="maint_actions")
  ) %>% drop_na()
ggplot(plot_df, aes(x = date_range, y = items)) + geom_point(aes(colour=type))
ggplot(plot_df, aes(x = date_range, y = if_else(type=="sorties","sortie","maint"))) + geom_point() + ylab("Action Occurred") +
  xlim(ymd("2016-10-01"), NA)


## custom function
cust_func <- function(sn, x, df_dates){
  two_options <- c("after_td"=df_dates %>% filter(serial_number == sn, depart_date >= x) %>% head(1) %>% pull(depart_date),
                   "before_td"=df_dates %>% filter(serial_number == sn, depart_date <= x) %>% head(1) %>% pull(depart_date))
  if(abs(difftime(x, two_options["after_td"])) > abs(difftime(x, two_options["before_td"]))){
    return(two_options["before_td"])
  } else {
    return(two_options["after_td"])
  }
}
x <- select(df_remis, transaction_date, serial_number) %>% 
  mutate(closest_dt = purrr::map2(serial_number, transaction_date, 
                                  .f = ~ cust_func(.x, .y, select(df_sortie, serial_number, depart_date))))

         

# missing sortie data -----------------------------------------------------
sns_no_old <- readr::read_csv("/home/travis/Documents/projects/eRCM/Missing Sortie Data.csv") %>% as.tibble()
df_sortie <- df_sortie %>% filter(depart_date>ymd("1950-01-01"))
df_sortie %>% filter(mds %in% c("C130H", "C130J"), 
                     serial_number %in% (df_sortie %>% pull(serial_number) %>% unique() %>% head(200))) %>% 
  ggplot(aes(x=depart_date,y=serial_number)) + 
  geom_density_ridges(rel_min_height = 0.01)

df_sortie %>% filter(mds %in% c("C130H","C130J")) %>% distinct(serial_number) %>% nrow()  # 409
df_sortie %>% filter(mds %in% c("C130H","C130J"), depart_date < ymd("2010-01-01")) %>% 
  distinct(serial_number) %>% nrow()  # 350
df_sortie %>% filter(mds %in% c("C130H","C130J"), depart_date < ymd("2007-01-01")) %>% 
  distinct(serial_number) %>% nrow()  # 323

# plot with date range below 2010
df_sortie %>% filter(mds %in% c("C130H", "C130J"), depart_date < ymd("2010-01-01"),
                     serial_number %in% (df_sortie %>% pull(serial_number) %>% unique() %>% head(200))) %>% 
  ggplot(aes(x=depart_date,y=serial_number)) + 
  geom_density_ridges(rel_min_height = 0.01)

# plot only those SNs that are not below 2010
df_sortie %>% filter(mds %in% c("C130H", "C130J"), 
                     !(serial_number %in% (df_sortie %>% 
                       filter(mds %in% c("C130H","C130J"), depart_date < ymd("2010-01-01")) %>% 
                       pull(serial_number) %>% unique()))) %>% 
  ggplot(aes(x=depart_date,y=serial_number)) + 
  geom_density_ridges(rel_min_height = 0.01)

# plot only those SNs that Kevin found missing
df_sortie %>% filter(mds %in% c("C130H", "C130J"), 
                     serial_number %in% sns_no_old$.) %>% 
  ggplot(aes(x=depart_date,y=serial_number)) + 
  geom_density_ridges(rel_min_height = 0.01)

# plot densities of both maintenance and flight hours for a few of these serial numbers
sns <- c("080003172", "0700046312", "1000005700")
df <- bind_rows(
  df_sortie %>% filter(serial_number %in% sns) %>% select(date=depart_date, serial_number) %>% mutate(action_type="sortie"),
  df_remis %>% filter(serial_number %in% sns) %>% select(date=transaction_date, serial_number) %>% mutate(action_type="maintenance")
)
df %>% ggplot(aes(x=date, y=serial_number)) + geom_density_ridges(aes(fill=action_type))
