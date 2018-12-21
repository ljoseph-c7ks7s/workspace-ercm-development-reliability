suppressPackageStartupMessages(library("RMySQL")) # database connection
suppressPackageStartupMessages(library("dplyr")) # data manipulation
suppressPackageStartupMessages(library("ggplot2")) # plotting
suppressPackageStartupMessages(library("tidyr")) # data manipulation, grouping
suppressPackageStartupMessages(library("purrr")) # data manipulation
suppressPackageStartupMessages(library("grid")) # unit function
suppressPackageStartupMessages(library("lubridate")) # date functions

SERVER <- "localhost"
USER_NAME <- "root"
PASSWORD <- ""
PORT <- 3306
# currently hardcoded for specific configuration of events for corrosion

# Features

### Group Choices
## user can select to custom grouping by combining up to three categories
# location
# serial number
# wuc
## with an optional one of two secondary selections
# event type
# maintenance level

## Aggregating and Filtering
#   User can aggregate a factor to ignore it.  It has no impact on plot data or filtering or factor choice filters
#    Currently unselecting Aggregate (disaggregating) and filtering must either both be selected or neither selected
#    Disaggregating
#   Currently only one factor of Location, SN, or WUC can get disagregated
#  TODO: add a "Filter" checkbox (see below)
# Filtering vs. Cascade Filtering:
# Filtering:
#   Currently only for Event Label:
#   Impacts the data in the plot, but not the options of other factors
# Cascade Filtering
#  When filtering one factor category, the other factor choices are recalculated:
#   each check/selection re-queries the possible options for each of the factor choices
#   This requires keeping track of factor type dissaggregate click order, and not allowing factor choices in factors
#     selected late to impact the factor choices of those factors selected first
#    An additional required feature is remembering the previous factor selections (selected options)
#     b/c options are re-calculated for all clicks even if it doesn't change the options (b/c of disaggregate-click-order)
#     this ensures the selections are still selected after the factor selection control reloads

##
# Time-line or Pareto
#  Ability to group by week, month, day, quarter, year

##
# Geographic Location nuance
#  Can choose performing location (where the maintenance is done) or assigned location (where the SN is stationed)

## 
# Normalization: Normalize Data by:
#   Avg # of events per year/month/qtr per assigned aircraft at a location or overall
#   Avg # of events per flight hours for each aircraft at a location or overall
#   Avg # of depot cycles for each aircraft overall

## Ability to Group by:
#   WUC subystems (2-, 3-, 4-, or 5- digits WUCs) or user-defined groups or General Support/Physical 

# TODO: use rCharts, remove legend (user can see which item a line represents by mouse-hover)
# TODO: add a "Filter" checkbox that filters other options based on selections but does not create new line for each combo
#  Four Options:
#   Aggregate and Do Not Filter: Default option - ignores this factor; options are hidden
#   Aggregate and Filter: factor options are revealed for filtering - all options are selected initially
#    will not create a new line or bar for each value, but unchecking options may remove some lines b/c no data
#   Disaggregate and Do Not Filter: creates a new line for each group combo but does not cascade filter options
#   Disaggregate and Filter: creates a new line for each group combo and applies cascade filtering of other factors' options
# TODO: consider setting date-axis labels, maybe based on the date group by selected
# TODO: consider using ids to filter instead of string matching

# Connect to DB -----------------------------------------------------------

source("../config.R")

# constants
error_message <- "No Data: Please Ensure Component has been Run"
error_message_qry_string <- "Missing Model Name"
error_message_predecessor <- "Missing Predecessor Id"

factor_size <- 4
axis_text_rel_size <- 1.3
axis_title_rel_size <- 1.6
legend_text_rel_size <- 1.2
legend_title_rel_size <- 1.3
pareto_label_rel_size <- 6
annot_pos_frac  <- 0.5 # bars with values above this fraction of the maximum-bar value will have annotations below the top of the bar
annot_pos_above <- 1.25 # positive values push the label below the bar height
annot_pos_below <- -0.15
annot_pos_below_dot <- -0.4

wuc_type_choices <- list("Five Digit" = "five", "Four Digit" = "four", 
                        "Three Digit" = "three", "Two Digit" = "two", 
                        "General Support vs. Physical" = "gen_sup", 
                        "User-Defined" = "user")
wuc_gen_sup_map <- list("1" = "General Support", "0" = "Physical", "None" = "None")

days_per_time <- list("Day" = 1, "Week" = 7, "Month" = 365.25/12, 
                      "Quarter" = 365.25/4, "Year" = 365.25)

selected_agg_order_map <- list('sn' = "Serial_Number", 
                               'loc' = c("Assigned_Location", "Assigned_Location_Name", 
                                         "Performing_Location", "Performing_Location_Name"), 
                               'wuc' = c("Work_Unit_Code", "reduced_wuc"),
                               'label' = "Label", 
                               'depot' = "Maintenance_Level") # five options: sn, loc, wuc, label, depot

factor_selection_order_map <- list('1' = 'Disagg. First', '2' = 'Disagg. Second', '3' = 'Disagg. Third', '4' = 'Disagg. Fourth')

lcm_palette <- c("#94ae0a","#115fa6","#a61120","#ff8809","#ffd13e","#a61187","#24ad9a","#7c7474","#a66111") # 9 colors
new_palette <- c("#6AABAB", "#B05C5C" ,"#A88F3E" ,"#685D96" ,"#B83989", "#67BF6F", "#B37542", "#197070", "#7D1F1F", "#6B5713", "#2C1D69", "#7A1C56" ,"#145C1B" ,"#663E1A", "#EB7C21", "#81A9D1", "#284C70" ,"#AACC46" ,"#50631E") # 19

chosen_color_brewer_palette <- "Set1" # Set 1 - 9 colors; Set 2 - 8 colors; Set 3 - 12 colors; Spectral - 11 colors
set1_palette <- c("#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999")
chosen_color_manual_palette <- c("#E41A1C","#377EB8","#4DAF4A","#984EA3","#FF7F00","#FFFF33","#A65628","#F781BF","#999999","#851111","#235075","#196119","#63256B","#A8A812","#A12C68","#404040")

max_colors <- length(chosen_color_manual_palette)
em_too_few_colors_defined <- paste("Maximum", max_colors, "line or bar segment colors allowed.  Please select fewer options.")
# Start Server ------------------------------------------------------------

