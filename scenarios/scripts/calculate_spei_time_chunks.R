# Goal ------------------------------------------------------------------####

# Calculate SPEI for all Russian River scenarios



# Working directory --------------------------------------------------------####

# set script directory
script_dir <- 'C:/work/projects/russian_river/model/RR_GSFLOW/GSFLOW/scripts/'

# set input directory
input_dir <- 'C:/work/projects/russian_river/model/RR_GSFLOW/GSFLOW/scripts/inputs_for_scripts/spei_inputs/'

# set output directory
output_dir <- 'C:/work/projects/russian_river/model/RR_GSFLOW/GSFLOW/scripts/script_outputs/spei_outputs/'

  
  
  
# Packages ----------------------------------------------------------------####

# # install packages
# install.packages('tidyverse')
# install.packages('dplyr')
# install.packages('SPEI')
# install.packages('accelerometry')

# load
library(tidyverse) 
library(lubridate)
library(readr)
library(dplyr)
library(tidyr)
library(SPEI)
library(accelerometry)



# Set model folders and files ----------------------------------------------------------------####

# set model folders
historical_baseline_folder <- paste0(input_dir, 'historical/hist_baseline/')
historical_unimpaired_folder <- paste0(input_dir, 'historical/hist_unimpaired/')  
historical_frost_folder <- paste0(input_dir, 'historical/hist_frost/')  
historical_baseline_modsim_folder <- paste0(input_dir, 'historical/hist_baseline_modsim/')    
historical_pv1_modsim_folder <- paste0(input_dir, 'historical/hist_pv1_modsim/')  
historical_pv2_modsim_folder <- paste0(input_dir, 'historical/hist_pv2_modsim/') 
CanESM2_rcp45_folder <- paste0(input_dir, 'future/CanESM2_rcp45/')      
CanESM2_rcp85_folder <- paste0(input_dir, 'future/CanESM2_rcp85/') 
CNRMCM5_rcp45_folder <- paste0(input_dir, 'future/CNRM-CM5_rcp45/') 
CNRMCM5_rcp85_folder <- paste0(input_dir, 'future/CNRM-CM5_rcp85/') 
HADGEM2ES_rcp45_folder <- paste0(input_dir, 'future/HADGEM2-ES_rcp45/')
HADGEM2ES_rcp85_folder <- paste0(input_dir, 'future/HADGEM2-ES_rcp85/') 
MIROC5_rcp45_folder <- paste0(input_dir, 'future/MIROC5_rcp45/') 
MIROC5_rcp85_folder <- paste0(input_dir, 'future/MIROC5_rcp85/')   

# place model folders in list
model_folders_list <- list(
  #historical_baseline_folder,
  #historical_unimpaired_folder,
  # historical_frost_folder,
  #historical_baseline_modsim_folder,
  #historical_pv1_modsim_folder,
  #historical_pv2_modsim_folder,
  CanESM2_rcp45_folder,
  CanESM2_rcp85_folder,
  CNRMCM5_rcp45_folder,
  CNRMCM5_rcp85_folder,
  HADGEM2ES_rcp45_folder,
  HADGEM2ES_rcp85_folder,
  MIROC5_rcp45_folder,
  MIROC5_rcp85_folder
)


# set model names
model_names <- list(
  #'hist_baseline',
  #'hist_unimpaired',
  # 'hist_frost',
  #'hist_baseline_modsim',
  #'hist_pv1_modsim',
  #'hist_pv2_modsim',
  'CanESM2_rcp45',
  'CanESM2_rcp85',
  'CNRM-CM5_rcp45',
  'CNRM-CM5_rcp85',
  'HADGEM2-ES_rcp45',
  'HADGEM2-ES_rcp85',
  'MIROC5_rcp45',
  'MIROC5_rcp85'
)


# set climate change scenario model names
model_names_cc <- list(
  'CanESM2_rcp45',
  'CanESM2_rcp85',
  'CNRM-CM5_rcp45',
  'CNRM-CM5_rcp85',
  'HADGEM2-ES_rcp45',
  'HADGEM2-ES_rcp85',
  'MIROC5_rcp45',
  'MIROC5_rcp85'
)


