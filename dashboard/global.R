suppressPackageStartupMessages(library(shinydashboard, quietly = TRUE)) # dashboard
suppressPackageStartupMessages(library(shinyjs, quietly = TRUE)) # toggle UI options
suppressPackageStartupMessages(library(tools, quietly = TRUE)) # text formatting

GracefulQuery <- function(conn, qry, msg = "Database Tables do not Exist - Please Run Component") {
  tryCatch(expr = dbGetQuery(conn, qry),
           error = function(e) {
             message("Database Tables do not Exist - Please Run Component")
             return(NULL)
           })
}

# for empty ggplot
# credit http://docs.ggplot2.org/dev/vignettes/themes.html
theme_nothing <- function(base_size = 12, base_family = "Helvetica")
{
  theme_bw(base_size = base_size, base_family = base_family)
    theme(
      rect             = element_blank(),
      line             = element_blank(),
      text             = element_blank()
    )
}

# format data-y field names into printing english
MakeTitleCase <- function(st) {
  st <- gsub("_"," ", st)
  st <- gsub("\\."," ", st)
  st <- toTitleCase(st)
  return(st)
}

ChangeNAtoNone <- function(df, field_name){
  # Sets NA (missing data) into the string NULL for a single field in a data frame
  # Args
  #   df, a data frame
  #   field_name, a field name string
  # Returns: the DF with adjusted field
  if (sum(is.na(select_(df, field_name))) > 0) {
    #to_return$Performing_Location[is.na(to_return$Performing_Location)] <- "None"
    df[, field_name] <- ifelse(is.na(df[, field_name]), "None", df[, field_name])
  }
  return(df)
}

SelectProperLocationName <- function(single_factor, loc_type, loc_selection, loc_type_field_name){
  if(single_factor == "Location"){
      if(is.null(loc_selection)){
        # if the location selection checkbox group is still loading then don't show a plot
        return(NULL)
      }
      return(loc_type_field_name)
  } else {
    # not location
    return(single_factor)
  }
}

Df2Vr <- function(df){
  # df a 1-column data frame or tbl_df
  # returns a vector with no names
  return(df %>% unlist() %>% unname())
}