shinyServer(
function(input, output, session) {
  
  ### PROCESS QUERY STRING
  qry_string <- reactive({parseQueryString(session$clientData$url_search)})
  
  database_name <- reactive(x = {
    if(is.null(qry_string()$workspace)){
      stop(error_message_qry_string)
    } else {
      return(qry_string()$workspace)
    }
  })
  
  component_name <- reactive(x = {
    if(is.null(qry_string()$id)){
      stop(error_message_qry_string)
    } else {
    return(qry_string()$id)
    }
  })
  
  predecessor_name <- reactive(x = {
    if(is.null(qry_string()$predecessor)){
      stop(error_message_predecessor)
    } else {
      return(qry_string()$predecessor)
    }
  })
  
  ### CONNECT TO DB
  conn <- reactive({
    if(is.null(qry_string()$id)){
      stop(error_message_qry_string)
    }
    dbConnect(drv = MySQL(), dbname = database_name(), username = USER_NAME, password = PASSWORD, host = SERVER, port = PORT)
  })
  
  # ReactiveValues ----------------------------------------------------------
  
  values <- reactiveValues()
  # reactive values are used for two reasons:
  # 1) to remember the value when it goes missing in the UI and the input value changes to NULL
  # 2) to control data filtering and plotting (immediate updates instead of delayed as inputs are delayed)
  # type selctions
  values$wuc_type_selection <- "five"
  values$loc_type_selection <- "Assigned"
  # specific selections - used to define selections when input$x_selection controls are generated and filtering
  #  useful b/c controls are often regenerated and we want to maintain the previous selections
  #  e.g. when changing options from another factor via cascading filtering
  values$sn_selection  <- ""
  values$wuc_selection <- ""
  values$loc_selection <- ""
  # normalization option
  values$normalize_option <- "None"
  
  # filtered events
  values$events_filtered <- data.frame()
  values$events_filtered_adj <- data.frame()
  
  # selected events from plot click
  values$nearest_events <- data.frame()
  
  # to control cascading filtering, keep track of the order of the selected disaggregation clicks.
  #  cascading filtering only works down the chain, i.e. choices made in the factor selected first 
  #   control options supplied to factors selected later and not vice versa
  values$selected_agg_order <- list()
  
  # Reactives -----------------------------------------------------------------------
  
  events <- reactive({
    if(is.null(qry_string()$id)){
      stop(error_message_qry_string)
    }
    to_return <- GracefulQuery(conn(), paste("SELECT * FROM", component_name()))
    if(is.null(to_return)){
      stop(error_message)
    }
    
    # apply null to none rendering and maintenance level
    if(is.null(to_return$Transaction_Date)){
      return(NULL)
    }
    to_return$Transaction_Date <- ymd(to_return$Transaction_Date) # date conversion
    to_return <- rename(to_return, id = Event_Id)
    
    if(is.null(to_return$Label)){
      to_return$Label <- NA
    }
    
    # Null to None Rendering
    fields_to_check <- c("Performing_Location", "Performing_Location_Name", "Assigned_Location", "Assigned_Location_Name", 
                          "Serial_Number", "Label", "Type_Maintenance_Code",
                         "Work_Unit_Code", "WUC_User_Defined", "WUC_Gen_Sup", "WUC_Assy", "WUC_Subsys", "WUC_Sys")
    for(field_name in fields_to_check){
      to_return <- ChangeNAtoNone(to_return, field_name)
    }
    
    # Change Type Maintenance Code to either Depot or Field and remove type maintenance
    to_return$Maintenance_Level <- ifelse(grepl("R", to_return$Type_Maintenance_Code), "Depot", "Field")
    to_return$Type_Maintenance_Code <- NULL
    
    return(to_return)
  })
  
  # SN Loc days active
  sn_loc_active_days <- reactive({
    if(is.null(events())){
      return(NULL)
    } 
    # Return SN assigned days at location and total assigned days
    events() %>% select(Serial_Number, Assigned_Location, Assigned_Location_Name, Days_SN_Asgn_Loc, Days_SN_Asgn_Tot) %>% distinct()
  })
  
  # SN Loc flying hours
  sn_loc_flying_hours <- reactive({
    if(is.null(events())){
      return(NULL)
    } 
  # Simply return the flight hours for each SN-Loc and total within SN across Loc
    # total calculated in SQL component because some flown locations aren't in the maintenance data
    events() %>% select(Serial_Number, Assigned_Location, Assigned_Location_Name, Fly_Hours_SN_Loc, Fly_Hours_SN_Tot) %>% distinct()
  })
  
  # SN depot cycles
  sn_depot_cycles <- reactive({
    if(is.null(events()) || is.null(events()$SN_Depot_Cycles)){
      return(NULL)
    } 
    events() %>% select(Serial_Number, Assigned_Location, Assigned_Location_Name, SN_Depot_Cycles) %>% distinct()
  })
  
  loc_field_name_id   <- reactive(paste(input$loc_type, "Location", sep = "_"))
  loc_field_name_name <- reactive(paste(input$loc_type, "Location", "Name", sep = "_"))
  
  ###                  ###
  ### BEGIN FILTERING  ###
  ###                  ###
  
  # There are two filtering tasks to do:
  #  1) filter events based on all group filters (SN, Loc, WUC, Event Label) to feed to plot
  #  2) filter events for each of the four group filters based on the other group filters
  # these tasks cannot be combined into one filtered event list, because that would ruin the list of available options to the user
  
  loc_options <- reactive({
    if (is.null(input$loc_agg) || is.null(input$loc_type) || is.null(events())) {
      return(NULL)
    }
    
    # control updates to loc options with isolate:
    #  depend only on wuc and sn selections IF they were disaggregated first
    isolate({
      sn_selection_local  <- values$sn_selection
      wuc_selection_local <- values$wuc_selection
      label_selection_local <- values$label_selection
      depot_selection_local <- values$depot_selection
    })
    
    # start with all events
    events_table <- events()
    
    # filter by serial number IF some specific serial numbers are chosen and SN was disaggregated before Location
    # this if check will throw an error if either 'sn' or 'loc' aren't in the reactivevalue - they should be there
    if (!is.null(sn_selection_local) && !input$sn_agg && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "sn") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      events_filter_by_sn <- semi_join(events_table, data.frame(Serial_Number = values$sn_selection), 
                                       by = "Serial_Number") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_sn <- events_table$id
    }
    # filter by wuc
    if (!is.null(wuc_selection_local) && !input$wuc_agg && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "wuc") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      events_table <- inner_join(events_table, select(wuc_map_selected_type(), Work_Unit_Code, reduced_wuc), by = "Work_Unit_Code")
      events_filter_by_wuc <- semi_join(events_table, data.frame(reduced_wuc = values$wuc_selection), 
                                        by = "reduced_wuc") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_wuc <- events_table$id
    }
    
    # filter by event labels
    if (!is.null(label_selection_local) && !input$label_agg && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      events_filter_by_label <- semi_join(events_table, data.frame(Label = values$label_selection), 
                                          by = "Label") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_label <- events_table$id
    }
    # filter by maintenance level
    if (!is.null(depot_selection_local) && !input$depot_agg && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      events_filter_by_depot <- semi_join(events_table, data.frame(Maintenance_Level = values$depot_selection), 
                                          by = "Maintenance_Level") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_depot <- events_table$id
    }
    
    # field names to use are made up of either assigned location or performing location id and name fields
    matching_ids <- purrr::reduce(.x=list(events_filter_by_sn, events_filter_by_wuc, 
                                          events_filter_by_label, events_filter_by_depot), .f=intersect)
    
    # order matches by total actions
    events_table_filtered <- select_(events_table, quote(id), loc_field_name_id(), 
                                     loc_field_name_name()) %>% semi_join(data.frame(id = matching_ids), by = "id") %>%
      group_by_(loc_field_name_id(), loc_field_name_name()) %>% summarise(actions = n()) %>% as.data.frame()
    
    # get either assigned location or performing location from filtered event list
      to_return <- as.list(select_(events_table_filtered, loc_field_name_id()) %>% Df2Vr())
      names(to_return) <- paste(events_table_filtered[, loc_field_name_id()],  
                                events_table_filtered[, loc_field_name_name()], sep = " - ")  
    
    # sort
    to_return <- to_return[order(events_table_filtered$actions, decreasing = TRUE)]
    # return only those locations that match all filters
    return(to_return)
  })
  
  # TODO: define a function these filters call to reduce code size
  sn_options <- reactive({
    if (is.null(input$sn_agg) || is.null(events())) {
      return(NULL)
    }
    
    # control updates to sn options with isolate:
    #  depend only on loc and wuc selections IF they were disaggregated first
    isolate({
      loc_selection_local <- values$loc_selection
      wuc_selection_local <- values$wuc_selection
      label_selection_local <- values$label_selection
      depot_selection_local <- values$depot_selection
    })
    
    # start with all serial numbers
    events_table <- events()
    
    # filter by location IF some specific locations are chosen 
    #  and location was disaggregated before SN (loc has priority cascade filtering)
    if (!is.null(loc_selection_local) && !input$loc_agg && 
        which(values$selected_agg_order[1:factor_size] == "loc") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      events_filter_by_loc <- events_table[events_table[, loc_field_name_id()] %in% values$loc_selection, "id"]
    } else {
      events_filter_by_loc <- events_table$id
    }
    # filter by wuc
    if (!is.null(wuc_selection_local) && !input$wuc_agg && 
        which(values$selected_agg_order[1:factor_size] == "wuc") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      events_table <- inner_join(events_table, select(wuc_map_selected_type(), Work_Unit_Code, reduced_wuc), by = "Work_Unit_Code")
      events_filter_by_wuc <- semi_join(events_table, data.frame(reduced_wuc = values$wuc_selection), 
                                        by = "reduced_wuc") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_wuc <- events_table$id
    }
    # filter by label
    if (!is.null(label_selection_local) && !input$label_agg && 
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      events_filter_by_label <- semi_join(events_table, data.frame(Label = values$label_selection), by = "Label") %>% 
        select(id) %>% Df2Vr()
    } else {
      events_filter_by_label <- events_table$id
    }
    # filter by depot
    if (!is.null(depot_selection_local) && !input$depot_agg && 
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      events_filter_by_depot <- semi_join(events_table, data.frame(Maintenance_Level = values$depot_selection), 
                                       by = "Maintenance_Level") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_depot <- events_table$id
    }
    
    matching_ids <- purrr::reduce(.x=list(events_filter_by_loc, events_filter_by_wuc, 
                                          events_filter_by_label, events_filter_by_depot), .f=intersect)
    
    # order matches by total actions then drop actions
    events_table_filtered <- select(events_table, id, Serial_Number) %>% 
      semi_join(data.frame(id = matching_ids), by = "id") %>%
      group_by(Serial_Number) %>% summarise(actions = n()) %>% arrange(desc(actions)) %>% select(-actions)
    ## TODO: to speed up code - keep this action count around and use it for the pareto, which now re-calculates actions
  
    # return only those serial numbers that match all filters
    return(events_table_filtered$Serial_Number)
  })
  
  events_filtered_except_wuc <- reactive({
    # events table with the SN and Location filters applied
    #  will be used to pull out WUC options
    if (is.null(events())) {
      return(NULL)
    }
    
    isolate({
      loc_selection_local <- values$loc_selection
      sn_selection_local  <- values$sn_selection
      label_selection_local <- values$label_selection
      depot_selection_local <- values$depot_selection
    })
    
    # start with all wucs
    events_table <- events()
    # filter by location
    if (!is.null(loc_selection_local) && !input$loc_agg && 
        which(values$selected_agg_order[1:factor_size] == "loc") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      events_filter_by_loc <- events_table[events_table[, loc_field_name_id()] %in% input$loc_selection, "id"]
    } else {
      events_filter_by_loc <- events_table$id
    }
    
    # filter by serial number
    if (!is.null(sn_selection_local) && !input$sn_agg && 
        which(values$selected_agg_order[1:factor_size] == "sn") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      events_filter_by_sn <- semi_join(events_table, data.frame(Serial_Number = values$sn_selection), by = "Serial_Number") %>% 
        select(id) %>% Df2Vr()
    } else {
      events_filter_by_sn <- events_table$id
    }
    # filter by label
    if (!is.null(label_selection_local) && !input$label_agg && 
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      events_filter_by_label <- semi_join(events_table, data.frame(Label = values$label_selection), by = "Label") %>% 
        select(id) %>% Df2Vr()
    } else {
      events_filter_by_label <- events_table$id
    }
    # filter by maintenance level
    if (!is.null(depot_selection_local) && !input$depot_agg && 
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      events_filter_by_depot <- semi_join(events_table, data.frame(Maintenance_Level = values$depot_selection), 
                                          by = "Maintenance_Level") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_depot <- events_table$id
    }
    
    matching_ids <- purrr::reduce(.x=list(events_filter_by_loc, events_filter_by_sn, 
                                          events_filter_by_label, events_filter_by_depot), .f=intersect)
    
    # return only those serial numbers that match all filters
    return(events_table %>% semi_join(data.frame(id = matching_ids), by = "id"))
  })
  
  # translate 5-digit WUC to user-specified WUC type (e.g. 4-digit) and 
  #  keep five-digit WUC for use in loc and sn filters and event filters
  #  one row for each 5-digit wuc
  wuc_map_selected_type <- reactive({
    # order matches by total actions within each WUC or WUC-group
    if(is.null(input$wuc_type)){
      return(NULL)
    }
    if(input$wuc_type == "five"){
      return(
        # count actions per wuc and add a field, reduced_wuc, to match the format of the rest of the returns in this reactive
        select(events_filtered_except_wuc(), Work_Unit_Code, WUC_Narrative) %>% group_by(Work_Unit_Code, WUC_Narrative) %>% 
          summarise(actions = n()) %>% ungroup() %>% arrange(desc(actions)) %>% mutate(reduced_wuc = Work_Unit_Code) %>% 
          distinct() %>% select(-actions)
        )
    }
    if(input$wuc_type == "four"){
        # set reduced WUC field to WUC Assembly 
        # size of event table
        # no known narrative for four-digit wuc so leave out
      wuc_map <- select(events_filtered_except_wuc(), Work_Unit_Code, WUC_Assy) %>% 
        rename(reduced_wuc = WUC_Assy)
      return(
        # return this map along with the count of actions of each reduced wuc, ordered by actions
        wuc_map %>% group_by(reduced_wuc) %>% summarise(actions = n()) %>%
          inner_join(wuc_map, by = "reduced_wuc") %>% arrange(desc(actions)) %>% distinct() %>% select(-actions)
      )
    }
    if(input$wuc_type == "three"){
      wuc_map <- select(events_filtered_except_wuc(), Work_Unit_Code, WUC_Subsys) %>% 
        rename(reduced_wuc = WUC_Subsys)
      return(
        # return this map along with the count of actions of each reduced wuc, ordered by actions
        wuc_map %>% group_by(reduced_wuc) %>% summarise(actions = n()) %>%
          inner_join(wuc_map, by = "reduced_wuc") %>% arrange(desc(actions)) %>% distinct() %>% select(-actions)
      )
    }
    if(input$wuc_type == "two"){
      wuc_map <- select(events_filtered_except_wuc(), Work_Unit_Code, WUC_Sys) %>% 
        rename(reduced_wuc = WUC_Sys)
      return(
        # return this map along with the count of actions of each reduced wuc, ordered by actions
        wuc_map %>% group_by(reduced_wuc) %>% summarise(actions = n()) %>%
          inner_join(wuc_map, by = "reduced_wuc") %>% arrange(desc(actions)) %>% distinct() %>% select(-actions)
      )
    }
    if(input$wuc_type == "gen_sup"){
      # match between WUC and reduced WUC; size of event table
      wuc_map <- select(events_filtered_except_wuc(), Work_Unit_Code, WUC_Gen_Sup) %>% 
        mutate(reduced_wuc = wuc_gen_sup_map[as.character(WUC_Gen_Sup)] %>% unlist())
      return(
        # return this map along with the count of actions of each reduced wuc, ordered by actions
        wuc_map %>% group_by(reduced_wuc) %>% summarise(actions = n()) %>%
          inner_join(wuc_map, by = "reduced_wuc") %>% arrange(desc(actions)) %>% distinct() %>% select(-actions)
      )
    }
    if(input$wuc_type == "user"){
      # use user defined wuc group
      wuc_map <- select(events_filtered_except_wuc(), Work_Unit_Code, WUC_User_Defined) %>% 
        rename(reduced_wuc = WUC_User_Defined)
      return(
        # return this map along with the count of actions of each reduced wuc, ordered by actions
        wuc_map %>% group_by(reduced_wuc) %>% summarise(actions = n()) %>%
          inner_join(wuc_map, by = "reduced_wuc") %>% arrange(desc(actions)) %>% distinct() %>% select(-actions)
      )
    }

  })
  
  # return user-specified WUC type (e.g. 4-digit) from wuc-map table above
  #  as well as the WUC name
  #  for use in Select WUC UI
  wuc_options_selected_type_as_list <- reactive({
    if(is.null(wuc_map_selected_type())){
      return(NULL)
    }
    if(!("WUC_Narrative" %in% names(wuc_map_selected_type()))) {
      # no matching narrative
      return(wuc_map_selected_type()$reduced_wuc %>% unique() %>% as.list())
    } else {
      to_return <- as.list(wuc_map_selected_type()$reduced_wuc)
      names(to_return) <- paste(wuc_map_selected_type()$reduced_wuc, wuc_map_selected_type()$WUC_Narrative, sep = " - ")
      return(to_return)
    }
    # shouldn't be here
    return(NULL)
  })

  ### Filter the events to hand off to plot
  
  events_filtered <- reactive({
    if(is.null(input$loc_agg) || is.null(input$sn_agg) || 
       is.null(input$wuc_agg) || is.null(events())){
      return(NULL)
    }
    ## TODO: if there's cases where the controls are still loading, then return NULL so filtering isn't required
    # e.g.:
    if(!input$wuc_agg && (is.null(input$wuc_selection) || input$wuc_selection == "") ||
       !input$loc_agg && (is.null(input$loc_selection) || input$loc_selection == "") ||
       !input$sn_agg && (is.null(input$sn_selection)  || input$sn_selection == "") || 
       !input$label_agg && (is.null(input$label_selection)  || input$label_selection == "") ||
       !input$depot_agg && (is.null(input$depot_selection)  || input$depot_selection == "")) {
      return(NULL)
    }
    
    # start with the full list
    events_to_return <- events()
    
    # if user wants to disaggregate factor
    if(!input$loc_agg){
      if(!is.null(input$loc_type) && !is.null(values$loc_selection)){
          events_to_return <- events_to_return[events_to_return[, loc_field_name_id()] %in% values$loc_selection, ]
      }
    }
    
    if(!input$sn_agg){
      events_to_return <- events_to_return[events_to_return$Serial_Number %in% values$sn_selection, ]
    }
    
    if(!input$wuc_agg){
      # no need to distinguish between what wuc type option is selected
      # match wuc selection to 5-digit wuc
      five_digit_wuc_selection <- wuc_map_selected_type() %>% 
        semi_join(data.frame(reduced_wuc = unlist(values$wuc_selection)), by = "reduced_wuc")
      # filter events based on selection and add reduced_wuc field for later filtering
      #  join on WUC_Narrative if it's there
      join_fields <- "Work_Unit_Code"
      if("WUC_Narrative" %in% names(five_digit_wuc_selection)){
        join_fields <- c(join_fields, "WUC_Narrative")
      }
      events_to_return <- inner_join(events_to_return, five_digit_wuc_selection, by = join_fields)
      # use a semi_join instead of inner_join to plots all the matching 5-digit wucs instead of 4 or whichever user selects
    }
    
    if(!input$label_agg){
      events_to_return <- events_to_return %>% 
        semi_join(data.frame(Label = values$label_selection), by = "Label")
    }
    
    if(!input$depot_agg){
      events_to_return <- events_to_return %>% 
        semi_join(data.frame(Maintenance_Level = input$depot_selection), by = "Maintenance_Level")
    }
    events_to_return$Transaction_Date_Adj <- events_to_return$Transaction_Date
    # move next to transaction_date
    events_to_return <- events_to_return[, c(1:which(names(events_to_return)=="Transaction_Date"),ncol(events_to_return),
                                             (1+which(names(events_to_return)=="Transaction_Date")):(ncol(events_to_return)-1))]

    return(events_to_return)
  })
  
  # Event Label Filter #
  label_options <- reactive({
    if(is.null(input$label_agg) || is.null(events())){
      return(NULL)
    }
    
    events_table <- events()
    
    # control updates to label options with isolate:
    isolate({
      loc_selection_local <- values$loc_selection
      sn_selection_local  <- values$sn_selection
      wuc_selection_local <- values$wuc_selection
      depot_selection_local <- values$depot_selection
    })
    
    # filter by location IF some specific locations are chosen 
    #  and location was disaggregated before label (loc has priority cascade filtering)
    if (!is.null(loc_selection_local) && !(loc_selection_local=="") && !input$loc_agg && 
        which(values$selected_agg_order[1:factor_size] == "loc") < which(values$selected_agg_order[1:factor_size] == "label")) {
      events_filter_by_loc <- events_table[events_table[, loc_field_name_id()] %in% values$loc_selection, "id"]
    } else {
      events_filter_by_loc <- events_table$id
    }
    
    # filter by sn
    if (!is.null(sn_selection_local) && !(sn_selection_local=="") && !input$sn_agg && 
        which(values$selected_agg_order[1:factor_size] == "sn") < which(values$selected_agg_order[1:factor_size] == "label")) {
      events_filter_by_sn <- semi_join(events_table, data.frame(Serial_Number = values$sn_selection), 
                                       by = "Serial_Number") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_sn <- events_table$id
    }
    
    # filter by wuc
    if (!is.null(wuc_selection_local) && !(wuc_selection_local=="") && !input$wuc_agg && 
        which(values$selected_agg_order[1:factor_size] == "wuc") < which(values$selected_agg_order[1:factor_size] == "label")) {
      events_table <- inner_join(events_table, select(wuc_map_selected_type(), Work_Unit_Code, reduced_wuc), by = "Work_Unit_Code")
      events_filter_by_wuc <- semi_join(events_table, data.frame(reduced_wuc = values$wuc_selection), 
                                        by = "reduced_wuc") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_wuc <- events_table$id
    }
    
    # filter by maintenance level
    if (!is.null(depot_selection_local) && !(depot_selection_local=="") && !input$depot_agg && 
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "label")) {
      events_filter_by_depot <- semi_join(events_table, data.frame(Maintenance_Level = values$depot_selection), 
                                          by = "Maintenance_Level") %>% select(id) %>% Df2Vr()
    } else {
      events_filter_by_depot <- events_table$id
    }
    
    matching_ids <- purrr::reduce(.x=list(events_filter_by_loc, events_filter_by_wuc, 
                                          events_filter_by_sn, events_filter_by_depot), .f=intersect)
    # order matches by total actions then drop actions
    events_table_filtered <- select(events_table, id, Label) %>% 
      semi_join(data.frame(id = matching_ids), by = "id") %>%
      group_by(Label) %>% summarise(actions = n()) %>% arrange(desc(actions)) %>% select(-actions)
    ## TODO: to speed up code - keep this action count around and use it for the pareto, which now re-calculates actions
    
    # return only those serial numbers that match all filters
    return(events_table_filtered$Label)
    
  })
  
  ###               ###
  ### End Filtering ###
  ###               ###
  
  intermediate_plot_calculation <- reactive({
    input$plot_type;input$pareto_labels;input$sort_by_severity # dependence
    input$loc_agg;input$sn_agg;input$wuc_agg;input$label_agg;input$depot_agg # dependence
    input$loc_type;input$wuc_type; # even if same data, still show different things
    input$normalize_option
    if(input$plot_type != "Pareto" || 
       input$plot_type == "Pareto" && values$normalize_option == "Time Period & Assigned Aircraft"){
     input$time_dependent_group_selection  # conditional dependence
    }
    
    # if data isn't loaded ...
    if(is.null(values$events_filtered_adj) || nrow(values$events_filtered_adj)==0 || 
       isolate(is.null(events_filtered())) || isolate(is.null(values$events_filtered)) ||
       # or if controls are not all loaded then return null
       (input$names_not_codes && is.null(input$which_labels))){
      return(NULL)
    }
    
    isolate({
    ## FAIL EARLY
    # if depot cycle data isn't specified or they're all NA display a warning but don't break
    shiny::validate(
      need(try(
        if(!is.null(values$normalize_option) && values$normalize_option == "Depot Cycles")
        (if(is.null(sn_depot_cycles()) || sum(!is.na(sn_depot_cycles()$SN_Depot_Cycles)) == 0) FALSE else TRUE) else TRUE),
        "No Depot Cycle Data Defined")
    )
    shiny::validate(
      need(try( # same for flying hours
        if(!is.null(values$normalize_option) && values$normalize_option == "Flying Hours")
          (if(is.null(sn_loc_flying_hours()) || sum(!is.na(sn_loc_flying_hours()$Fly_Hours_SN_Loc)) == 0) FALSE else TRUE) else TRUE),
        "No Flying Hours Data Defined")
    )
    
    # Plot Something
    # copy data
    grouped_events <- values$events_filtered_adj # times adjusted for grouping (e.g. monthly)
    
    # Prevent an error when date is all NAs or some zero
    if(nrow(grouped_events) > 0 && (sum(!is.na(grouped_events$Transaction_Date_Adj)) == 0 || 
       min(year(grouped_events$Transaction_Date_Adj), na.rm = TRUE) < 1900)){
      stop("Some Dates are Before 1900 - Cannot Plot")
    }
    
    # if no factors selected then use default clockwork blue
    if(!any(!input$loc_agg, !input$sn_agg, !input$wuc_agg, !input$label_agg, !input$depot_agg)){
      if(input$plot_type == "Time Dependent"){
        
        # group data and sum actions
        grouped_events <- grouped_events %>% group_by(Transaction_Date_Adj) %>% summarise(actions = n())
        # complete data - fill in zeros for all days with no actions
        all_dates <- data.frame("Transaction_Date_Adj" = seq(min(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                         max(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                         by=paste0(tolower(input$time_dependent_group_selection), 's')))
        grouped_events <- right_join(grouped_events, all_dates, by = "Transaction_Date_Adj")
        if (sum(is.na(grouped_events$actions)) > 0) {
          # set NAs to zero
          grouped_events[is.na(grouped_events$actions), ]$actions <- 0
        }
        
        # Set y-axis Label
        y_label <- paste0("Events Per ", input$time_dependent_group_selection, "\n")
        # return a plot
        return(ggplot(grouped_events, aes(x = Transaction_Date_Adj, y = actions)) + geom_line(colour = "#0799B9") + theme_bw() + 
                 labs(x = "Date\n", y = y_label) + theme(axis.text = element_text(size = rel(axis_text_rel_size)), 
                                                         axis.title = element_text(size = rel(axis_title_rel_size))) + 
                 ylim(0, NA))
      } else if(input$plot_type == "Pareto") { # Pareto
        # plot a single group of sum of all actions
        # Normalize if Selected 
        if(!is.null(values$normalize_option) && values$normalize_option != "None"){
          if(values$normalize_option == "Time Period & Assigned Aircraft"){
            # Divide each SN by its active days, sum this total, then divide by total Aircraft ever assigned
            #  (sort of an average, but denominator may be larger than # of aicraft with a corrosion maintenance event)
            plot_df <- AggregateForParetoNormalization(selected_factors = NULL, grouped_events = grouped_events,
                                                       normalize_option = "Asgn_Days", sn_loc_active_days = sn_loc_active_days,
                                                       sn_loc_flying_hours = sn_loc_flying_hours, sn_depot_cycles = sn_depot_cycles)
            # SN with "None" or no assigned location sometimes show up.  exclude these actions
            #   and exclude them from denominator
            plot_df <- data.frame("yy" = sum(plot_df$actions) / values$events_filtered_adj[1, "Aircraft_Any_Asgn_Tot"])
            # multiply by Days per Time Period
            plot_df$yy <- plot_df$yy * days_per_time[[input$time_dependent_group_selection]] # retrieve from list
            # Set y-axis Label
            y_label <- paste0("Events Per Aircraft Per ", input$time_dependent_group_selection, "\n")
            round_num <- 1
          } else if(values$normalize_option == "Flying Hours") { 
            # Flying Hours
            # Divide each SN by its total flight hours and take average as above with aircraft
            plot_df <- AggregateForParetoNormalization(selected_factors = NULL, grouped_events = grouped_events,
                                                       normalize_option = "Flying_Hours", sn_loc_active_days = sn_loc_active_days,
                                                       sn_loc_flying_hours = sn_loc_flying_hours, sn_depot_cycles = sn_depot_cycles)
            plot_df <- data.frame("yy" = sum(plot_df$actions, na.rm = TRUE) / values$events_filtered_adj[1, "Aircraft_Any_Asgn_Tot"])
            # Set y-axis Label
            y_label <- paste0("Events Per Flying Hour\n")
            round_num <- 4
          } else if (values$normalize_option == "Depot Cycles"){
            # Divide each SN by its total flight hours and take average as above with aircraft
            plot_df <- values$events_filtered_adj %>% group_by(Serial_Number) %>% summarise(actions = n()) %>%
              inner_join(
                select(sn_depot_cycles(), Serial_Number, SN_Depot_Cycles) %>% distinct()
                , by = "Serial_Number") %>% filter(!is.na(SN_Depot_Cycles)) %>% mutate(actions = actions/SN_Depot_Cycles)
            plot_df <- data.frame("yy" = sum(plot_df$actions, na.rm = TRUE) / values$events_filtered_adj[1, "Aircraft_Any_Asgn_Tot"])
            # Set y-axis Label
            y_label <- paste0("Events Per Depot Cycle (min. 1 per aircraft)\n")
            round_num <- 2
          } else {
            stop("unknown normalization option")
          }
        } else {
          # No Normalization - just count number of events
          plot_df <- data.frame("yy" = nrow(values$events_filtered_adj))
          y_label <- "Events"
          round_num <- 1
        }
        
        return(ggplot(plot_df, aes(x = 1, y = yy, fill = "All Data")) + geom_bar(stat = "identity") + 
                 labs(x = "All Data", y = y_label) + scale_fill_manual(values = "#0799B9") + 
                 theme_bw() + theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(),
                                    axis.text.x = element_blank(), axis.ticks.x = element_blank(), 
                                    legend.position = "none", 
                                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                                    axis.title = element_text(size = rel(axis_title_rel_size))) +
                 if(input$pareto_labels){
                   geom_text(aes(label = round(yy, round_num)), vjust = annot_pos_below, size = rel(pareto_label_rel_size)) # place labels above top of bar
                 } else {
                   NULL # otherwise no labels
                   })
      } else { # input$plot_type == Time between Event
        # single plot of average time between any event for all serial numbers
        #  average across serial numbers: (days assigned anywhere)/(sum of days-with-some-event)
        #  exclude SNs with no assignment info and thus NA Days_SN_Asgn_Tot 
        #    (exclude events and do not include in denominator for average across SNs)
        #  exclude events without a serial number
        plot_df <- values$events_filtered_adj %>% filter(Serial_Number != "None", !is.na(Days_SN_Asgn_Tot)) %>%
          group_by(Serial_Number, Transaction_Date, Days_SN_Asgn_Tot) %>%
          distinct() %>% ungroup() %>% group_by(Serial_Number, Days_SN_Asgn_Tot) %>% 
          summarise(actions = n()) %>% mutate(dbe = Days_SN_Asgn_Tot/actions)
        # calculate average across serial numbers and adjust for time period
        plot_df <- data.frame("yy" = mean(plot_df$dbe) * (1/days_per_time[[input$time_dependent_group_selection]]))
        
        y_label <- paste0(input$time_dependent_group_selection, "s Between Events for Average Aircraft")
        round_num <- FindDigitsToRound(plot_df$yy)
        return(ggplot(plot_df, aes(x = 1, y = yy, fill = "All Data")) + geom_bar(stat = "identity") + 
                 labs(x = "All Data", y = y_label) + 
                 scale_fill_manual(values = "#0799B9") + 
                 theme_bw() + theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(),
                                    axis.text.x = element_blank(), axis.ticks.x = element_blank(), 
                                    legend.position = "none", 
                                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                                    axis.title = element_text(size = rel(axis_title_rel_size))) +
                 if(input$pareto_labels){
                   geom_text(aes(label = round(yy, round_num)), vjust = annot_pos_below, size = rel(pareto_label_rel_size)) # place labels above top of bar
                 } else {
                   NULL # otherwise no labels
                 })
      }
    }
    # ONE FACTOR DISAGGREGATED -------------------------------------------------
    # if only one factor is disaggregated then don't bother creating a new factor 
    if(sum(!input$loc_agg, !input$sn_agg, !input$wuc_agg, !input$label_agg, !input$depot_agg) == 1){
      possible_factors <- c("Location", "Serial_Number", "Work_Unit_Code", "Label", "Maintenance_Level")
      single_factor <- possible_factors[which(c(!input$loc_agg, !input$sn_agg, !input$wuc_agg, 
                                                !input$label_agg, !input$depot_agg))]
      
      # if selected, be more specific about location
      single_factor <- SelectProperLocationName(single_factor, input$loc_type, values$loc_selection, loc_field_name_id())
      if(is.null(single_factor)){
        # controls are still loading
        return(NULL)
      }
  
      #   if user wants to show WUC Narrative instead of WUC then use nomenclature (or location name instead of code)
      #    (must be 5-digit wuc. no narrative for other types of WUC)
      #  Work Unit Code is the name of the legend and pareto x axis (or x_Location)
      single_factor_legend_name <- single_factor
      single_factor <- AdjustAFactorForParameters(single_factor, input$names_not_codes, input$which_labels, input$wuc_type, input$loc_agg)
      
      if(input$plot_type == "Time Dependent"){ # one factor disaggregated
        
        # if selected, attach the total number of aircraft per group per day/wk/mo/qtr/yr to normalize actions
        if(!is.null(values$normalize_option) && values$normalize_option != "None"){
          updateRadioButtons(session, inputId = "normalize_option", selected = "None")
          return(NULL) # Trying to Normalize Time Dependent
          # shouldn't be here b/c not normalizing time dependent
          
        } else { #  not normalizing 
          
          y_label <- paste0("Events Per ", input$time_dependent_group_selection,"\n")
          
          # group by date and this single factor and count actions
          grouped_events <- grouped_events %>% group_by_("Transaction_Date_Adj", single_factor) %>% 
            summarise(actions = n())
          
          # can't plot more than n (16ish) lines b/c colour palette isn't large enough
          shiny::validate(
            need(try(length(unique(grouped_events[[single_factor]])) <= max_colors), em_too_few_colors_defined)
          )
          
          # complete data by filling in zeros for in-between dates
          all_vals <- expand.grid("Transaction_Date_Adj" = seq(min(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                           max(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                           by=paste0(tolower(input$time_dependent_group_selection), 's')), 
                                  single_factor = unname(unlist(unique(grouped_events[, single_factor]))), 
                                  stringsAsFactors = FALSE)
          names(all_vals)[2] <- single_factor
          grouped_events <- right_join(grouped_events, all_vals, by = c("Transaction_Date_Adj", single_factor))
          if (sum(is.na(grouped_events$actions)) > 0 ) {
            grouped_events[is.na(grouped_events$actions), ]$actions <- 0 # replace missing values with zero
          }
          
        }
        # time-dependent plot will not work if there's only one data date.  instead, use a jittered dot plot 
        #    ( could also use a dodged bar plot )
        if(length(unique(grouped_events$Transaction_Date_Adj))==1){
          
          # set this up before the call to plot b/c otherwise the transaction date will pass through as literaly "Transaction_Date_Adj"
          grouped_events$x_field <- paste0(input$time_dependent_group_selection,": ", grouped_events$Transaction_Date_Adj)
          
          # must use aes_q b/c grouping factor is in a variable (http://docs.ggplot2.org/current/aes_.html)
          return(ggplot(grouped_events, aes_q(x = quote(x_field), y = quote(actions), colour = as.name(single_factor))) +
                   geom_jitter(width = 0.15, cex = 5) + # rather than geom_bar(stat = "identity", position = "dodge")
                   guides(colour = guide_legend(title = MakeTitleCase(single_factor_legend_name))) + theme_bw() +  
                   theme(legend.position = "bottom", # legend needs work
                         legend.key = element_rect(colour = "white"),
                         legend.text = element_text(size = rel(legend_text_rel_size)),
                         legend.title = element_text(size = rel(legend_title_rel_size)),
                         axis.text = element_text(size = rel(axis_text_rel_size)), 
                         axis.title = element_text(size = rel(axis_title_rel_size)))  + 
                   labs(x = "Date\n", y = y_label) + scale_colour_manual(values = chosen_color_manual_palette) +#scale_colour_brewer(palette = chosen_color_brewer_palette) + 
                   ylim(0, NA) # set y min to zero
          )
        } else {
          return(
            ggplot(grouped_events, aes_q(x = quote(Transaction_Date_Adj), y = quote(actions), 
                                         colour = as.name(single_factor))) + 
              geom_line() + guides(colour = guide_legend(title = MakeTitleCase(single_factor_legend_name))) + theme_bw() + 
              theme(legend.position = "bottom", # legend needs work
                    legend.key = element_rect(colour = "white"),
                    legend.text = element_text(size = rel(legend_text_rel_size)),
                    legend.title = element_text(size = rel(legend_title_rel_size)),
                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                    axis.title = element_text(size = rel(axis_title_rel_size)))  + 
              labs(x = "Date\n", y = y_label) + ylim(0, NA) + scale_colour_manual(values = chosen_color_manual_palette)
              #scale_colour_brewer(palette = chosen_color_brewer_palette)
          )
        }
      }
      
      else if (input$plot_type == "Pareto") { # pareto - one factor disagreggated
        # if selected, normalize by Assigned Aircraft or Flying Hours
        if(!is.null(values$normalize_option) && values$normalize_option != "None"){
          # if location is selected, normalize by days at location.  otherwise, normalize by total days
          # normalization is not possible when looking at Performing Maintenance locations
          if(values$normalize_option == "Flying Hours"){
            round_num <- 4
          } else {
            round_num <- 2 # Years & Depot Cycles
          }
          # if location or location_name then normalize by location
          if(grepl(pattern = "Assigned_Location", x = single_factor)){
            if(values$normalize_option == "Time Period & Assigned Aircraft"){
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Asgn_Days", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              # Adjust for time period
              grouped_events$actions <- grouped_events$actions * days_per_time[[input$time_dependent_group_selection]]
              y_label <- paste0("Events Per Aircraft Per ", input$time_dependent_group_selection, "\n")
            } else if (values$normalize_option == "Flying Hours"){ 
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Flying_Hours", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              y_label <- "Events Per Flying Hour\n"
            } else if (values$normalize_option == "Depot Cycles") {
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Depot_Cycles", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              y_label <- "Events Per Depot Cycle (min. 1 per aircraft)\n"
            } else {
              stop("unknown normalization")
            }
            # when location is disaggregated: sum actions within location and divide by number of aircraft assigned at that location
            aircraft_at_location <- values$events_filtered_adj %>% select_(single_factor, "Aircraft_Any_Asgn_Loc") %>% distinct()
            grouped_events <- grouped_events %>% ungroup() %>% group_by_(single_factor) %>% summarise(actions = sum(actions)) %>%
              inner_join(
                aircraft_at_location, by = single_factor
              ) %>% mutate(actions = actions/Aircraft_Any_Asgn_Loc)
            
          } else if(single_factor == "Serial_Number") {
            if(values$normalize_option == "Time Period & Assigned Aircraft"){
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Asgn_Days", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              # Adjust for time period
              grouped_events$actions <- grouped_events$actions * days_per_time[[input$time_dependent_group_selection]]
              y_label <- paste0("Events Per ", input$time_dependent_group_selection, "\n")
            } else if (values$normalize_option == "Flying Hours"){ 
            # Flight Hours
            grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                              grouped_events, "Flying_Hours", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
            y_label <- "Events Per Flying Hour\n"
            } else if(values$normalize_option == "Depot Cycles"){
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Depot_Cycles", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              y_label <- "Events Per Depot Cycle (min. 1 per aircraft)\n"
            } else {
            stop("unkown normalization")
          }
          } else {
            # single_factor is WUC or Event Label or Maintenance Level. group by serial number and this factor
            if(values$normalize_option == "Time Period & Assigned Aircraft"){
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Depot_Cycles", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              # Adjust for time period
              grouped_events$actions <- grouped_events$actions * days_per_time[[input$time_dependent_group_selection]]
              y_label <- paste0("Events Per Aircraft Per ", input$time_dependent_group_selection, "\n")
            } else if (values$normalize_option == "Flying Hours") {
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Flying_Hours", sn_loc_active_days, sn_loc_flying_hours)
              y_label <- "Events Per Flying Hour\n"
            } else if (values$normalize_option == "Depot Cycles"){
              grouped_events <- AggregateForParetoNormalization(selected_factors = single_factor, 
                                                                grouped_events, "Depot_Cycles", sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
              y_label <- "Events Per Depot Cycle (min. 1 per aircraft)\n"
            } else {
              stop("unknown normalization")
            }
            
            # then get "average" - sum of actions per WUC or event-type divided by total number of aircraft
            aircraft_total <- values$events_filtered_adj[1, "Aircraft_Any_Asgn_Tot"]
            grouped_events <- grouped_events %>% ungroup() %>% group_by_(single_factor) %>% summarise(actions = sum(actions)/aircraft_total)
          }
          
          
        } else {
          # No Normalization
          # group by single group factor but not time
          grouped_events <- grouped_events %>% group_by_(single_factor) %>% summarise(actions = n())
          y_label <- "Events\n"
          round_num <- 1
        }
        
        # order for pareto
        # if ordering by Location Severity then sort by Location severity then count
        if(input$sort_by_severity && grepl("Location", single_factor)){
          # attach severity index to filtered and aggregated data set
          grouped_events <- grouped_events %>% inner_join(
            values$events_filtered_adj %>% select_(single_factor, 
                                               paste0(single_factor_legend_name,"_Severity_Label"),
                                               paste0(single_factor_legend_name,"_Severity_Index")) %>% distinct(),
                                               by = single_factor) %>%
          # rename fields to make predictable
            rename_("Severity_Label" = paste0(single_factor_legend_name,"_Severity_Label"), 
                    "Severity_Index" = paste0(single_factor_legend_name,"_Severity_Index"))
          # find order
          factor_order <- (grouped_events[, single_factor] %>% unlist() %>% unname())[ # complex way to get a ordered vector
            order(grouped_events$Severity_Index, -grouped_events$actions)]
          grouped_events[, single_factor] <- factor(unname(unlist(grouped_events[, single_factor])), levels = factor_order)
          # find placement of labels and lines
          severity_labels <- grouped_events %>% group_by(Severity_Label, Severity_Index) %>% summarise(ct = n())
          severity_labels <- severity_labels[order(severity_labels$Severity_Index), ] # arrange isn't working
          severity_labels$ctcum = cumsum(severity_labels$ct)
          if(nrow(severity_labels)>1){
            # more than one type of location severity
            vlines <- severity_labels$ctcum[1:(nrow(severity_labels)-1)] + 0.5
            severity_labels$pos <- c(vlines - 0.5, max(severity_labels$ctcum))  
          } else {
            # only one type of location severity - plot name but not line
            vlines <- NA
            severity_labels$pos <- max(severity_labels$ctcum)
          }
          
        } else {
        # otherwise sort just by count
          factor_order <- unname(unlist(grouped_events[order(
            grouped_events$actions, decreasing = TRUE), 1])) # gets single factor
          grouped_events[, 1] <- factor(unname(unlist(grouped_events[, 1])), levels = factor_order)
        }
        
        # normalizing by assigned location when no assigned locations are defined gives an empty data frame
        #   don't try to plot this 
        shiny::validate(
          need(try(nrow(grouped_events)>0), "Configuration results in no data.")
        )
        # make plot
        to_return <- ggplot(grouped_events, aes_q(x = as.name(single_factor), 
                                     y = quote(actions), fill = "All Data")) + 
          geom_bar(stat = "identity") + labs(x = MakeTitleCase(single_factor_legend_name), y = y_label) + 
          scale_fill_manual(values = "#0799B9") + theme_bw() + 
          theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), 
                axis.ticks.x = element_blank(), legend.position = "none", 
                axis.text = element_text(size = rel(axis_text_rel_size)), 
                axis.title = element_text(size = rel(axis_title_rel_size)))
        # Add pareto labels
        if(input$pareto_labels){
          to_return <- to_return + geom_text(aes(label = round(actions, round_num), 
                                                 vjust = annot_pos_below), 
                                             size = rel(pareto_label_rel_size)) # place labels above top of bar
        }
        # Add lines and severity labels
        if(input$sort_by_severity && grepl("Location", single_factor)){
            to_return <- to_return + geom_text(data = severity_labels, 
                                               aes(label = Severity_Label, x = pos, 
                                                   y = max(grouped_events$actions)*1.08), 
                                               size = rel(pareto_label_rel_size)) + geom_vline(xintercept = vlines)
        }
      
      return(to_return)
        # end Pareto for one factor
      } else { # Time between event for 1 factor
        # if user disaggregates on SN: group by SN and plot dots
        # if user disaggregates on something beside SN: group by SN & that factor, 
        #   careful to use the correct Assigned Days Value
        if(single_factor == "Serial_Number"){
          # calculate days between events
          grouped_events <- grouped_events %>% filter(Serial_Number != "None", !is.na(Days_SN_Asgn_Tot)) %>%
            group_by(Serial_Number, Transaction_Date, Days_SN_Asgn_Tot) %>%
            distinct() %>% ungroup() %>% group_by(Serial_Number, Days_SN_Asgn_Tot) %>% 
            summarise(actions = n()) %>% mutate(dbe = Days_SN_Asgn_Tot/actions)
          # sort by fewest days first (most events per day)
          factor_order <- unname(unlist(grouped_events[order(
            grouped_events$dbe, decreasing = FALSE), 1])) # gets single factor
          grouped_events[, 1] <- factor(unname(unlist(grouped_events[, 1])), levels = factor_order)
          
          y_label <- "Days Between Events"
          round_num <- FindDigitsToRound(min(grouped_events$dbe))
      
        } else { # single factor is not serial number
          # if single factor is assigned location (code or name) then divide days at location by actions at location
          #  else divide days total over actions total. use total days for performing location
          days_division_variable <- "Days_SN_Asgn_Tot"
          if(grepl(pattern = "Assigned_Location", x = single_factor)){
            days_division_variable <- "Days_SN_Asgn_Loc"
          }
          
          # calculate days between events
          grouped_events <- grouped_events %>% filter(Serial_Number != "None") %>%
            # filter out records with no serial number and serial numbers with no assigned days
            filter_(paste0("!is.na(",days_division_variable,")")) %>%
            # unique days
            group_by_(single_factor, "Serial_Number", "Transaction_Date", days_division_variable) %>%
            # unique factors including SN - count event-days and calculate dbe
            distinct() %>% ungroup() %>% group_by_(single_factor, "Serial_Number", days_division_variable) %>% 
            summarise(actions = n()) %>% mutate_(dbe = paste0(days_division_variable,"/actions")) %>%
            # unique factors excluding SN - average dbe across SNs
            ungroup() %>% group_by_(single_factor) %>% summarise(dbe = mean(dbe)) %>% 
            # adjust for time period
            mutate(dbe = dbe/days_per_time[[input$time_dependent_group_selection]])
          
          y_label <- paste0(input$time_dependent_group_selection, "s Between Events for Average Aircraft")
          round_num <- FindDigitsToRound(min(grouped_events$dbe))
          
          # sort by fewest days first (most events per day)
          # UNLESS user wants to sort by location severity
          if(grepl(pattern = "Location", x = single_factor) && input$sort_by_severity){
            # attach severity index to filtered and aggregated data set
            grouped_events <- grouped_events %>% inner_join(
              values$events_filtered_adj %>% select_(single_factor, 
                                                     paste0(single_factor_legend_name,"_Severity_Label"),
                                                     paste0(single_factor_legend_name,"_Severity_Index")) %>% distinct(),
              by = single_factor) %>%
              # rename fields to make predictable
              rename_("Severity_Label" = paste0(single_factor_legend_name,"_Severity_Label"), 
                      "Severity_Index" = paste0(single_factor_legend_name,"_Severity_Index"))
            # find order
            factor_order <- (grouped_events[, single_factor] %>% unlist() %>% unname())[ # complex way to get a ordered vector
              order(grouped_events$Severity_Index, grouped_events$dbe)]
            grouped_events[, single_factor] <- factor(unname(unlist(grouped_events[, single_factor])), 
                                                      levels = factor_order)
            # find placement of labels and lines
            severity_labels <- grouped_events %>% group_by(Severity_Label, Severity_Index) %>% summarise(ct = n())
            severity_labels <- severity_labels[order(severity_labels$Severity_Index), ] # arrange isn't working
            severity_labels$ctcum = cumsum(severity_labels$ct)
            if(nrow(severity_labels) > 1){
              # more than one type of location severity
              vlines <- severity_labels$ctcum[1:(nrow(severity_labels) - 1)] + 0.5
              severity_labels$pos <- c(vlines - 0.5, max(severity_labels$ctcum))  
            } else {
              # only one type of location severity - plot name but not line
              vlines <- NA
              severity_labels$pos <- max(severity_labels$ctcum)
            }
          } else {
            # otherwise just sort by dbe
            factor_order <- unname(unlist(grouped_events[order(
              grouped_events$dbe, decreasing = FALSE), 1])) # gets single factor
            grouped_events[, 1] <- factor(unname(unlist(grouped_events[, 1])), levels = factor_order)
          }
          
        }
        
        # regardless of which single factor for Time Between Event, return a plot
        to_return <- ggplot(grouped_events, aes_string(x = single_factor, y = "dbe")) + 
                 geom_point(stat = "identity", size = 3, colour = "#0799B9") + 
                 labs(x = MakeTitleCase(single_factor_legend_name), y = y_label) + ylim(c(0,NA)) +
                 theme_bw() + theme(panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(),
                                    legend.position = "none", 
                                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                                    axis.title = element_text(size = rel(axis_title_rel_size)))
        # Add pareto labels
        if(input$pareto_labels){
          to_return <- to_return + geom_text(aes(label = round(dbe, round_num), 
                                                 vjust = annot_pos_below_dot), 
                                             size = rel(pareto_label_rel_size)) # place labels above top of dot
        }
        # Add lines and severity labels
        if(input$sort_by_severity && grepl("Location", single_factor)){
          to_return <- to_return + geom_text(data = severity_labels, 
                                             aes(label = Severity_Label, x = pos, 
                                                 y = max(grouped_events$dbe)*1.08), 
                                             size = rel(pareto_label_rel_size)) + geom_vline(xintercept = vlines)
        }
      return(to_return) # ggplot object
      } # end Time b/w Event for 1 factor
      
    } else {
      # if more than one factor selected, then create a new factor out of all the possible combinations of factors the user selects (loc, sn, etc.)
      # this new factor will be the graph's color (first adjust some of them to match with column names)
      possible_factors <- c("Location", "Serial_Number", "Work_Unit_Code", "Label", "Maintenance_Level") # Event Label
      selected_factors <- possible_factors[which(c(!input$loc_agg, !input$sn_agg, !input$wuc_agg, 
                                                   !input$label_agg, !input$depot_agg))]
      
      for (ii in seq_along(selected_factors)){
        # if selected, be more specific about location
        selected_factor <- SelectProperLocationName(selected_factors[ii], input$loc_type, values$loc_selection, loc_field_name_id())
        if(is.null(selected_factor)){
          # controls are still loading
          return(NULL)
        } else {
          selected_factors[ii] <- selected_factor
        }
      }
      
      # Save factor names for display in Legend
      single_factor_name <- paste(selected_factors, collapse = "\n")
      
      # Change factor names for proper label: code or label
      for (ii in seq_along(selected_factors)){
        # Adjust a factor based on user parameters (labels instead of codes, wuc_type instead of wuc)
        selected_factors[ii] <- AdjustAFactorForParameters(selected_factors[ii], input$names_not_codes, input$which_labels, input$wuc_type, input$loc_agg)
      }
      
      
      if(input$plot_type == "Time Dependent"){ # multiple factors selected
        
        # save the factor name (concat of all factor names) for plotting
        grouped_events[["single_factor"]] <- do.call(what = paste, 
                                                     args = c(grouped_events %>% select_(.dots = selected_factors), sep=" - "))
        # attach field name to selected_factors vector so it stays around after summarising
        selected_factors <- c(selected_factors, "single_factor")
        
        #  not normalizing by assigned aircraft qty
        y_label <- paste0("Events Per ",input$time_dependent_group_selection,"\n")
        
        # group by date and this single factor and count actions
        grouped_events <- grouped_events %>% group_by_("Transaction_Date_Adj", .dots = selected_factors) %>% 
          summarise(actions = n())
        
        # can't plot more than n (16ish) line colors b/c colour palette isn't large enough
        shiny::validate(
          need(try(length(unique(grouped_events[["single_factor"]])) <= max_colors), em_too_few_colors_defined)
        )
        
        # complete data by filling in zeros for in-between dates
        all_vals <- expand.grid("Transaction_Date_Adj" = seq(min(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                         max(grouped_events$Transaction_Date_Adj, na.rm = TRUE), 
                                                         by=paste0(tolower(input$time_dependent_group_selection), 's')), 
                                single_factor = unname(unlist(unique(grouped_events[, "single_factor"]))), 
                                stringsAsFactors = FALSE)
        names(all_vals)[2] <- "single_factor"
        grouped_events <- right_join(grouped_events, all_vals, by = c("Transaction_Date_Adj", "single_factor"))
        if (sum(is.na(grouped_events$actions)) > 0 ) {
          grouped_events[is.na(grouped_events$actions), ]$actions <- 0 # replace missing values with zero
        }
          
        # time-dependent plot will not work if there's only one data date.  instead, use a jittered dot plot 
        #    ( could also use a dodged bar plot )
        
        if(length(unique(grouped_events$Transaction_Date_Adj))==1){
          
          # set this up before the call to plot b/c otherwise the transaction date will pass through as literaly "Transaction_Date_Adj"
          grouped_events$x_field <- paste0(input$time_dependent_group_selection,": ", grouped_events$Transaction_Date_Adj)
        
          return(ggplot(grouped_events, aes(x = x_field, y = actions, colour = single_factor)) +
                   geom_jitter(width = 0.15, cex = 5) + # rather than geom_bar(stat = "identity", position = "dodge")
                   guides(colour = guide_legend(title = MakeTitleCase(single_factor_name))) + theme_bw() +  
                   theme(legend.position = "bottom", # legend needs work
                         legend.key = element_rect(colour = "white"),
                         legend.text = element_text(size = rel(legend_text_rel_size)),
                         legend.title = element_text(size = rel(legend_title_rel_size)),
                         axis.text = element_text(size = rel(axis_text_rel_size)), 
                         axis.title = element_text(size = rel(axis_title_rel_size)))  + 
                   guides(colour = guide_legend(title = MakeTitleCase(single_factor_name))) +
                   labs(x = "Date\n", y = y_label) + scale_colour_manual(values = chosen_color_manual_palette) + #scale_colour_brewer(palette = chosen_color_brewer_palette) + 
                   ylim(0, NA) # set y min to zero
          )
        } else {
          return(
            ggplot(grouped_events, aes(x = Transaction_Date_Adj, y = actions, 
                                         colour = single_factor)) + 
              geom_line() + guides(colour = guide_legend(title = MakeTitleCase(single_factor_name))) + theme_bw() + 
              theme(legend.position = "bottom", # legend needs work
                    legend.key = element_rect(colour = "white"),
                    legend.text = element_text(size = rel(legend_text_rel_size)),
                    legend.title = element_text(size = rel(legend_title_rel_size)),
                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                    axis.title = element_text(size = rel(axis_title_rel_size)))  + 
              labs(x = "Date\n", y = y_label) + ylim(0, NA) + scale_colour_manual(values = chosen_color_manual_palette)
              #scale_colour_brewer(palette = chosen_color_brewer_palette)
          )
        }
      }
      else if(input$plot_type == "Pareto") { # Pareto - multiple factors selected
        # Must treat Event Labels and Maintenance Level differently 
        #  between time-dependent and pareto: pareto will be stacked bar
        split_label_into_fill <- FALSE
        if("Label" %in% selected_factors){
          # remove label from selected factors and use for fill on the pareto
          selected_factors <- selected_factors[-which(selected_factors == "Label")]
          split_label_into_fill <- TRUE
          factor_for_stacking <- "Label"
        }
        if("Maintenance_Level" %in% selected_factors){
          # remove level from selected factors and use for fill on the pareto
          selected_factors <- selected_factors[-which(selected_factors == "Maintenance_Level")]
          split_label_into_fill <- TRUE
          factor_for_stacking <- "Maintenance_Level"
        }
        
        # else treat the factor the same as time-dependent
          # name should be wide to go along the bottom of the plot - use "+" to collapse factor names
        single_factor_name <- gsub(pattern = "\n", x = single_factor_name, replacement = "+")
        
        # save the factor name (concat of all factor names) for plotting
        grouped_events[["single_factor"]] <- do.call(what = paste, 
                                                     args = c(grouped_events %>% select_(.dots = selected_factors), sep=" - "))
        
        # attach field name to selected_factors vector so it stays around after summarising
        selected_factors <- c(selected_factors, "single_factor")
        # put label or maintenance level back if it was removed
        if(split_label_into_fill){
          selected_factors <- c(selected_factors, factor_for_stacking)
        }
        
        y_label <- "Events\n"
        # if selected, must fill in all the missing dates with zeros to get the average number of SNs through the entire time period (min to max global maintenance dates)
        #  then attach the total number of aircraft per group per day to normalize actions
        #  should plot Total Actions at a location over Average (daily) aircraft quantity at that location
        if(!is.null(values$normalize_option) && values$normalize_option != "None"){
          y_label <- "Events Per Aircraft\n"
          returned_list  <- NormalizeMultiFactorParetoWithSN(grouped_events, selected_factors, 
                                                             values$normalize_option, input$time_dependent_group_selection, 
                                                             days_per_time, sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles)
          grouped_events <- returned_list[["grouped_events"]]
          y_label        <- returned_list[["y_label"]]
          round_num      <- returned_list[["round_num"]]
          
          # if serial number is not chosen to disaggregate then "average" across serial numbers
          if(!("Serial_Number" %in% selected_factors)){
            # No Serial Number - "average" across serial numbers
            # grouped events includes serial number as group so re-group without it
            if(any(grepl(pattern = "Assigned_Location", x = selected_factors))){
              loc_factor <- selected_factors[which(grepl(pattern = "Assigned_Location", x = selected_factors))]
              grouped_events <- grouped_events %>% ungroup() %>% group_by_(.dots = selected_factors) %>% 
                inner_join(
                  select_(values$events_filtered_adj, loc_factor, "Aircraft_Any_Asgn_Loc") %>% distinct(),
                  by = loc_factor
                ) %>% summarise(actions = sum(actions)/mean(Aircraft_Any_Asgn_Loc))
            } else {
              # divide by all aircraft
              aircraft_total <- values$events_filtered_adj[1, "Aircraft_Any_Asgn_Tot"]
              grouped_events <- grouped_events %>% ungroup() %>% group_by_(.dots = selected_factors) %>% 
                summarise(actions = sum(actions)/aircraft_total)
            }
          }
          
        } else {
          # group by multiple group factors but not time
          grouped_events <- grouped_events %>% group_by_(.dots = selected_factors) %>% summarise(actions = n())
          y_label <- "Events\n"
          round_num <- 1
        } 
        
        # add line break in name to give less chance bar labels overlap
        grouped_events$single_factor <- gsub(x = grouped_events$single_factor, pattern = " - ", replacement = "\n")
        
        # order for pareto and plot
        # Event Label
        if(split_label_into_fill){
          
          # can't plot more than n (16ish) bar colors b/c colour palette isn't large enough
          shiny::validate(
            need(try(length(unique(grouped_events[[factor_for_stacking]])) <= max_colors), em_too_few_colors_defined)
          )
          
          # regroup to get order of the bars
          # split by location severity if selected
          factors_without_stack <- selected_factors[!(grepl(factor_for_stacking, selected_factors))] # avoid '-which()'
          factors_for_y_label <- factors_without_stack[!(grepl("single_factor", factors_without_stack))]
          factors_for_y_label[grepl("Location", factors_for_y_label)] <- gsub(pattern = "_Name", replacement = "", x = factors_for_y_label[grepl("Location", factors_for_y_label)])
          factors_for_y_label[grepl("wuc", tolower(factors_for_y_label))] <- "Work_Unit_Code" # catch reduced_wuc and wuc_narrative
          factors_for_y_label <- paste(factors_for_y_label, collapse = "+")
          
          if(input$sort_by_severity && any(grepl("Location", selected_factors))){
            #   get count across Event Label so pareto of stacked bar makes sense
            grouped_events_for_order <- grouped_events %>% group_by_(.dots = factors_without_stack) %>% summarise(actions = sum(actions))
            # remove _Name from location in case assigned_location_name. severity field names do not have _Name
            location_name_full <- selected_factors[which(grepl("Location", selected_factors))]
            location_name <- gsub(pattern = "_Name", replacement = "", x = location_name_full)
            # attach severity index to filtered and aggregated data set and sort factors by both Severity Index and actions count
            grouped_events_for_order <- grouped_events_for_order %>% inner_join(
              values$events_filtered_adj %>% select_(location_name_full, 
                                                 paste0(location_name,"_Severity_Label"),
                                                 paste0(location_name,"_Severity_Index")) %>% distinct(),
              by = location_name_full) %>%
              # rename fields to make predictable
              rename_("Severity_Label" = paste0(location_name,"_Severity_Label"), 
                      "Severity_Index" = paste0(location_name,"_Severity_Index"))
            # find order
            factor_order <- grouped_events_for_order$single_factor[order(grouped_events_for_order$Severity_Index, -grouped_events_for_order$actions)]
            grouped_events$single_factor <- factor(grouped_events$single_factor, levels = factor_order)
            grouped_events[[factor_for_stacking]] <- as.factor(grouped_events[[factor_for_stacking]])
            # find placement of labels and lines
            severity_labels <- grouped_events_for_order %>% group_by(Severity_Label, Severity_Index) %>% summarise(ct = n())
            severity_labels <- severity_labels[order(severity_labels$Severity_Index), ] # arrange isn't working
            severity_labels$ctcum = cumsum(severity_labels$ct)
            if(nrow(severity_labels)>1){
              # more than one type of location severity
              vlines <- severity_labels$ctcum[1:(nrow(severity_labels) - 1)] + 0.5
              severity_labels$pos <- c(vlines - 0.5, max(severity_labels$ctcum))  
            } else {
              # only one type of location severity - plot name but not line
              vlines <- NA
              severity_labels$pos <- max(severity_labels$ctcum)
            }
          } else {
            # else don't split by location severity
            grouped_events_for_order <- grouped_events %>% group_by(single_factor) %>% summarise(actions = sum(actions))
            factor_order <- unname(unlist(grouped_events_for_order[order(
              grouped_events_for_order$actions, decreasing = TRUE), ]$single_factor)) # gets single factor
            grouped_events$single_factor <- factor(unname(unlist(grouped_events$single_factor)), levels = factor_order)
            grouped_events[[factor_for_stacking]] <- as.factor(grouped_events[[factor_for_stacking]]) 
          }
          # normalizing by assigned location when no assigned locations are defined gives an empty data frame
          #   don't try to plot this 
          shiny::validate(
            need(try(nrow(grouped_events) > 0), "Configuration results in no data.")
          )
          to_return <- ggplot(grouped_events, aes_string(x = "single_factor", 
                                       y = "actions", fill = factor_for_stacking)) + 
              geom_bar(stat = "identity") + labs(x = paste0(MakeTitleCase(factors_for_y_label),"\n"), y = y_label) + 
              scale_fill_manual(name = MakeTitleCase(factor_for_stacking), values = chosen_color_manual_palette) +
            theme_bw() + 
              theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), 
                    axis.ticks.x = element_blank(), legend.position = "bottom",
                    legend.text = element_text(size = rel(legend_text_rel_size)),
                    legend.title = element_text(size = rel(legend_title_rel_size)),
                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                    axis.title = element_text(size = rel(axis_title_rel_size)))
          if(input$pareto_labels){
                # for stacked bar attach total labels to each bar
            to_return <- to_return + geom_text(data = grouped_events_for_order, inherit.aes = FALSE, 
                                               aes(x = single_factor, y = actions, label = round(actions, round_num), 
                              vjust = annot_pos_below), 
                              size = rel(pareto_label_rel_size)) +
            # Also plot individual elements below bars
              geom_text(aes_q(label = quote(round(actions, round_num)), colour = grouped_events[[factor_for_stacking]], 
                        y = -max(grouped_events_for_order[["actions"]])/20*
                          (max(as.numeric(grouped_events[[factor_for_stacking]]))-
                             as.numeric(grouped_events[[factor_for_stacking]])+1)),
                        size = rel(pareto_label_rel_size),
                        show.legend = FALSE) + 
              scale_colour_manual(name = NULL, values = chosen_color_manual_palette) +
              # remove negative y-axis labels that appear b/c ticks are below bars (i'd like to remove ticks too but that's hard)
              scale_y_continuous(labels = RemoveNegativeLabels)
              }  # otherwise no labels
          if(input$sort_by_severity && any(grepl("Location", selected_factors))){
            to_return <- to_return + geom_text(data = severity_labels, inherit.aes = FALSE, # no Label, so don't inherit aes
                                               aes(label = Severity_Label, x = pos, 
                                                   y = max(grouped_events_for_order$actions)*1.08), # padding in case max bar is at label
                                               size = rel(pareto_label_rel_size)) + 
              geom_vline(xintercept = vlines)
          }
          return(to_return)
          
        } else {
          # single factor order
          # split by location severity if selected
          if(input$sort_by_severity && any(grepl("Location", selected_factors))){
            # location name complexities b/c could be label ("_Name") or code
            location_name_full <- selected_factors[which(grepl("Location", selected_factors))]
            location_name <- gsub(pattern = "_Name", replacement = "", x = location_name_full)
            # attach severity index to filtered and aggregated data set and sort factors by both Severity Index and actions count
            
            grouped_events <- grouped_events %>% inner_join(
              values$events_filtered_adj %>% select_(location_name_full, 
                                                 paste0(location_name,"_Severity_Label"),
                                                 paste0(location_name,"_Severity_Index")) %>% distinct(),
              by = location_name_full) %>%
              # rename fields to make predictable
              rename_("Severity_Label" = paste0(location_name,"_Severity_Label"), 
                      "Severity_Index" = paste0(location_name,"_Severity_Index"))
            # find order
            factor_order <- grouped_events$single_factor[order(grouped_events$Severity_Index, -grouped_events$actions)]
            grouped_events$single_factor <- factor(grouped_events$single_factor, levels = factor_order)
            
            shiny::validate(
              need(try(nrow(grouped_events) > 0), "Configuration results in no data.")
            )
            
            # find placement of labels and lines
            severity_labels <- grouped_events %>% group_by(Severity_Label, Severity_Index) %>% summarise(ct = n())
            severity_labels <- severity_labels[order(severity_labels$Severity_Index), ] # arrange isn't working
            severity_labels$ctcum = cumsum(severity_labels$ct)
            if(nrow(severity_labels)>1){
              # more than one type of location severity
              vlines <- severity_labels$ctcum[1:(nrow(severity_labels)-1)] + 0.5
              severity_labels$pos <- c(vlines - 0.5, max(severity_labels$ctcum))  
            } else {
              # only one type of location severity - plot name but not line
              vlines <- NA
              severity_labels$pos <- max(severity_labels$ctcum)
            }
            
            
          } else {
            # Normal Pareto
            factor_order <- unname(unlist(grouped_events[order(
              grouped_events$actions, decreasing = TRUE), ]$single_factor)) 
            grouped_events$single_factor <- factor(unname(unlist(grouped_events$single_factor)), levels = factor_order)  
          }
          # normalizing by assigned location when no assigned locations are defined gives an empty data frame
          #   don't try to plot this 
          shiny::validate(
            need(try(nrow(grouped_events)>0), "Configuration results in no data.")
          )
          to_return <- ggplot(grouped_events, aes(x = single_factor, y = actions, fill = "All Data")) + 
              geom_bar(stat = "identity") + labs(x = MakeTitleCase(single_factor_name), y = y_label) + 
              scale_fill_manual(values = "#0799B9") + theme_bw() + 
              theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), 
                    axis.ticks.x = element_blank(), legend.position = "none", 
                    axis.text = element_text(size = rel(axis_text_rel_size)), 
                    axis.title = element_text(size = rel(axis_title_rel_size)))
          if(input$pareto_labels){
            to_return <- to_return + geom_text(aes(label = round(actions, round_num), 
                                                   vjust = annot_pos_below),
                                               size = rel(pareto_label_rel_size)) 
          }
          if(input$sort_by_severity && any(grepl("Location", selected_factors))){
            to_return <- to_return + geom_text(data = severity_labels, 
                                               aes(label = Severity_Label, x = pos, 
                                                   y = max(grouped_events$actions)*1.08), # padding in case max bar is at label
                                               size = rel(pareto_label_rel_size)) + geom_vline(xintercept = vlines)
          }
          
          return(to_return)
        }
      } else { # time between event for multiple factors
        # first factor deaggregated is x axis
        # second factor deaggregated is panel
        # third factor deaggregated is included in panel with second factor
        # no stacked bars.
        
        # values$selected_agg_order # five options: sn, loc, wuc, label, depot
        # name should be wide to go along the bottom of the plot - use "+" to collapse factor names
        
        # if more than two factor types selected than group the 2nd-last ones into a single factor for facet
        # otherwise just use the 2nd for the facet name (as single_factor)
        # Save factor names for group by
        second_factors <- selected_factors[!(selected_factors %in% selected_agg_order_map[[values$selected_agg_order[[1]]]])]
        
        first_factor <- selected_factors[selected_factors %in% selected_agg_order_map[[values$selected_agg_order[[1]]]]]
        
        
        # save the factor name (concat of all factor names) for plotting
        grouped_events[["single_factor"]] <- do.call(what = paste, 
                                                    args = c(grouped_events %>% select_(.dots = selected_factors), sep=" - ")) # not displayed anywhere
        # split single factor into first factor and everything-else factor (facet_factor) for sending to facet
        grouped_events[["facet_factor"]] <- do.call(what = paste, 
                                                    args = c(grouped_events %>% select_(.dots = second_factors), sep="\n")) # for display in facet strip label
        grouped_events[["first_factor"]] <- grouped_events[[first_factor]]
        
        # attach special field names to selected_factors vector so it stays around after summarising
        selected_factors <- c(selected_factors, "single_factor", "facet_factor", "first_factor")
        
        # if single factor is assigned location (code or name) then divide days at location by actions at location
        #  else divide days total over actions total
        days_division_variable <- "Days_SN_Asgn_Tot"
        if(any(grepl(pattern = "Assigned_Location", x = selected_factors))){
          days_division_variable <- "Days_SN_Asgn_Loc"
        }
        
        # calculate days between events
        grouped_events <- grouped_events %>% filter(Serial_Number != "None") %>%
          # filter out records with no serial number and serial numbers with no assigned days
          filter_(paste0("!is.na(",days_division_variable,")")) %>%
          # unique days - SN may be in selected_factors, and that's okay
          group_by_(.dots = selected_factors, "Serial_Number", "Transaction_Date", days_division_variable) %>%
          # unique factors including SN - count event-days and calculate dbe
          distinct() %>% ungroup() %>% 
          group_by_(.dots = selected_factors, "Serial_Number", days_division_variable) %>% 
          summarise(actions = n()) %>% mutate_(dbe = paste0(days_division_variable,"/actions")) %>%
          # unique factors excluding SN - average dbe across SNs. SN may be in single_factor or facet_factor, and that's okay.
          ungroup() %>% group_by_(.dots = selected_factors) %>% summarise(dbe = mean(dbe))
        
        second_factors[grepl("wuc", tolower(second_factors))] <- "Work_Unit_Code" # catch reduced_wuc and wuc_narrative
        first_factor[grepl("wuc", tolower(first_factor))] <- "Work_Unit_Code" # catch reduced_wuc and wuc_narrative
        
        round_num <- FindDigitsToRound(min(grouped_events$dbe))
        
        # order chart
        #  first the facets
        facet_order <- grouped_events %>% group_by(facet_factor) %>% summarise(min_dbe = min(dbe)) %>% arrange(min_dbe)
        grouped_events[, "facet_factor"] <- factor(unname(unlist(grouped_events[, "facet_factor"])), levels = facet_order[[1]])
        #  then the dots within the facets
        x_axis_order <- grouped_events %>% ungroup() %>% arrange(dbe) %>% select(single_factor)
        grouped_events[, "single_factor"] <- factor(unname(unlist(grouped_events[, "single_factor"])), levels = x_axis_order[[1]])
        
        to_return <- ggplot(grouped_events, aes(x = first_factor, y = dbe)) + 
          geom_point(stat = "identity", size = 3, colour = "#0799B9") + 
          facet_grid(. ~ facet_factor, scale = "free", space = "free_x") + theme_bw() + 
          theme(axis.text.x = element_text(angle = 90)) + 
          theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), 
                legend.position = "none", 
                strip.text = element_text(size = rel(axis_text_rel_size), colour = "white"),
                strip.background = element_rect(fill = "#0799B9"),
                axis.text = element_text(size = rel(axis_text_rel_size)), 
                axis.title = element_text(size = rel(axis_title_rel_size))) + 
          ylim(c(0, max(grouped_events$dbe)*1.02)) +
          labs(y = "Days Between Events", x = MakeTitleCase(first_factor))
        if(input$pareto_labels){
          to_return <- to_return + geom_text(aes(label = round(dbe, round_num), 
                                                 vjust = annot_pos_below_dot), 
                                             size = rel(pareto_label_rel_size))
        }
        return(to_return)
    
      }
      # shouldn't be here
      stop("something's wrong ref: 2")
    }
    })
  })
  
  # Final Plot Data to show the plot the user wants:
  #  Controls the Auto Updating or Plot Refresh
  #  Need to do this if/else check in a reactive instead of the renderPlot so that the user
  #   can download the plot that's on the screen, as expected
  #   (instead of downloading what the controls show, even if the Auto Update flag is false)
  final_plot <- reactive({
    if(input$autorefresh_plot){
      return(
        withProgress(message = 'Calculating...', value = 0, expr = {
          intermediate_plot_calculation()})
        )
    } else {
      input$refresh_plot_action 
      return(
        withProgress(message = 'Calculating...', value = 0, expr = {
          isolate(intermediate_plot_calculation())})
        )
    }
  }
  )
  
  