# set model names pretty
model_names_pretty <- list(
  #'hist-baseline',
  #'hist-unimpaired',
  # 'hist-frost',
  #'hist-baseline-modsim',
  #'hist-pv1-modsim',
  #'hist-pv2-modsim',
  'CanESM2-rcp45',
  'CanESM2-rcp85',
  'CNRM-CM5-rcp45',
  'CNRM-CM5-rcp85',
  'HADGEM2-ES-rcp45',
  'HADGEM2-ES-rcp85',
  'MIROC5-rcp45',
  'MIROC5-rcp85'
)


# set file names
hru_ppt_file <- 'nsub_hru_ppt.csv'
nsub_potet_file <- 'nsub_potet.csv'



# Set constants ----------------------------------------------------------------####

# units conversion
mm_per_inch <- 25.4

# set historical and future indices
min_hist <- as_date('1990-01-01')
max_hist <- as_date('2015-12-31')
min_future <- as_date('2016-01-01')
max_future <- as_date('2099-12-31')

# set max number of consecutive non-drought months to remove (and still consider part of a drought)
max_num_nondrought_months <- 12



# Read in and reformat ----------------------------------------------------------------####

precip_potet_hist_list <- list()
precip_potet_future_list <- list()
for (i in 1:length(model_names)){
  
  # extract
  model_folder <- model_folders_list[[i]]
  model_name <- model_names[[i]]
  model_name_pretty <- model_names_pretty[[i]]
  
  # read in precip file
  file_path <- paste0(model_folder, hru_ppt_file)
  precip <- read_csv(file_path)
  
  # read in potet file
  file_path <- paste0(model_folder, nsub_potet_file)
  potet <- read_csv(file_path)
  
  # sum over watershed
  precip['precip'] <- rowSums(precip[,(2:ncol(precip))])
  potet['potet'] <- rowSums(potet[,(2:ncol(potet))])
  
  # place precip and potet in data frame together
  precip <- precip[,c('Date', 'precip')]
  potet <- potet[,c('Date', 'potet')]
  precip_potet <- left_join(precip, potet, by="Date")
  
  # convert units from inches to mm
  precip_potet['precip'] <- precip_potet['precip'] * mm_per_inch
  precip_potet['potet'] <- precip_potet['potet'] * mm_per_inch
  
  # add month and year columns
  precip_potet$year <- year(precip_potet$Date)
  precip_potet$month <- month(precip_potet$Date)
  
  # separate into historical and future chunks
  mask_hist <- (precip_potet[['Date']] >= min_hist) & (precip_potet[['Date']] <= max_hist)
  precip_potet_hist <- precip_potet[mask_hist,]
  
  mask_future <- (precip_potet[['Date']] >= min_future) & (precip_potet[['Date']] <= max_future)
  precip_potet_future <- precip_potet[mask_future,]
  
  
  # sum by month-year
  precip_potet_hist <- precip_potet_hist %>%
    group_by(year, month) %>%
    summarise(precip = sum(precip),
              potet = sum(potet))
  precip_potet_future <- precip_potet_future %>%
    group_by(year, month) %>%
    summarise(precip = sum(precip),
              potet = sum(potet))
  
  # calculate climatic water balance as precip minus potet
  precip_potet_hist$cwb <- precip_potet_hist$precip - precip_potet_hist$potet
  precip_potet_future$cwb <- precip_potet_future$precip - precip_potet_future$potet
  
  # add column for model name
  precip_potet_hist$model_name <- model_name
  precip_potet_future$model_name <- model_name
  
  # store data frame in list
  precip_potet_hist_list[[i]] <- precip_potet_hist
  precip_potet_future_list[[i]] <- precip_potet_future
  
  
}

# combine all data frames into one
precip_potet_hist_df <- bind_rows(precip_potet_hist_list)
precip_potet_future_df <- bind_rows(precip_potet_future_list)


# export
file_path <- paste0(output_dir, 'precip_potet_hist_cwb.csv')
write.csv(precip_potet_hist_df, file = file_path, row.names=FALSE)

file_path <- paste0(output_dir, 'precip_potet_future_cwb.csv')
write.csv(precip_potet_future_df, file = file_path, row.names=FALSE)





