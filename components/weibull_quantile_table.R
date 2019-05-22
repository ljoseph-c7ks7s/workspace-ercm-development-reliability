fn <- function(conn_rmysql, load_path, params_path, component_path, output_file) {
  # Clockwork Solutions Confidential & Proprietary
  # Copyright 2019
  
  # Script calculates weibull for all intervals and saves confidence bounds for 
  #   > user-specificed confidence limits
  #   > pre-defined quantiles: 0.001, 0.01, 0.02, .., 0.99, 0.999
  
  suppressPackageStartupMessages(library(jsonlite))
  suppressPackageStartupMessages(library(dplyr))
  suppressPackageStartupMessages(library(purrr))
  suppressPackageStartupMessages(library(tidyr))
  suppressPackageStartupMessages(library(flexsurv))
  suppressPackageStartupMessages(library(RMySQL))
  
  
  # Figure out the Studio component name, to which results will be written
  # see https://clockwork.atlassian.net/browse/PH-1207
  s_output_table <- ifelse(Sys.info()["sysname"] == "Windows", 
                           strsplit(params_path, "\\\\"),
                           strsplit(params_path, "/")) %>%
    unlist() %>% 
    last() %>% 
    sub("\\.json", "", .)
  
  r_component_attributes <- fromJSON(params_path)
  if (!is.null(r_component_attributes[["alpha"]])) {
    alpha = r_component_attributes[["alpha"]]
  } else {
    alpha = 0.05 # default is 0.05 for 95% CIs
  }
  if (!is.null(r_component_attributes[["min_interval_time"]])) {
    min_interval_time = r_component_attributes[["min_interval_time"]]
  } else {
    min_interval_time = 1.0 # default is 1
  }
  
  df <- dbGetQuery(conn_rmysql, paste("SELECT rd.id distribution_id, dt.name dist_type, i.interval_value, i.causal FROM 
    reliability_distribution rd
        JOIN
	distribution_type dt ON dt.id = rd.distribution_type_id
        JOIN
    classify_distributions cd ON cd.distribution_id = rd.id
        JOIN
    reliability_interval_map rim ON rim.base_interval_parameter_set_id = rd.interval_parameter_set_id
        JOIN
    `interval` i ON rim.includes_interval_parameter_set_id = i.interval_parameter_set_id 
        WHERE i.interval_value >=", min_interval_time)) %>% 
    as_tibble()
  
  return_ci_table <- function(df, distribution_id, dist_type, alpha){
  
    df_for_fits <- Surv(df$interval_value, df$causal)
    
    single_fit <- flexsurvreg(df_for_fits ~ 1, dist=dist_type)
      
    
    print(single_fit)
    
    # Calculate time/TOW confidence intervals for each quantile - horizontal CIs
    df_ci_tow <- single_fit %>% summary(type="quantile", 
                                          quantiles=c(0.1, seq(1,99), 99.9)/100, 
                                          tidy=TRUE, 
                                          cl=(1-alpha),
                                          B=25000) %>%
      mutate_at(2:4, round, 2) %>%
      rename(time=est) %>%
      mutate(type="tow_ci")
    
    # calculate quantile confidence intervals for each TOW, calulated above, except TOWs for first(0.001) and last (.999) quantiles
    df_ci_qntl <- single_fit %>% summary(type="survival", 
                                           t=df_ci_tow$time[2:(nrow(df_ci_tow)-1)], 
                                           tidy=TRUE, 
                                           B=25000) %>%
      mutate_at(2:4, round, 5) %>%
      # convert from Survival curve to CDF (unreliability)
      # first swap ucl and lcl
      rename(quantile=est,
             uppercl=lcl,
             lcl=ucl) %>% 
      rename(ucl=uppercl) %>%
      mutate_at(2:4, Vectorize(function(x)1-x)) %>%
      mutate(type="quantile_ci")
    
    return(bind_rows(df_ci_tow, df_ci_qntl))
  }
  
  to_return <- nest(df %>% group_by(distribution_id, dist_type)) %>%
    mutate(quantiles = purrr::pmap(list(data, distribution_id, dist_type, alpha), .f=return_ci_table)) %>%
    select(-data, -dist_type) %>% unnest()
  
  RMySQL::dbWriteTable(conn_rmysql, name=s_output_table, 
                       value=to_return, 
                       overwrite=FALSE, 
                       append=TRUE, 
                       row.names=FALSE)
}

# fn <- Vectorize(function(x) log(-log(1-x)))
# seq_weib <- c(0.001, 0.003, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.96, 0.99, 0.999)
# ggplot(to_return %>% filter(type=="tow_ci")) + geom_line(aes(x=time, y=fn(quantile))) +
#   geom_line(aes(x=lcl, y=fn(quantile)), colour="blue", linetype=2) +
#   geom_line(aes(x=ucl, y=fn(quantile)), colour="red", linetype=2) +
#   scale_x_log10() +
#   scale_y_continuous(name="Unreliability", breaks = log(-log(1-seq_weib)), labels=seq_weib)
# ggplot(to_return %>% filter(type=="quantile_ci")) + geom_line(aes(x=time, y=fn(quantile))) +
#   geom_line(aes(x=time, y=fn(lcl)), colour="blue", linetype=2) +
#   geom_line(aes(x=time, y=fn(ucl)), colour="red", linetype=2) +
#   scale_x_log10() +
#   scale_y_continuous(name="Unreliability", breaks = log(-log(1-seq_weib)), labels=seq_weib)