# Observers ---------------------------------------------------------------
  
  # Plot click - select events that are nearest the click values
  observeEvent(input$plot_click, {
    # for pareto, clicking on a bar may not return that bar's events.  this is because the events the click is trying to find is tied to the y at the top of the bars
    #   TODO: fix this so that a click on a bar always returns that bar

    # minimize calculations and if statements here. the semi-join should do the majority of the work
    # if all data is selected then simply return all the data
    if("yy" %in% colnames(final_plot()$data)){
      values$nearest_events <- values$events_filtered_adj
    } else {
      # otherwise subset the data to include only the events near the plot click
      nearest_events_plot_data <- nearPoints(df = final_plot()$data, coordinfo = input$plot_click, 
                                             threshold = 1e5, maxpoints = 1)
      
      # nearPoints doesn't work with stacked bar to get proper Y value so must do manually
      if((any("Label" %in% names(final_plot()$data)) || any(grepl("Maintenance_Level", names(final_plot()$data)))) &&
         input$plot_type == "Pareto" && length(names(final_plot()$data)) > 2){
        # get "label" or "maintenance_level" since can't be both
        stack_factor_name <- list("t" = "Label", "f" = "Maintenance_Level")[[1 + any(grepl("Maintenance_Level", names(final_plot()$data)))]]
        x_val <- nearest_events_plot_data$single_factor
        stacked_levels <- final_plot()$data[final_plot()$data$single_factor == x_val, ] %>% 
          mutate(actions_cum = cumsum(actions), y_click_dist = abs(actions_cum-input$plot_click$y))
        nearest_events_plot_data[[stack_factor_name]] <- stacked_levels[stacked_levels$y_click_dist == min(stacked_levels$y_click_dist), ][[stack_factor_name]]
        nearest_events_plot_data$actions <- stacked_levels[stacked_levels$y_click_dist == min(stacked_levels$y_click_dist), ]$actions
      }
      
      values$nearest_events <- semi_join(values$events_filtered_adj, nearest_events_plot_data)
    }

    # drop unnecessary fields
    values$nearest_events <- values$nearest_events %>% 
      select(id, Serial_Number, Job_Control_Number,
             Assigned_Location, Assigned_Location_Name, Assigned_Location_Severity_Label, 
             Performing_Location, Performing_Location_Name, 
             Performing_Location_Severity_Label, Work_Unit_Code, WUC_Narrative, WUC_User_Defined, Transaction_Date, 
             Transaction_Date_Adj, Labor_Manhours, Discrepancy_Narrative, Work_Center_Event_Narrative, 
             Corrective_Narrative, When_Discovered_Code, How_Malfunction_Code, 
             Action_Taken_Code, Label, Maintenance_Level)
  })
  
  observeEvent(input$normalize_option, {
    # set normalize options reactiveValue to its input value
    values$normalize_option <- input$normalize_option
  }, priority = 1 # before intermediate_plot_calcuation
  )
  
  observe({
    # when user selects Time Dependent or Time Between Event (normalization only possible with Pareto Chart for now)
    #  disable normalization option control
    if(input$plot_type != "Pareto"){
      disable("normalize_option")
    } else {
      enable("normalize_option")
    }
  })
  
  observe({
    # When user changes location type set normalization option to None.
    # Normalization is only available when location is set to Assigned Location
    if(!is.null(input$loc_type)){
      
      if(input$loc_type == "Performing"){
        values$normalize_option <- "None"
        updateRadioButtons(session, inputId = "normalize_option", selected = "None")
        disable("normalize_option")
      } else if (input$plot_type == "Pareto") {
        # Time Dependent still shouldn't allow normalization
        enable("normalize_option")
      }  
    }
  })
  
  observe({
    # only one of (1)event label (2)maintenance level can be disaggregated.  disable one when the other is disaggregated
    if(!is.null(input$label_agg) && !is.null(input$depot_agg)){
      if(!(input$label_agg)){
        shinyjs::disable("depot_agg")
      } else {
        shinyjs::enable("depot_agg")
      }
      
      if(!(input$depot_agg)){
        shinyjs::disable("label_agg")
      } else {
        shinyjs::enable("label_agg")
      }
    }
  })
  
  observe({
    # when user has Auto Refresh Plot option selected, disable the Update Plot button
    if(input$autorefresh_plot){
      disable("refresh_plot_action")
    } else {
      enable("refresh_plot_action")
    }
  })

  observe({
    # when user has Time Dependent plot, disable Sort Pareto by Severity and Pareto Annotations options
    if(input$plot_type == "Time Dependent"){
      disable("pareto_labels")
      disable("sort_by_severity")
    } else {
      enable("pareto_labels")
      enable("sort_by_severity")
    }
  })
  
  observe({
    # only allow sort by severity if location is disaggregated
    if(!is.null(input$loc_agg) && input$loc_agg){
      shinyjs::disable("sort_by_severity")
    } else {
      shinyjs::enable("sort_by_severity")
    }
  })
  
  observeEvent(input$wuc_type, {
    # Each time the user chooses to aggregate or disaggregate WUC save the selected WUC type
    #  The next time a user chooses to disaggregate WUC the type option from before is loaded.
    #  This is useful in its own right, and it avoids re-loading the selction options and plot with the default five-digit-wuc
    values$wuc_type_selection <- input$wuc_type
  })

  observeEvent(input$loc_type, {
    # Location too
    values$loc_type_selection <- input$loc_type
  })
  
  observe({
    # force events filtered to update before final_plot
    #  this is also triggered anytime the reactive events_filtered() changes
    input$loc_type
    input$wuc_type
    input$sn_agg
    values$events_filtered <- events_filtered()
  }, priority = 1)
  
  observe({
    if(!is.null(input$plot_type)){#!is.null(values$events_filtered) && !is.null(input$plot_type)){
      class(values$events_filtered) # dependence
      if(input$plot_type == "Time Dependent"){
        input$time_dependent_group_selection
      }
      
      # need to isolate values$events_filtered_adj fromm itself, otherwise infinite update loop
      isolate({
        values$events_filtered_adj <- values$events_filtered
        if(input$plot_type == "Time Dependent"){
          # convert days to their grouped date, like most-recent Quarter
          if(input$time_dependent_group_selection != "Day"){
            values$events_filtered_adj[["Transaction_Date_Adj"]] <- floor_date(values$events_filtered_adj[["Transaction_Date"]], 
                                                                               unit = tolower(input$time_dependent_group_selection))
          }
        }
      })
    }
    
  }, priority = 1)
  
  observe({
    input$loc_type
    # initiates loc_selection with top n
    # also clears loc selection every time user chooses a different location type
    # this will flush the events table (make it empty) so nothing is plotted
    #  until input$loc_selection is refreshed with new options
    # if loc selection is hidden then set selection to empty string (not null)
    if(is.null(input$loc_agg) || input$loc_agg) {
      values$loc_selection <- ""
    } else {
      isolate(
        # don't update every time the options change
        loc_options_local <- loc_options()
      )
      values$loc_selection <- loc_options_local[1:isolate(input$top_n_selection)]
    }
  }, priority = 1)
  
  observe({
    input$wuc_type
    # same thing for wuc
    if(is.null(input$wuc_agg) || input$wuc_agg) {
      values$wuc_selection <- ""
    } else {
      isolate(
        # don't update every time the options change
        wuc_options_local <- wuc_options_selected_type_as_list()
      )
      values$wuc_selection <- wuc_options_local[1:isolate(input$top_n_selection)]
    }
  }, priority = 1)
  
  observe({
    input$sn_agg
    # same thing for sn, which has no type so take dependency on agg
    if(is.null(input$sn_agg) || input$sn_agg) {
      values$sn_selection <- ""
    } else {
      isolate(
        # don't update every time the options change
        sn_options_local <- sn_options()
      )
      values$sn_selection <- sn_options_local[1:isolate(input$top_n_selection)]
    }
  }, priority = 1)
  
  observe({
    input$label_agg
    # same thing for sn, which has no type so take dependency on agg
    if(is.null(input$label_agg) || input$label_agg) {
      values$label_selection <- ""
    } else {
      isolate(
        # don't update every time the options change
        label_options_local <- label_options()
      )
      values$label_selection <- label_options_local[1:input$top_n_selection]
    }
  }, priority = 1)
  
  observe({
    input$depot_agg
    # same thing for sn, which has no type so take dependency on agg
    if(is.null(input$depot_agg) || input$depot_agg) {
      values$depot_selection <- ""
    } else {
      values$depot_selection <- c("Depot", "Field")
    }
  }, priority = 1)
  
  
  observe({
    input$loc_selection
    # clicking off the last option will set selection to NULL
    # this conflicts with null checking elsewhere
    # instead, set to empty string
    if(!is.null(isolate(input$loc_agg)) && is.null(input$loc_selection)){
      values$loc_selection <- ""
    } else {
    # values is used to filter instead of input$loc_selection
      values$loc_selection <- input$loc_selection
    }
  })
  
  observe({
    input$wuc_selection
    # update wuc selections reactiveValues on option selection
    if(!is.null(isolate(input$wuc_agg)) && is.null(input$wuc_selection)){
      values$wuc_selection <- ""
    } else {
      # values is used to filter instead of input$loc selection
      values$wuc_selection <- input$wuc_selection
    }
  })
  
  observe({
    input$sn_selection
    # update sn selections reactiveValues on option selection
    if(!is.null(isolate(input$sn_agg)) && is.null(input$sn_selection)){
      values$sn_selection <- ""
    } else {
      # values is used to filter instead of input$loc selection
      values$sn_selection <- input$sn_selection
    }
  })
  
  observe({
    input$label_selection
    # update label selections reactiveValues on option selection
    if(!is.null(isolate(input$label_agg)) && is.null(input$label_selection)){
      values$label_selection <- ""
    } else {
      # values is used to filter instead of input$loc selection
      values$label_selection <- input$label_selection
    }
  })
  
  observe({
    input$depot_selection
    # update depot selections reactiveValues on option selection
    if(!is.null(isolate(input$depot_agg)) && is.null(input$depot_selection)){
      values$depot_selection <- ""
    } else {
      # values is used to filter instead of input$loc selection
      values$depot_selection <- input$depot_selection
    }
  })
  
  
  # each time user selects an aggregation action add or remove it from the aggregation list
  #   input$loc_agg has the new value (after the user clicks)
  observeEvent(input$loc_agg, {
    # if user selects "aggregate" and location is in the list (expected outcome)
    if(input$loc_agg && "loc" %in% values$selected_agg_order[1:factor_size]){
      # remove it from the list
      values$selected_agg_order <- values$selected_agg_order[-which(values$selected_agg_order[1:factor_size]=="loc")]
    } else if(!input$loc_agg && !("loc" %in% values$selected_agg_order[1:factor_size])){
      # if user un-selects "aggregate" and location is not in the list (expected outcome)
      # add it to the end of the list
      values$selected_agg_order <- c(values$selected_agg_order, "loc")
    } else if(!input$loc_agg && !("loc" %in% values$selected_agg_order[1:factor_size])){
      # if user un-selectes "aggregate" and location is in the list (not expected)
        stop("reached here in error ref: 3") # this shouldn't happen
      }
  }, priority = 2) # highest priority
  
  # do the same for wuc, sn, event label, and maintenance level
  observeEvent(input$sn_agg, {
    # if user selects "aggregate" and location is in the list (expected outcome)
    if(input$sn_agg && "sn" %in% values$selected_agg_order[1:factor_size]){
      # remove it from the list
      values$selected_agg_order <- values$selected_agg_order[-which(values$selected_agg_order[1:factor_size]=="sn")]
    } else if(!input$sn_agg && !("sn" %in% values$selected_agg_order[1:factor_size])){
      # if user un-selects "aggregate" and location is not in the list (expected outcome)
      # add it to the end of the list
      values$selected_agg_order <- c(values$selected_agg_order, "sn")
    }
  }, priority = 2) # highest priority
  
  observeEvent(input$wuc_agg, {
    # if user selects "aggregate" and location is in the list (expected outcome)
    if(input$wuc_agg && "wuc" %in% values$selected_agg_order[1:factor_size]){
      # remove it from the list
      values$selected_agg_order <- values$selected_agg_order[-which(values$selected_agg_order[1:factor_size]=="wuc")]
    } else if(!input$wuc_agg && !("wuc" %in% values$selected_agg_order[1:factor_size])){
      # if user un-selects "aggregate" and location is not in the list (expected outcome)
      # add it to the end of the list
      values$selected_agg_order <- c(values$selected_agg_order, "wuc")
    }
  }, priority = 2) # highest priority
  
  observeEvent(input$label_agg, {
    # if user selects "aggregate" and location is in the list (expected outcome)
    if(input$label_agg && "label" %in% values$selected_agg_order[1:factor_size]){
      # remove it from the list
      values$selected_agg_order <- values$selected_agg_order[-which(values$selected_agg_order[1:factor_size]=="label")]
    } else if(!input$label_agg && !("label" %in% values$selected_agg_order[1:factor_size])){
      # if user un-selects "aggregate" and location is not in the list (expected outcome)
      # add it to the end of the list
      values$selected_agg_order <- c(values$selected_agg_order, "label")
    }
  }, priority = 2) # highest priority
  
  observeEvent(input$depot_agg, {
    if(input$depot_agg && "depot" %in% values$selected_agg_order[1:factor_size]){
      values$selected_agg_order <- values$selected_agg_order[-which(values$selected_agg_order[1:factor_size]=="depot")]
    } else if(!input$depot_agg && !("depot" %in% values$selected_agg_order[1:factor_size])){
      values$selected_agg_order <- c(values$selected_agg_order, "depot")
    }
  }, priority = 2) # highest priority
  
  ## select all or none factors on button click.  add or remove items from search box
  observeEvent(input$loc_select_none_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "loc_selection", selected = character(0))
      )
    })
  
  observeEvent(input$loc_select_all_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "loc_selection", selected = loc_options())
    )
  })

  observeEvent(input$loc_add_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "loc_selection", selected = c(values$loc_selection, input$loc_selection_searched))
    )
  })
  
  observeEvent(input$loc_remove_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "loc_selection", selected = values$loc_selection[!(values$loc_selection %in% input$loc_selection_searched)])
    )
  })
  
  observeEvent(input$sn_select_none_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "sn_selection", selected = character(0))
    )
  })
  
  observeEvent(input$sn_select_all_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "sn_selection", selected = sn_options())
    )
  })
  
  observeEvent(input$sn_add_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "sn_selection", selected = c(values$sn_selection, input$sn_selection_searched))
    )
  })
  
  observeEvent(input$sn_remove_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "sn_selection", selected = values$sn_selection[!(values$sn_selection %in% input$sn_selection_searched)])
    )
  })
  
  observeEvent(input$wuc_select_none_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "wuc_selection", selected = character(0))
    )
  })
  
  observeEvent(input$wuc_select_all_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "wuc_selection", selected = wuc_options_selected_type_as_list())
    )
  })
  
  observeEvent(input$wuc_add_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "wuc_selection", selected = c(values$wuc_selection, input$wuc_selection_searched))
    )
  })
  
  observeEvent(input$wuc_remove_searched, {
    isolate(
      updateCheckboxGroupInput(session, inputId =  "wuc_selection", selected = values$wuc_selection[!(values$wuc_selection %in% input$wuc_selection_searched)])
    )
  })
  
  observeEvent(input$label_select_none_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "label_selection", selected = character(0))
    )
  })
  
  observeEvent(input$label_select_all_btn, {
    isolate(
      updateCheckboxGroupInput(session, inputId = "label_selection", selected = label_options())
    )
  })
  
  # clear selections from search box
  observeEvent(input$loc_clear_searched, {
    isolate(
      updateSelectizeInput(session, inputId =  "loc_selection_searched", selected = "")
    )
  })
  observeEvent(input$sn_clear_searched, {
    isolate(
      updateSelectizeInput(session, inputId =  "sn_selection_searched", selected = "")
    )
  })
  observeEvent(input$wuc_clear_searched, {
    isolate(
      updateSelectizeInput(session, inputId =  "wuc_selection_searched", selected = "")
    )
  })
  