# Calculate SPEI ----------------------------------------------------------------####


# remove precip and potet data
precip_potet_hist_df <- precip_potet_hist_df[,c('model_name', 'year', 'month', 'cwb')]
precip_potet_future_df <- precip_potet_future_df[,c('model_name', 'year', 'month', 'cwb')]


# convert to wide format with one column per model
precip_potet_hist_df = precip_potet_hist_df %>% 
  pivot_wider(names_from=c(model_name), values_from=cwb)
precip_potet_future_df = precip_potet_future_df %>% 
  pivot_wider(names_from=c(model_name), values_from=cwb)


# remove year and month columns
precip_potet_hist_df_old <- precip_potet_hist_df
precip_potet_hist_df <- subset(precip_potet_hist_df, select = -c(year, month))

precip_potet_future_df_old <- precip_potet_future_df
precip_potet_future_df <- subset(precip_potet_future_df, select = -c(year, month))


# calculate SPEI
spei_3months_hist <- spei(as.matrix(precip_potet_hist_df),3)
# spei_6months_hist <- spei(as.matrix(precip_potet_hist_df),6)
# spei_9months_hist <- spei(as.matrix(precip_potet_hist_df),9)
# spei_12months_hist <- spei(as.matrix(precip_potet_hist_df),12)
# spei_60months_hist <- spei(as.matrix(precip_potet_hist_df),60)

spei_3months_future <- spei(as.matrix(precip_potet_future_df),3)
# spei_6months_future <- spei(as.matrix(precip_potet_future_df),6)
# spei_9months_future <- spei(as.matrix(precip_potet_future_df),9)
# spei_12months_future <- spei(as.matrix(precip_potet_future_df),12)
# spei_60months_future <- spei(as.matrix(precip_potet_future_df),60)




# Define SPEI plotting functions ----------------------------------------------------------------####

spei_plotting_function <- function(spei_output, precip_potet_df_old, output_file_name, plot_title){
  
  # reformat
  spei_df <- data.frame(spei_output$fitted)
  spei_df$year <- precip_potet_df_old$year
  spei_df$month <- precip_potet_df_old$month
  spei_df$date <- paste(spei_df$month, '-', spei_df$year) 
  spei_df$date <- my(spei_df$date)
  
  # export
  file_path <- paste0(output_dir, output_file_name, '.csv')
  write.csv(spei_df, file_path, row.names=FALSE)
  
  # reformat
  spei_df <- spei_df %>% 
    pivot_longer(
      cols = !c('date', 'year', 'month'), 
      names_to = "scenario",
      values_to = "SPEI"
    ) %>%
    dplyr::mutate(sign = ifelse(SPEI >= 0, "pos", "neg"))
  
  # plot
  this_plot <- ggplot(spei_df) +
    geom_bar(aes(x = date, y = SPEI, col = sign, fill = sign),
             show.legend = F, stat = "identity") +
    scale_color_manual(values = c("pos" = "blue", "neg" = "red")) +
    scale_fill_manual(values = c("pos"  = "blue", "neg" = "red")) +
    scale_y_continuous(limits = c(-3, 3),
                       breaks = -3:3) +
    ylab("SPEI") + 
    ggtitle(plot_title) +
    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) + 
    facet_wrap(vars(scenario), ncol=1)
  
  # export plot
  file_path <- paste0(output_dir, output_file_name, '.png')
  ggsave(
    filename = file_path,
    plot = this_plot,
    device = 'png',
    width = 8,
    height = 11,
    units = 'in'
  )
}





