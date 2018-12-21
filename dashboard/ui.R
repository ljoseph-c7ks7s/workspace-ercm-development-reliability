
body <- dashboardBody(

  useShinyjs(), # intialize shiny js
  
  tags$link(rel = "stylesheet", type = "text/css", href = "custom.css"),
  
  fluidRow(
      column(width=3,box(width = NULL, collapsible = FALSE, solidHeader = FALSE, status = "primary", title = NULL, class = "input-super-box",
             box(width = NULL, collapsible = TRUE, solidHeader = TRUE, status = "primary",
                 title = "Select Plot Options", 
                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary", 
                     title = "Plot Type & Granularity",
                   tags$div(class = "well", class = "well-shiny-option",
                     #radioButtons("plot_type", label = NULL, 
                     #             choices = c("Time Dependent", "Time between Event", "Pareto"), 
                     #             selected = "Pareto")
                     HTML('
<div id="plot_type" class="form-group shiny-input-radiogroup shiny-input-container">
  <div class="shiny-options-group">
    <div class="radio">
      <label>
        <input type="radio" name="plot_type" value="Time Dependent"/>
          <span>Time Dependent</span>
      </label>
        <div class = "pull-right">
          <a class="loc_type_info" data-toggle="tooltip" data-placement="left" title="Events recorded on a day, or within that Time Period - e.g. month - starting that day">
            <span id="custom-info" class="glyphicon dropdown-toggle glyphicon-info-sign-sm info">
            </span>
          </a>
        </div>
    </div>
    <div class="radio">
      <label>
        <input type="radio" name="plot_type" value="Time between Event"/>
          <span>Time between Event</span>
      </label>
        <div class = "pull-right">
          <a class="loc_type_info" data-toggle="tooltip" data-placement="left" title="Days or other Time Period between event-days (days with at least one event with the specified classifications)
for each aircraft serial number.  If serial number is not disaggregated, then this metric displays the average across the serial numbers matching the specifications.
Calculated as (Days / Event Count), where Days is days assigned to specific location if data is disaggregated across Assigned Locations and total assigned days to any location otherwise">
            <span id="custom-info" class="glyphicon dropdown-toggle glyphicon-info-sign-sm info">
            </span>
          </a>
        </div>
    </div>
    <div class="radio">
      <label>
        <input type="radio" name="plot_type" value="Pareto" checked="checked"/>
          <span>Pareto</span>
      </label>
        <div class = "pull-right">
          <a class="loc_type_info" data-toggle="tooltip" data-placement="left" title="Count of events for the specified classification">
            <span id="custom-info" class="glyphicon dropdown-toggle glyphicon-info-sign-sm info">
            </span>
          </a>
        </div>
    </div>
  </div>
</div>')
                     ),
                   uiOutput("time_dependent_group")
                   ),
                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary", 
                     title = "Normalization and Styling Options",
                     uiOutput("normalize_control"),
                     tags$div(class = "well", class = "well-shiny-option",
                              checkboxInput("sort_by_severity", label = "Sort Pareto by Location Severity Index", value = FALSE),
                              checkboxInput("pareto_labels", label = "Pareto Annotations", value = TRUE)),
                     tags$div(class = "well", class = "well-shiny-option",
                              checkboxInput("names_not_codes", label = "Display Names Instead of Codes", value = FALSE),
                              uiOutput("which_labels_select")
                     )
                 ),
                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary", title = "Misc. Options", 
                     uiOutput("top_n_select")
                 )
             ),
             # TODO make the selection UIs data-driven with modularized code - http://shiny.rstudio.com/articles/modules.html
             # consider a table within a panel instead of boxes within box
             box(width = NULL, collapsible = TRUE, solidHeader = TRUE, status = "primary",
                 title = "Select Filtering", 
                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary", 
                     title = "Location", 
                     tags$div(class = "well", class = "well-shiny-option",
                              HTML(paste('<div style="display: inline-block; width: 100%">', 
                                         uiOutput("loc_agg_select", class = "agg-checkbox"), 
                                         uiOutput("loc_agg_select_helptext", class = "selected-order"), '</div>'
                                         )
                              )),
                     uiOutput("loc_type_select"),
                     uiOutput("loc_select")),
                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary",
                     title = "Serial Number",
                     tags$div(class = "well", class = "well-shiny-option",
                              HTML(paste('<div style="display: inline-block; width: 100%">', 
                                         uiOutput("sn_agg_select", class = "agg-checkbox"), 
                                         uiOutput("sn_agg_select_helptext", class = "selected-order"), '</div>')
                              )),
                     uiOutput("sn_select")),

                 box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary",
                    title = "Work Unit Code",
                    tags$div(class = "well", class = "well-shiny-option",
                             HTML(paste('<div style="display: inline-block; width: 100%">', 
                                        uiOutput("wuc_agg_select", class = "agg-checkbox"), 
                                        uiOutput("wuc_agg_select_helptext", class = "selected-order"), '</div>')
                             )),
                    uiOutput("wuc_type_select"),
                    uiOutput("wuc_select")),
                    # Event Label filter is here for the final dashboard
                box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary",
                    title = "Event Label",
                    tags$div(class = "well", class = "well-shiny-option",
                             HTML(paste('<div style="display: inline-block; width: 100%">', 
                                        uiOutput("label_agg_select", class = "agg-checkbox"),
                                        uiOutput("label_agg_select_helptext", class = "selected-order"), '</div>'
                             )
                    )),
                    uiOutput("label_select", class = "checkbox-filter-group")),
                box(width = NULL, collapsible = TRUE, solidHeader = FALSE, status = "primary",
                    title = "Maintenance Level",
                    tags$div(class = "well", class = "well-shiny-option",
                             HTML(paste('<div style="display: inline-block; width: 100%">', 
                                        uiOutput("depot_agg_select", class = "agg-checkbox"),
                                        uiOutput("depot_agg_select_helptext", class = "selected-order"), '</div>'
                    ))),
                    uiOutput("depot_select", class = "checkbox-filter-group"))
                    ))
                ),
      column(width = 9, 
             box(width=NULL, collapsible = FALSE, solidHeader = TRUE, status = "primary",
                 title = "Events", height = "600px",
               plotOutput("selected_plot", click = "plot_click", height = "500px"))
             )
),
fluidRow(
  column(width = 3,
                box(width=NULL, collapsible = FALSE, solidHeader = FALSE, status = "primary",
                title = "Update Control", height = NULL,
                tags$span(style = "width: 100%",
                  # checkbox - checkboxInput("autorefresh_plot", label = "Auto Update", value = TRUE)
                  HTML('
                    <div class="form-group shiny-input-container", style = "display:inline">
                      <div class="checkbox", style = "display:inline">
                      <label>
                      <input id="autorefresh_plot" type="checkbox" checked="checked"/>
                      <span>Auto Update</span>
                      </label>
                      </div>
                      </div>'
                  ),
                  #actionButton("refresh_plot", "Update Plot")
                  HTML('<button id="refresh_plot_action" type="button" class="btn btn-default action-button" 
                       style = "margin-left:18px">Update Plot</button> ')
                ))),
         column(width = 9,
             box(width=NULL, collapsible = FALSE, solidHeader = FALSE, status = "primary",
                 title = "Downloads", height = NULL,
                 # inline download buttons with tooltips
                 tags$span(#downloadButton("dl_filtered_data", label = "Filtered Dataset"),
                           #downloadButton("dl_aggregated_data", label = "Aggregated Dataset"),
                           #downloadButton("dl_selected_data", label = "Selected Dataset"),
                           #downloadButton("dl_plot_png", label = "Plot Image")))
                   HTML('<a id="dl_filtered_data" class="btn btn-default shiny-download-link " href="" target="_blank"
                        data-toggle="tooltip" data-placement="bottom" title="Raw data filtered from checkbox selections">
                        <i class="glyphicon glyphicon-download-alt"></i>
                        Filtered Data
                        </a>'),
                   HTML('<a id="dl_aggregated_data" class="btn btn-default shiny-download-link " href="" target="_blank"
                        data-toggle="tooltip" data-placement="bottom" title="Aggregated data filtered from checkbox selections">
                        <i class="glyphicon glyphicon-download-alt"></i>
                        Aggregated Data
                        </a>'),
                   HTML('<a id="dl_selected_data" class="btn btn-default shiny-download-link " href="" target="_blank"
                        data-toggle="tooltip" data-placement="bottom" title="Raw data filtered from plot click selection with subset of fields (as in table)">
                        <i class="glyphicon glyphicon-download-alt"></i>
                        Selected Data
                        </a>'),
                   HTML('<a id="dl_plot_png" class="btn btn-default shiny-download-link " href="" target="_blank"
                        data-toggle="tooltip" data-placement="bottom" title="Image (png) of plot">
                        <i class="glyphicon glyphicon-download-alt"></i>
                        Plot Image
                        </a>')
                   ))
         )
),
fluidRow(column(width=12,
                box(width=NULL, collapsible = TRUE, solidHeader = TRUE, status = "primary",
                    title = "Selected Events",
                  dataTableOutput("source_events_table")
                )
                )
         )
     
)

shinyUI(
dashboardPage(
  dashboardHeader(disable = TRUE),
  dashboardSidebar(disable = TRUE),
  body
)
)