# Outputs -----------------------------------------------------------------
  
  # UI elements ----------------------
  
  # Time Period
  output$time_dependent_group <- renderUI({
    # I am making heavy use of null checks and hiding both the inputs or output plot.
    #  An alternative may be the conditional panel feature, which uses javascript instead of R to check conditions.
    tags$div(class = "well", class = "well-shiny-option",
             radioButtons("time_dependent_group_selection", label = "Time Period:", 
                          choices = c("Day", "Week", "Month", "Quarter", "Year"), 
                          selected = "Year"))
  })
  
  # Normalization Options
  output$normalize_control <- renderUI({
    isolate(
      if(is.null(input$plot_type)){
        return(NULL)
      }
    )
    
    # Time-dependent Normalization options shouldn't mention Time Period - it's redundant --- EXCLUDE for now
    #if(input$plot_type == "Time Dependent"){
    #  return(GenerateNormalizationOptionsWithTooltip(list("Assigned Aircraft", "Flying Hours")))
    #} else {
      return(GenerateNormalizationOptionsWithTooltip(list("Time Period & Assigned Aircraft", "Flying Hours", "Depot Cycles")))
    #}
    
  })
  
  output$top_n_select <- renderUI({
    # controls the top_n number to select when first disaggregating a factor
    # render UI so loads with other controls
    # thin input with custom label at right
    #numericInput("top_n_selection", label = "", value = 4, step = 1, width = 70),
    tags$div(class = "well", class = "well-shiny-option",    
             HTML('<div class="form-group shiny-input-container" style="width: 70px; display:inline-block; margin-top:6px; margin-bottom:6px">
                  <input id="top_n_selection" type="number" class="form-control" value="4" min="0" step="1"/>
                  </div>'),
             tags$span("Initial Options to Select", style = "padding-left: 10px"))
  })
  
  ##### Location selection options
  
  output$loc_agg_select <- renderUI({
    if (is.null(events())) {
      return(NULL)
    }
      
    checkboxInput("loc_agg", label = "Aggregate", value = TRUE)
  })
  
  output$loc_agg_select_helptext <- renderUI({
    selected_num <- which(values$selected_agg_order[1:factor_size] == "loc")
    # if doesnt exist in selected list then selected_num will be integer(), i.e. a zero-length integer
    HTML(GenerateAggCheckboxAnnotation("Location", 
                                       ifelse(length(selected_num) == 0, '', 
                                              factor_selection_order_map[[as.character(selected_num)]])
    ))
  })
  
  output$loc_type_select <- renderUI({
    if (is.null(events()) || is.null(input$loc_agg) || input$loc_agg) {
      return(NULL)
    }
    # HTML to include info button
    tags$div(class = "well", class = "well-shiny-option",
             HTML(paste0('<div id="loc_type" class="form-group shiny-input-radiogroup shiny-input-container">
<label class="control-label" for="loc_type">Type</label>
<div class="pull-right" style="font-size: 16px">
<a class="loc_type_info" data-toggle="tooltip" data-placement="bottom" title="Performing Maintenance Options:
Pareto does not normalize. Time between Events is calculated as total days over event-days\nwhereas Assigned Location uses days at that assigned location.">
<span id="custom-info" class="glyphicon dropdown-toggle glyphicon-info-sign info"></span>
</a>
</div>
<div class="shiny-options-group">
<div class="radio">
<label>
<input type="radio" name="loc_type" value="Assigned" ', 
ifelse(values$loc_type_selection=="Assigned", 'checked="checked"',''), 
'/>','
<span>Assigned</span>
</label>
</div>
<div class="radio">
<label>
<input type="radio" name="loc_type" value="Performing" ', 
ifelse(values$loc_type_selection=="Performing", 'checked="checked"',''),'/>
<span>Performing Maintenance</span>
</label>
</div>
</div>
</div>')))
      #radioButtons("loc_type", choices = list("Assigned" = "Assigned", "Performing Maintenance" = "Performing"), 
      #             selected = values$loc_type_selection, label = "Type")
  })
  
  output$loc_select <- renderUI({
    if (is.null(events()) || is.null(input$loc_agg) || 
        is.null(input$loc_type) || input$loc_agg){
      return(NULL)
    }
    
    # take no dependency on location options and selections, nor non-loc UI elements
    isolate({
      loc_options_local <- loc_options()
      # if empty string is selected (b/c coming back from zero options in another factor) then select initial options
      if(length(values$loc_selection) == 1  && values$loc_selection == ""){
        loc_selections_local <- loc_options_local[1:input$top_n_selection]
      } else {
        loc_selections_local <- values$loc_selection
      }
      wuc_agg_local <- input$wuc_agg
      sn_agg_local  <- input$sn_agg
      label_agg_local  <- input$label_agg
      depot_agg_local  <- input$depot_agg
      })
    
    # take a dependency on wuc options IF it was selected before loc options
    if (!wuc_agg_local && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "wuc") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      input$wuc_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on sn options IF it was selected before loc options
    if (!sn_agg_local && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "sn") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      input$sn_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on event label options IF it was selected before loc options
    if (!label_agg_local && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      input$label_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on maintenance level options IF it was selected before loc options
    if (!depot_agg_local && !input$loc_agg &&
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "loc")) {
      input$depot_selection[1] # just a dummy selection to take dependency
    }
    tagList(
      tags$div(class = "well", class = "well-shiny-option", style = "padding-right:10px;padding-bottom:0px;",
      tags$div(
        actionButton("loc_clear_searched", "Clear", class = "in-well-button"),
        actionButton("loc_remove_searched", "Remove", class = "in-well-button"),
        actionButton("loc_add_searched", "Add", class = "in-well-button"),
        tags$span(selectizeInput("loc_selection_searched", label = "Loc. Search", multiple = TRUE, 
                       choices = loc_options_local,
                       selected = loc_selections_local, 
                       options = {
                         list(
                           placeholder = 'Search for a Location',
                           onInitialize = I('function() { this.setValue(""); }'),
                           selectOnTab = TRUE
                         )
                       }))
      )),
      tags$div(class = "well", class = "well-shiny-option", class = "checkbox-filter-group",
               actionButton("loc_select_none_btn", "None", class = "in-well-button"),
               actionButton("loc_select_all_btn", "All", class = "in-well-button"),
               checkboxGroupInput("loc_selection", label = paste(input$loc_type, "Location"), 
                                  choices = loc_options_local,
                                  selected = loc_selections_local)
    ))
  }
  )
  
  output$which_labels_select <- renderUI({
    if(is.null(input$names_not_codes) || !input$names_not_codes){
      return(NULL)
    } else {
      return(checkboxGroupInput("which_labels", label = "On Which Fields?", 
                                choices = c("Location", "Work Unit Code"), 
                                selected = c("Location", "Work Unit Code")))
    }
  })
  
  ##### SN selection options
  
  output$sn_agg_select <- renderUI({
    if (is.null(events())) {
      return(NULL)
    }
    
    checkboxInput("sn_agg", label = "Aggregate", value = TRUE)
  })
  
  output$sn_agg_select_helptext <- renderUI({
    selected_num <- which(values$selected_agg_order[1:factor_size] == "sn")
    # if doesnt exist in selected list then selected_num will be integer(), i.e. a zero-length integer
    
    HTML(GenerateAggCheckboxAnnotation("Serial Number", 
                                       ifelse(length(selected_num) == 0, '', 
                                              factor_selection_order_map[[as.character(selected_num)]])
    ))
  })
  
  output$sn_select <- renderUI({
    if (is.null(events())) {
      stop(error_message)
    }
    if (is.null(input$sn_agg) || input$sn_agg){
      return(NULL)
    }
    
    # take no dependency on sn options and selections, nor non-loc UI elements
    isolate({
      sn_options_local <- sn_options()
      # if empty string is selected (b/c coming back from zero options in another factor) then select initial options
      if(length(values$sn_selection) == 1  && values$sn_selection == ""){
        sn_selections_local <- sn_options_local[1:isolate(input$top_n_selection)]
      } else {
        sn_selections_local <- values$sn_selection
      }
      wuc_agg_local <- input$wuc_agg
      loc_agg_local <- input$loc_agg
      label_agg_local <- input$label_agg
      depot_agg_local <- input$depot_agg
    })
    # take a dependency on wuc options IF it was selected before sn options
    if (!wuc_agg_local && !input$sn_agg &&
        which(values$selected_agg_order[1:factor_size] == "wuc") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      input$wuc_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on loc options IF it was selected before sn options
    if (!loc_agg_local && !input$sn_agg &&
        which(values$selected_agg_order[1:factor_size] == "loc") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      input$loc_selection[1] # just a dummy selection to take dependency
    }
    if (!label_agg_local && !input$sn_agg &&
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      input$label_selection[1] # just a dummy selection to take dependency
    }
    if (!depot_agg_local && !input$sn_agg &&
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "sn")) {
      input$depot_selection[1] # just a dummy selection to take dependency
    }
    
    tagList(
      tags$div(class = "well", class = "well-shiny-option", style = "padding-right:10px;padding-bottom:0px;",
        tags$span(
          actionButton("sn_clear_searched", "Clear", class = "in-well-button"),
          actionButton("sn_remove_searched", "Remove", class = "in-well-button"),
          actionButton("sn_add_searched", "Add", class = "in-well-button"),
          selectizeInput("sn_selection_searched", label = "SN Search", multiple = TRUE, 
                         choices = sn_options_local, selected = sn_selections_local, 
                         options = {
                           list(
                             placeholder = 'Search for a Serial Number',
                             onInitialize = I('function() { this.setValue(""); }'),
                             selectOnTab = TRUE
                           )
                         }))
    ),
      tags$div(class = "well", class = "well-shiny-option", class = "checkbox-filter-group",
               actionButton("sn_select_none_btn", "None", class = "in-well-button"),
               actionButton("sn_select_all_btn", "All", class = "in-well-button"),
               checkboxGroupInput("sn_selection", label = "Serial Number", 
                           choices = sn_options_local,
                           selected = sn_selections_local)
    )
    )
  }
  )
  
  ##### WUC selection options
  
  output$wuc_agg_select <- renderUI({
    if (is.null(events())) {
      return(NULL)
    }
    
    checkboxInput("wuc_agg", label = "Aggregate", value = TRUE)
  })
  
  output$wuc_agg_select_helptext <- renderUI({
    selected_num <- which(values$selected_agg_order[1:factor_size] == "wuc")
    # if doesnt exist in selected list then selected_num will be integer(), i.e. a zero-length integer
    
    HTML(GenerateAggCheckboxAnnotation("WUC", 
                                       ifelse(length(selected_num) == 0, '', 
                                              factor_selection_order_map[[as.character(selected_num)]])
                                       ))
  })
  
  output$wuc_type_select <- renderUI({
    if (is.null(events()) || is.null(input$wuc_agg) || input$wuc_agg) {
      return(NULL)
    }
    
    tags$div(class = "well", class = "well-shiny-option",
             radioButtons("wuc_type", choices = wuc_type_choices, 
                          selected = values$wuc_type_selection, label = "Classification", inline = TRUE)
    )
  })
  
  output$wuc_select <- renderUI({
    if (is.null(events())) {
      stop(error_message)
    }
    if(is.null(input$wuc_agg) || input$wuc_agg || is.null(input$wuc_type)){
      return(NULL)
    }
    
    # take no dependency on wuc options or other aggregates, nor non-wuc UI elements 
    isolate({
      wuc_options_local <- wuc_options_selected_type_as_list()
      # if empty string is selected (b/c coming back from zero options in another factor) then select initial options
      if(length(values$wuc_selection) == 1  && values$wuc_selection == ""){
        wuc_selections_local <- wuc_options_local[1:isolate(input$top_n_selection)]
      } else {
        wuc_selections_local <- values$wuc_selection
      }
      loc_agg_local <- input$loc_agg
      sn_agg_local <- input$sn_agg
      label_agg_local <- input$label_agg
      depot_agg_local <- input$depot_agg
    })
    
    # take a dependency on loc options IF it was selected before wuc options
    if (!loc_agg_local && !input$wuc_agg &&
        which(values$selected_agg_order[1:factor_size] == "loc") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      input$loc_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on sn options IF it was selected before wuc options
    if (!sn_agg_local && !input$wuc_agg &&
        which(values$selected_agg_order[1:factor_size] == "sn") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      input$sn_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on lalbel options IF it was selected before wuc options
    if (!label_agg_local && !input$wuc_agg &&
        which(values$selected_agg_order[1:factor_size] == "label") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      input$label_selection[1] # just a dummy selection to take dependency
    }
    # take a dependency on lalbel options IF it was selected before wuc options
    if (!depot_agg_local && !input$wuc_agg &&
        which(values$selected_agg_order[1:factor_size] == "depot") < which(values$selected_agg_order[1:factor_size] == "wuc")) {
      input$depot_selection[1] # just a dummy selection to take dependency
    }
    
    tagList(
      tags$div(class = "well", class = "well-shiny-option", style = "padding-right:10px;padding-bottom:0px;",
               tags$span(
                 actionButton("wuc_clear_searched", "Clear", class = "in-well-button"),
                 actionButton("wuc_remove_searched", "Remove", class = "in-well-button"),
                 actionButton("wuc_add_searched", "Add", class = "in-well-button"),
                         selectizeInput("wuc_selection_searched", label = "WUC Search", multiple = TRUE,
                                        choices = wuc_options_local,
                                        selected = wuc_selections_local, 
                                        options = {
                                          list(
                                            placeholder = 'Search for a Work Unit Code',
                                            onInitialize = I('function() { this.setValue(""); }'),
                                            selectOnTab = TRUE
                                          )
                                        }))
      ),
      tags$div(class = "well", class = "well-shiny-option", class = "checkbox-filter-group",
               actionButton("wuc_select_none_btn", "None", class = "in-well-button"),
               actionButton("wuc_select_all_btn", "All", class = "in-well-button"),
               checkboxGroupInput("wuc_selection", label = names(which(wuc_type_choices==input$wuc_type)), 
                                  choices = wuc_options_local,
                                  selected = wuc_selections_local)
      )
    )
    }
  )
  
  # Event Label Filter #
  output$label_agg_select <- renderUI({
    if (is.null(events())) {
      return(NULL)
    }
    # Event Label can only be disaggregated when Maintenance Level is agreggated
    checkboxInput("label_agg", label = "Aggregate", value = TRUE)
  })
  
  output$label_agg_select_helptext <- renderUI({
    selected_num <- which(values$selected_agg_order[1:factor_size] == "label")
    # if doesnt exist in selected list then selected_num will be integer(), i.e. a zero-length integer
    
    HTML(GenerateAggCheckboxAnnotation("Label", 
                                       ifelse(length(selected_num) == 0, '', 
                                              factor_selection_order_map[[as.character(selected_num)]])
    ))
  })
  
  output$label_select <- renderUI({
    if (is.null(events()) || is.null(input$label_agg) || 
        is.null(label_options) || input$label_agg) {
      return(NULL)
    }
    
    tags$div(class = "well", class = "well-shiny-option",
             actionButton("label_select_none_btn", "None", class = "in-well-button"),
             actionButton("label_select_all_btn", "All", class = "in-well-button"),
             checkboxGroupInput("label_selection", label = "Event Label", 
                                choices = label_options(),
                                selected = label_options()[1:isolate(input$top_n_selection)])
    )
  }
  )
  
  output$depot_agg_select <- renderUI({
    if (is.null(events())) {
      return(NULL)
    }
    # Depot/Field can only be disaggregated when Event Label is agreggated
    checkboxInput("depot_agg", label = "Aggregate", value = TRUE)
  })
  
  output$depot_agg_select_helptext <- renderUI({
    selected_num <- which(values$selected_agg_order[1:factor_size] == "depot")
    # if doesnt exist in selected list then selected_num will be integer(), i.e. a zero-length integer
    
    HTML(GenerateAggCheckboxAnnotation("Level", 
                                       ifelse(length(selected_num) == 0, '', 
                                              factor_selection_order_map[[as.character(selected_num)]])
    ))
  })
  
  output$depot_select <- renderUI({
    if (is.null(events()) || is.null(input$depot_agg) || input$depot_agg) {
      return(NULL)
    }
    
    tags$div(class = "well", class = "well-shiny-option",
             checkboxGroupInput("depot_selection", label = "Maintenance Level", 
                                choices = c("Depot", "Field"),
                                selected = c("Depot", "Field"))
    )
  }
  )
  
  # Return either NULL (no plot or loading) or a plot
  output$selected_plot <- renderPlot(expr = {
    return(final_plot())
  })
  
  # Downloads ---------------------------------------------------------------  
  
  output$dl_filtered_data <- downloadHandler(
    # Return the filtered data set with all columns and as they appear in the dataset (w/o Null to None rendering)
    filename = 'filtered_events.csv',
    content = function(file) {
      write.csv(
        x = values$events_filtered_adj,
        file = file, na = "", row.names = FALSE)
    }
  )
  
  output$dl_aggregated_data <- downloadHandler(
    # Return the filtered data set with all columns and as they appear in the dataset (w/o Null to None rendering)
    filename = 'aggregated_events.csv',
    content = function(file) {
      write.csv(
        x = if(!is.null(final_plot()$data)){
          final_plot()$data
        } else {
          "Data Loading. Try Again"
        }, 
        file = file, row.names = FALSE)
    }
  )
  
  output$dl_selected_data <- downloadHandler(
    # Return the selected data (subset of filtered data) with subset of columns - as appears in displayed data table
    filename = 'selected_events.csv',
    content = function(file) {
      write.csv(
        x = if(!is.null(values$nearest_events)){
          values$nearest_events
        } else {
          "Data Loading. Try Again"
        }, 
        file = file, row.names = FALSE)
    }
  )
  
  output$dl_plot_png <- downloadHandler(
    filename = function() { paste0("events_plot", ".png") },
    content = function(file) {
      ggsave(file, plot = final_plot(), device = "png", height = 7, width = 7 * 2.25) # dimensions are a swing in the dim light
    }
  )
  
  # Events Table -----------------------------------------------
  
  output$source_events_table <- renderDataTable(expr = {
    # nearest events table
    if(nrow(values$nearest_events)==0) {
      return(NULL)
    }
    to_return <- values$nearest_events
    names(to_return) <- MakeTitleCase(names(to_return)) # remove underscores, except for narrative fields
    names(to_return)[names(to_return) == "Discrepancy Narrative"] <- "Discrepancy_Narrative"
    names(to_return)[names(to_return) == "Corrective Narrative"] <- "Corrective_Narrative"
    names(to_return)[names(to_return) == "Work Center Event Narrative"] <- "Work_Center_Event_Narrative"
    return(to_return)
  },
  # Data Table Params
  options=list(lengthMenu = list(c(5, 15, 25, 50, 75, 100), c('5', '10', '25', '50', '75', '100')),
               scrollX=TRUE, scrollY="450px", scrollCollapse=TRUE)
  )
  
  # Clean up ----------------------------------------------------

  # remove connection upon app restart or disconnect
  session$onSessionEnded(function(){
    # observe never returns anything. it must be used to access conn()
    observe(dbDisconnect(conn()))
  })
  
}
)