spei_plotting_function_combine_hist_and_future <- function(spei_output_hist, spei_output_future, precip_potet_hist_df_old, precip_potet_future_df_old, output_file_name, plot_title){
  
  # reformat hist
  spei_df_hist <- data.frame(spei_output_hist$fitted)
  spei_df_hist$year <- precip_potet_hist_df_old$year
  spei_df_hist$month <- precip_potet_hist_df_old$month
  spei_df_hist$date <- paste(spei_df_hist$month, '-', spei_df_hist$year) 
  spei_df_hist$date <- my(spei_df_hist$date)
  
  # reformat future
  spei_df_future <- data.frame(spei_output_future$fitted)
  spei_df_future$year <- precip_potet_future_df_old$year
  spei_df_future$month <- precip_potet_future_df_old$month
  spei_df_future$date <- paste(spei_df_future$month, '-', spei_df_future$year) 
  spei_df_future$date <- my(spei_df_future$date)
  
  # combine hist and future
  spei_df <- rbind(spei_df_hist, spei_df_future)
  
  # export
  file_path <- paste0(output_dir, output_file_name, '.csv')
  write.csv(spei_df, file_path, row.names=FALSE)
  
  # reformat
  spei_df <- spei_df %>% 
    pivot_longer(
      cols = !c('date', 'year', 'month'), 
      names_to = "scenario",
      values_to = "SPEI"
    ) %>%
    dplyr::mutate(sign = ifelse(SPEI >= 0, "pos", "neg"))
  
  # plot
  this_plot <- ggplot(spei_df) +
    geom_bar(aes(x = date, y = SPEI, col = sign, fill = sign),
             show.legend = F, stat = "identity") +
    scale_color_manual(values = c("pos" = "blue", "neg" = "red")) +
    scale_fill_manual(values = c("pos"  = "blue", "neg" = "red")) +
    scale_y_continuous(limits = c(-3, 3),
                       breaks = -3:3) +
    ylab("SPEI") + 
    ggtitle(plot_title) +
    theme_bw() + 
    theme(plot.title = element_text(hjust = 0.5)) + 
    facet_wrap(vars(scenario), ncol=1)
  
  # export plot
  file_path <- paste0(output_dir, output_file_name, '.jpg')
  ggsave(
    filename = file_path,
    plot = this_plot,
    device = 'jpeg',
    width = 8,
    height = 11,
    units = 'in'
  )
}
  






# Plot SPEI ----------------------------------------------------------------------------####

# plot SPEI: 3 months, hist
output_file_name <- 'spei_3months_hist'
plot_title <- '3-Month SPEI: historical'
spei_plotting_function(spei_3months_hist, precip_potet_hist_df_old, output_file_name, plot_title)

# plot SPEI: 3 months, future
output_file_name <- 'spei_3months_future'
plot_title <- '3-Month SPEI: future'
spei_plotting_function(spei_3months_future, precip_potet_future_df_old, output_file_name, plot_title)

# plot SPEI: 3 months, hist and future
output_file_name <- 'spei_3months_hist_and_future'
plot_title <- '3-Month SPEI'
spei_plotting_function_combine_hist_and_future(spei_3months_hist, spei_3months_future, precip_potet_hist_df_old, precip_potet_future_df_old, output_file_name, plot_title)
  



# # plot SPEI: 6 months
# output_file_name <- 'spei_6months'
# plot_title <- '6-Month SPEI'
# spei_plotting_function(spei_6months, precip_potet_df_old, output_file_name, plot_title)
# 
# 
# # plot SPEI: 9 months
# output_file_name <- 'spei_9months'
# plot_title <- '9-Month SPEI'
# spei_plotting_function(spei_9months, precip_potet_df_old, output_file_name, plot_title)
# 
# 
# # plot SPEI: 12 months
# output_file_name <- 'spei_12months'
# plot_title <- '12-Month SPEI'
# spei_plotting_function(spei_12months, precip_potet_df_old, output_file_name, plot_title)
# 
# 
# # plot SPEI: 60 months
# output_file_name <- 'spei_60months'
# plot_title <- '60-month SPEI'
# spei_plotting_function(spei_60months, precip_potet_df_old, output_file_name, plot_title)