GenerateAggCheckboxAnnotation <- function(factor_type_long, selected_text){
  paste0('
         <div class="selected-order">
         <a class="define-metric" data-toggle="tooltip" data-placement="top" title="',factor_type_long, 
         ' selections affect available choices for factor groups disaggregated after ', factor_type_long, '">',
         selected_text,
         '</div>
         </div>
         </div>')
}


GenerateNormalizationOptionsWithTooltip <- function(option_list){
  options_html <- ""
  for(ii in option_list) {
    options_html <- paste0(options_html, '<div class="radio">
             <label>
             <input type="radio" name="normalize_option" value="', ii, '"/>
             <span>', ii, '</span>
             </label>
             </div>')
  }

  HTML(paste0('
       <div class="well well-shiny-option">
         <div id="normalize_option" class="form-group shiny-input-radiogroup shiny-input-container">
           <label class="control-label" for="normalize_option">Normalize By:
           </label>
           <div class="shiny-options-group">
             <div class="radio">
             <label>
              <input type="radio" name="normalize_option" value="None" checked="checked"/>
              <span>None</span>
              </label>
              </div>',
              options_html,'
           </div>
         </div>
       </div> 
  ')
  )
}

NormalizeMultiFactorParetoWithSN <- function(grouped_events, selected_factors, normalize_option, time_dependent_group_selection, 
                                             days_per_time, sn_loc_active_days, sn_loc_flying_hours, sn_depot_cyles){
  # Used to simplify calculations in multi-factor pareto calculations
  if(normalize_option == "Time Period & Assigned Aircraft"){
    # if location is chosen then use Loc days/flight-hours fields. otherwise use totals
    grouped_events <- AggregateForParetoNormalization(selected_factors, grouped_events, "Asgn_Days", 
                                                      sn_loc_active_days, sn_loc_flying_hours, sn_depot_cyles)
    # Adjust for time period
    grouped_events$actions <- grouped_events$actions * days_per_time[[time_dependent_group_selection]]
    if("Serial_Number" %in% selected_factors){
      y_label <- paste0("Events Per ", time_dependent_group_selection, "\n")
    } else {
      y_label <- paste0("Events Per Aircraft Per ", time_dependent_group_selection, "\n")
    }
    round_num <- 2
  } else if(normalize_option == "Flying Hours"){
    # if location is chosen then use Loc days/flight-hours fields. otherwise use totals
    grouped_events <- AggregateForParetoNormalization(selected_factors, grouped_events, "Flying_Hours", 
                                                      sn_loc_active_days, sn_loc_flying_hours, sn_depot_cyles)
    y_label <- "Events Per Flight Hour\n"
    round_num <- 4
  } else if(normalize_option == "Depot Cycles"){
    # use depot cycles whether location is selected or not
    grouped_events <- AggregateForParetoNormalization(selected_factors, grouped_events, "Depot_Cycles", 
                                                      sn_loc_active_days, sn_loc_flying_hours, sn_depot_cyles)
    y_label <- "Events Per Depot Cycle (min. 1 per aircraft)\n"
    round_num <- 2
  } else {
    stop("unknown normalization option")
  }
  return(list("grouped_events" = grouped_events, "y_label" = y_label, "round_num" = round_num))
}

AggregateForParetoNormalization <- function(selected_factors, grouped_events, normalize_option, 
                                            sn_loc_active_days, sn_loc_flying_hours, sn_depot_cycles){
  # Used to simplify calculations in multi-factor pareto calculations
  #  splits by SN even if it's not in selected factors
  #  called by previous
  
  add_ending <- TRUE
  # distinguish between assigned aircraft-days and flying hours and depot cycles
  if(normalize_option == "Asgn_Days"){
    stem <- "Days_SN_Asgn_"
    days_or_hours_per_sn <- sn_loc_active_days()
  } else if(normalize_option == "Flying_Hours"){
    stem <- "Fly_Hours_SN_"
    days_or_hours_per_sn <- sn_loc_flying_hours()
  } else if (normalize_option == "Depot_Cycles"){
    stem <- "SN_Depot_Cycles"
    add_ending <- FALSE
    days_or_hours_per_sn <- sn_depot_cycles()
  }
  
  # will explicitly break out by SN so remove it if it's included in selected factors
  if("Serial_Number" %in% selected_factors){
    selected_factors <- selected_factors[-which(selected_factors == "Serial_Number")]
  }
  if(any(grepl(pattern = "Assigned_Location", x = selected_factors))){
    # make new variable, loc_factor, which could either be assigned_location or assigned_location_name
    loc_factor <- selected_factors[which(grepl(pattern = "Assigned_Location", x = selected_factors))]
    divi <- if(add_ending) paste0(stem, "Loc") else stem
    return(
      grouped_events %>% group_by_("Serial_Number", .dots = selected_factors) %>% summarise(actions = n()) %>%
        inner_join(
          days_or_hours_per_sn %>% select_("Serial_Number", loc_factor, divi),
          by = c("Serial_Number", loc_factor)) %>% mutate_("actions" = paste0("actions/", divi)) %>%
                                                          # Standard Eval requires quote of entire expression
        filter(actions < Inf) # remove any groups of data with zero flight hours
    )
  } else {
    # No Location. use total and ignore location
    divi <- if(add_ending) paste0(stem,"Tot") else stem
    return(
      grouped_events %>% group_by_("Serial_Number", .dots = selected_factors) %>% summarise(actions = n()) %>%
        inner_join(
          days_or_hours_per_sn %>% select_("Serial_Number", divi) %>% distinct(),
          by = "Serial_Number") %>% 
        # remove any groups of data with NA assigned time or hours or no serial number
        filter_(!is.na(divi), "Serial_Number" != "None") %>% 
        # calculate normalized quantity for each group of data
        mutate_("actions" = paste0("actions/", divi)) %>%
        filter(actions < Inf) # remove any groups of data with zero flight hours
    )
  }
}

AdjustAFactorForParameters <- function(single_factor, names_not_codes, which_labels, wuc_type, loc_agg){
  ## Use a different WUC or Location for plot labels, depending on configuration
  if(single_factor == "Work_Unit_Code"){
    if(names_not_codes && ("Work Unit Code" %in% which_labels) && wuc_type == "five"){
      return("WUC_Narrative")
    } else {
      return("reduced_wuc")
    }
  } else if(grepl("Location", single_factor) && names_not_codes && ("Location" %in% which_labels) && !loc_agg){
    return(paste0(single_factor, "_Name"))
  }
  return(single_factor)
}

# function for removing negative labels to pass to scale_y_continuous
RemoveNegativeLabels <- function(labels){
  ifelse(labels >= 0, labels, "")
}

# return the number of digits to pass to the round function to get 2ish digits
FindDigitsToRound <- function(x, n = 0){
  if(x >= 10){
    return(n)
  } else {
    if(x >= 1){
      return(n + 1)
    } else {
      FindDigitsToRound(x*10, n + 1)
    }
  }
}
