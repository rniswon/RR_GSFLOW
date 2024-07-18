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

# load
library(tidyverse) 
library(lubridate)
library(readr)
library(dplyr)
library(tidyr)
library(SPEI)



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



# Read in and reformat ----------------------------------------------------------------####

precip_potet_list <- list()
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
  
  # sum by month-year
  precip_potet <- precip_potet %>%
    group_by(year, month) %>%
    summarise(precip = sum(precip),
              potet = sum(potet))
  
  # calculate climatic water balance as precip minus potet
  precip_potet$cwb <- precip_potet$precip - precip_potet$potet
  
  # add column for model name
  precip_potet$model_name <- model_name
    
  # store data frame in list
  precip_potet_list[[i]] <- precip_potet
  
  
}

# combine all data frames into one
precip_potet_df <- bind_rows(precip_potet_list)

# export
file_path <- paste0(output_dir, 'precip_potet_cwb.csv')
write.csv(precip_potet_df, file = file_path, row.names=FALSE)






# Calculate SPEI ----------------------------------------------------------------####


# remove precip and potet data
precip_potet_df <- precip_potet_df[,c('model_name', 'year', 'month', 'cwb')]

# convert to wide format with one column per model
precip_potet_df = precip_potet_df %>% 
  pivot_wider(names_from=c(model_name), values_from=cwb)

# remove year and month columns
precip_potet_df_old <- precip_potet_df
precip_potet_df <- subset(precip_potet_df, select = -c(year, month))

# calculate SPEI
spei_3months <- spei(as.matrix(precip_potet_df),3)
spei_6months <- spei(as.matrix(precip_potet_df),6)
spei_9months <- spei(as.matrix(precip_potet_df),9)
spei_12months <- spei(as.matrix(precip_potet_df),12)
spei_60months <- spei(as.matrix(precip_potet_df),60)




# Define SPEI plotting function ----------------------------------------------------------------####

spei_ploting_function <- function(spei_output, precip_potet_df_old, output_file_name, plot_title){
  
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
  






# Plot SPEI ----------------------------------------------------------------------------####

# plot SPEI: 3 months
output_file_name <- 'spei_3months'
plot_title <- '3-Month SPEI'
spei_ploting_function(spei_3months, precip_potet_df_old, output_file_name, plot_title)


# plot SPEI: 6 months
output_file_name <- 'spei_6months'
plot_title <- '6-Month SPEI'
spei_ploting_function(spei_6months, precip_potet_df_old, output_file_name, plot_title)


# plot SPEI: 9 months
output_file_name <- 'spei_9months'
plot_title <- '9-Month SPEI'
spei_ploting_function(spei_9months, precip_potet_df_old, output_file_name, plot_title)


# plot SPEI: 12 months
output_file_name <- 'spei_12months'
plot_title <- '12-Month SPEI'
spei_ploting_function(spei_12months, precip_potet_df_old, output_file_name, plot_title)


# plot SPEI: 60 months
output_file_name <- 'spei_60months'
plot_title <- '60-month SPEI'
spei_ploting_function(spei_60months, precip_potet_df_old, output_file_name, plot_title)