# # Calculate drought severity, duration, and intensity for 3-month SPEI ----------------------------------------------------------------####
# 
# 
# # note: 
# # historical period is months 1-312 for SPEI-3
# # future period is months 313-1320 for SPEI-3
# # drought defined as SPEI < -1
# # drought frequency calculated as number of times that you have drought in the time period of interest
# # drought duration calculated as number of consecutive time periods in which you have drought
# # drought severity calculated as mean of SPEI during drought periods
# 
# # identify drought periods
# drought_id = spei_3months$fitted
# mask = drought_id < -1
# drought_id[mask] <- 1
# drought_id[!mask] <- 0
# 
# # prep for drought severity
# drought_severity_prep <- spei_3months$fitted
# mask = drought_severity_prep >= -1
# drought_severity_prep[mask] <- NA
# 
# # separate hist and cc
# hist <- spei_3months$fitted[1:312,]
# hist_drought_id <- drought_id[1:312,]
# hist_drought_severity_prep <- drought_severity_prep[1:312,]
# cc <- spei_3months$fitted[313:1320,]
# cc_drought_id <- drought_id[313:1320,]
# cc_drought_severity_prep <- drought_severity_prep[313:1320,]
# 
# # calculate drought frequency (as percentage of time spent in drought)
# hist_drought_freq <- colSums(hist_drought_id, na.rm=TRUE)/nrow(hist_drought_id)
# cc_drought_freq <- colSums(cc_drought_id, na.rm=TRUE)/nrow(cc_drought_id)
# 
# # calculate drought severity
# hist_drought_severity <- apply(hist_drought_severity_prep, 2, min, na.rm=TRUE)
# cc_drought_severity <- apply(cc_drought_severity_prep, 2, min, na.rm=TRUE)
# 
# # calculate drought duration
# hist_drought_duration_list <- list()
# cc_drought_duration_list <- list()
# num_cols <- ncol(hist_drought_id)
# for (col in 1:num_cols){
#   
#   # hist
#   hist_duration <- rle(hist_drought_id[,col])
#   hist_drought_duration_list[[col]] <- hist_duration
# 
#   # cc
#   cc_duration <- rle(cc_drought_id[,col])
#   cc_drought_duration_list[[col]] <- cc_duration
#   
# }
# names(hist_drought_duration_list) <- colnames(hist_drought_id)
# names(cc_drought_duration_list) <- colnames(cc_drought_id)
# 
# # calculate longest drought duration for each scenario
# drought_duration_longest <- data.frame(matrix(NA, nrow=length(colnames(hist_drought_id)), ncol=3))
# colnames(drought_duration_longest) <- c('scenarios', 'hist', 'cc')
# drought_duration_longest$scenarios <- colnames(hist_drought_id)
# drought_duration_longest$hist <- NA
# drought_duration_longest$cc <- NA
# num_rows <- nrow(drought_duration_longest)
# for (row in 1:num_rows){
#   
#   # get scenario 
#   scenario <- drought_duration_longest$scenario[row]
#   
#   # get longest drought duration: hist
#   length <- hist_drought_duration_list[[scenario]]$length
#   value <- hist_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$hist[row] <- longest_drought
#   
#   # get longest drought duration: cc
#   length <- cc_drought_duration_list[[scenario]]$length
#   value <- cc_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$cc[row] <- longest_drought
#   
#   
# }








# # Calculate drought severity, duration, and intensity for 3-month SPEI: from separate hist/future SPEI calculation ------------------------------------------------------####
# 
# 
# # note: 
# # drought defined as SPEI < -1
# # drought frequency calculated as percentage of time period of interest in which you have drought 
# # drought duration calculated as maximum number of consecutive time periods in which you have drought during a time period of interest
# # drought severity calculated as min of SPEI during droughts in time period of interest
# 
# # identify drought periods: hist
# hist_drought_id = spei_3months_hist$fitted
# mask = hist_drought_id < -1
# hist_drought_id[mask] <- 1
# hist_drought_id[!mask] <- 0
# 
# # identify drought periods: future
# cc_drought_id = spei_3months_future$fitted
# mask = cc_drought_id < -1
# cc_drought_id[mask] <- 1
# cc_drought_id[!mask] <- 0
# 
# # prep for drought severity: hist
# hist_drought_severity_prep <- spei_3months_hist$fitted
# mask = hist_drought_severity_prep >= -1
# hist_drought_severity_prep[mask] <- NA
# 
# # prep for drought severity: future
# cc_drought_severity_prep <- spei_3months_future$fitted
# mask = cc_drought_severity_prep >= -1
# cc_drought_severity_prep[mask] <- NA
# 
# # separate hist and cc
# # hist <- spei_3months$fitted[1:312,]
# # hist_drought_id <- drought_id[1:312,]
# # hist_drought_severity_prep <- drought_severity_prep[1:312,]
# # cc <- spei_3months$fitted[313:1320,]
# # cc_drought_id <- drought_id[313:1320,]
# # cc_drought_severity_prep <- drought_severity_prep[313:1320,]
# 
# # calculate drought frequency (as percentage of time spent in drought)
# hist_drought_freq <- colSums(hist_drought_id, na.rm=TRUE)/nrow(hist_drought_id)
# cc_drought_freq <- colSums(cc_drought_id, na.rm=TRUE)/nrow(cc_drought_id)
# 
# # calculate drought severity
# hist_drought_severity <- apply(hist_drought_severity_prep, 2, min, na.rm=TRUE)
# cc_drought_severity <- apply(cc_drought_severity_prep, 2, min, na.rm=TRUE)
# 
# # calculate drought duration
# hist_drought_duration_list <- list()
# cc_drought_duration_list <- list()
# num_cols <- ncol(hist_drought_id)
# for (col in 1:num_cols){
#   
#   # hist
#   hist_duration <- rle(hist_drought_id[,col])
#   hist_drought_duration_list[[col]] <- hist_duration
#   
#   # cc
#   cc_duration <- rle(cc_drought_id[,col])
#   cc_drought_duration_list[[col]] <- cc_duration
#   
# }
# names(hist_drought_duration_list) <- colnames(hist_drought_id)
# names(cc_drought_duration_list) <- colnames(cc_drought_id)
# 
# # calculate longest drought duration for each scenario
# drought_duration_longest <- data.frame(matrix(NA, nrow=length(colnames(hist_drought_id)), ncol=3))
# colnames(drought_duration_longest) <- c('scenarios', 'hist', 'cc')
# drought_duration_longest$scenarios <- colnames(hist_drought_id)
# drought_duration_longest$hist <- NA
# drought_duration_longest$cc <- NA
# num_rows <- nrow(drought_duration_longest)
# for (row in 1:num_rows){
#   
#   # get scenario 
#   scenario <- drought_duration_longest$scenario[row]
#   
#   # get longest drought duration: hist
#   length <- hist_drought_duration_list[[scenario]]$length
#   value <- hist_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$hist[row] <- longest_drought
#   
#   # get longest drought duration: cc
#   length <- cc_drought_duration_list[[scenario]]$length
#   value <- cc_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$cc[row] <- longest_drought
#   
#   
# }




# Calculate drought severity, duration, and intensity for 3-month SPEI: from separate hist/future SPEI calculation, with modified duration calculation -------------------####


# note: 
# drought defined as SPEI < -1
# drought frequency calculated as percentage of time period of interest in which you have drought 
# drought duration calculated as maximum number of consecutive time periods in which you have drought during a time period of interest
# drought severity calculated as min of SPEI during droughts in time period of interest

# identify drought periods: hist
hist_drought_id = spei_3months_hist$fitted
mask = hist_drought_id < -1
hist_drought_id[mask] <- 1
hist_drought_id[!mask] <- 0

# identify drought periods: future
cc_drought_id = spei_3months_future$fitted
mask = cc_drought_id < -1
cc_drought_id[mask] <- 1
cc_drought_id[!mask] <- 0

# # prep for drought severity: hist
# hist_drought_severity_prep <- spei_3months_hist$fitted
# mask = hist_drought_severity_prep >= -1
# hist_drought_severity_prep[mask] <- NA
# 
# # prep for drought severity: future
# cc_drought_severity_prep <- spei_3months_future$fitted
# mask = cc_drought_severity_prep >= -1
# cc_drought_severity_prep[mask] <- NA
# 
# # calculate drought frequency (as percentage of time spent in drought)
# hist_drought_freq <- colSums(hist_drought_id, na.rm=TRUE)/nrow(hist_drought_id)
# cc_drought_freq <- colSums(cc_drought_id, na.rm=TRUE)/nrow(cc_drought_id)
# 
# # calculate drought severity
# hist_drought_severity <- apply(hist_drought_severity_prep, 2, min, na.rm=TRUE)
# cc_drought_severity <- apply(cc_drought_severity_prep, 2, min, na.rm=TRUE)

# calculate drought duration
hist_drought_duration_list <- list()
cc_drought_duration_list <- list()
num_cols <- ncol(hist_drought_id)
for (col in 1:num_cols){
  
  # hist: convert rows with less than n values of non-drought to drought
  hist_duration_orig <- rle2(hist_drought_id[,col], indices=TRUE)
  hist_duration_nondrought <- as_tibble(hist_duration_orig) %>%
    dplyr::filter(., 
                  value == 0,
                  length <= max_num_nondrought_months)
  num_rows <- nrow(hist_duration_nondrought)
  for (row in 1:num_rows){     # loop through rows in hist_duration_nondrought and convert to drought in hist_drought_id
    
    # get start and stop indices
    idx_start <- hist_duration_nondrought[row, 'start'][[1]]
    idx_stop <- hist_duration_nondrought[row, 'stop'][[1]]
    
    # convert non-drought to drought
    hist_drought_id[c(idx_start:idx_stop), col] <- 1
    
  }
  
  # hist: calculate duration
  hist_duration <- rle(hist_drought_id[,col])
  hist_drought_duration_list[[col]] <- hist_duration
  
  
  
  #----------------
  
  
  # cc:  convert rows with less than n values of non-drought to drought
  cc_duration_orig <- rle2(cc_drought_id[,col], indices=TRUE)
  cc_duration_nondrought <- as_tibble(cc_duration_orig) %>%
    dplyr::filter(., 
                  value == 0,
                  length <= max_num_nondrought_months)
  num_rows <- nrow(cc_duration_nondrought)
  for (row in 1:num_rows){     # loop through rows in hist_duration_nondrought and convert to drought in hist_drought_id
    
    # get start and stop indices
    idx_start <- cc_duration_nondrought[row, 'start'][[1]]
    idx_stop <- cc_duration_nondrought[row, 'stop'][[1]]
    
    # convert non-drought to drought
    cc_drought_id[c(idx_start:idx_stop), col] <- 1
    
  } 
  
 
  # cc: calculate duration
  cc_duration <- rle(cc_drought_id[,col])
  cc_drought_duration_list[[col]] <- cc_duration
  
  
}

names(hist_drought_duration_list) <- colnames(hist_drought_id)
names(cc_drought_duration_list) <- colnames(cc_drought_id)


# calculate longest drought duration for each scenario
drought_duration_longest <- data.frame(matrix(NA, nrow=length(colnames(hist_drought_id)), ncol=3))
colnames(drought_duration_longest) <- c('scenarios', 'hist', 'cc')
drought_duration_longest$scenarios <- colnames(hist_drought_id)
drought_duration_longest$hist <- NA
drought_duration_longest$cc <- NA
num_rows <- nrow(drought_duration_longest)
for (row in 1:num_rows){
  
  # get scenario 
  scenario <- drought_duration_longest$scenario[row]
  
  # get longest drought duration: hist
  length <- hist_drought_duration_list[[scenario]]$length
  value <- hist_drought_duration_list[[scenario]]$values
  df <- data.frame(length, value)
  names(df) <- c('length', 'value')
  df <- subset(df, value == 1)
  longest_drought <- max(df$length)
  drought_duration_longest$hist[row] <- longest_drought
  
  # get longest drought duration: cc
  length <- cc_drought_duration_list[[scenario]]$length
  value <- cc_drought_duration_list[[scenario]]$values
  df <- data.frame(length, value)
  names(df) <- c('length', 'value')
  df <- subset(df, value == 1)
  longest_drought <- max(df$length)
  drought_duration_longest$cc[row] <- longest_drought
  
  
}



# prep for drought severity: hist
hist_drought_severity_prep <- spei_3months_hist$fitted
mask = hist_drought_severity_prep >= -1
hist_drought_severity_prep[mask] <- NA

# prep for drought severity: future
cc_drought_severity_prep <- spei_3months_future$fitted
mask = cc_drought_severity_prep >= -1
cc_drought_severity_prep[mask] <- NA

# calculate drought frequency (as percentage of time spent in drought)
hist_drought_freq <- colSums(hist_drought_id, na.rm=TRUE)/nrow(hist_drought_id)
cc_drought_freq <- colSums(cc_drought_id, na.rm=TRUE)/nrow(cc_drought_id)

# calculate drought severity
hist_drought_severity <- apply(hist_drought_severity_prep, 2, min, na.rm=TRUE)
cc_drought_severity <- apply(cc_drought_severity_prep, 2, min, na.rm=TRUE)









# # Calculate drought severity, duration, and intensity for 12-month SPEI ----------------------------------------------------------------####
# 
# 
# # note:
# # historical period is months 1-312 for SPEI-12
# # future period is months 312-1320 for SPEI-12
# # drought defined as SPEI < -1
# # drought frequency calculated as number of times that you have drought in the time period of interest
# # drought duration calculated as number of consecutive time periods in which you have drought
# # drought severity calculated as mean of SPEI during drought periods
# 
# # identify drought periods
# drought_id = spei_12months$fitted
# mask = drought_id < -1
# drought_id[mask] <- 1
# drought_id[!mask] <- 0
# 
# # prep for drought severity
# drought_severity_prep <- spei_12months$fitted
# mask = drought_severity_prep >= -1
# drought_severity_prep[mask] <- NA
# 
# # separate hist and cc
# hist <- spei_12months$fitted[1:312,]
# hist_drought_id <- drought_id[1:312,]
# hist_drought_severity_prep <- drought_severity_prep[1:312,]
# cc <- spei_12months$fitted[313:1320,]
# cc_drought_id <- drought_id[313:1320,]
# cc_drought_severity_prep <- drought_severity_prep[313:1320,]
# 
# # calculate drought frequency (as percentage of time spent in drought)
# hist_drought_freq <- colSums(hist_drought_id, na.rm=TRUE)/nrow(hist_drought_id)
# cc_drought_freq <- colSums(cc_drought_id, na.rm=TRUE)/nrow(cc_drought_id)
# 
# # calculate drought severity
# hist_drought_severity <- apply(hist_drought_severity_prep, 2, min, na.rm=TRUE)
# cc_drought_severity <- apply(cc_drought_severity_prep, 2, min, na.rm=TRUE)
# 
# # calculate drought duration
# hist_drought_duration_list <- list()
# cc_drought_duration_list <- list()
# num_cols <- ncol(hist_drought_id)
# for (col in 1:num_cols){
# 
#   # hist
#   hist_duration <- rle(hist_drought_id[,col])
#   hist_drought_duration_list[[col]] <- hist_duration
# 
#   # cc
#   cc_duration <- rle(cc_drought_id[,col])
#   cc_drought_duration_list[[col]] <- cc_duration
# 
# }
# names(hist_drought_duration_list) <- colnames(hist_drought_id)
# names(cc_drought_duration_list) <- colnames(cc_drought_id)
# 
# # calculate longest drought duration for each scenario
# drought_duration_longest <- data.frame(matrix(NA, nrow=length(colnames(hist_drought_id)), ncol=3))
# colnames(drought_duration_longest) <- c('scenarios', 'hist', 'cc')
# drought_duration_longest$scenarios <- colnames(hist_drought_id)
# drought_duration_longest$hist <- NA
# drought_duration_longest$cc <- NA
# num_rows <- nrow(drought_duration_longest)
# for (row in 1:num_rows){
# 
#   # get scenario
#   scenario <- drought_duration_longest$scenario[row]
# 
#   # get longest drought duration: hist
#   length <- hist_drought_duration_list[[scenario]]$length
#   value <- hist_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$hist[row] <- longest_drought
# 
#   # get longest drought duration: cc
#   length <- cc_drought_duration_list[[scenario]]$length
#   value <- cc_drought_duration_list[[scenario]]$values
#   df <- data.frame(length, value)
#   names(df) <- c('length', 'value')
#   df <- subset(df, value == 1)
#   longest_drought <- max(df$length)
#   drought_duration_longest$cc[row] <- longest_drought
# 
# 
# }






