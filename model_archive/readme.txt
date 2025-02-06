MODEL ARCHIVE REFERENCES
------------------------

	Publication
	[insert RR paper reference]

	Data Releases
	[insert RR data release references]

	Model Application Data Release
	[insert model application data release reference]



MODEL ARCHIVE SUMMARY
---------------------

Archive created: 2024-04-01


        Description: 
        ------------

		The underlying directories contain all of the input and output files for the
		simulations described in the publication, along with the executable files.
				 
		The model simulations were run with GSFLOW version 2.3.0 and MODSIM version 8.6.  
				   

		
		System requirements:
		--------------------
		
		The model was run on a Windows Server 2019 Standard Edition (64-bit) operating system 
		with a 3 GHz Intel(R) Xeon(R) Gold 6154 CPU and 384 GB RAM.
		
		The complete model archive requires about 5.16 TB of storage space (once unzipped).  The 
		modified model archive included in this data release (with large files removed) requires 
		about 206 GB of storage space (once unzipped).
		
		
		
		Reconstructing the model archive from the online model archive data release:
        ----------------------------------------------------------------------------
		
		The model archive is available as a data release from:
        [INSERT MODEL ARCHIVE DATA RELEASE LINK]
        
        The models will run successfully only if the correct directory 
        structure is correctly restored. The model archive is broken into 
        several pieces to reduce the likelihood of download timeouts. 
        Small files (readme.txt and modelgeoref.txt) are available as 
        uncompressed files. Each subdirectory within the output directory is 
		zipped separately.  All other files are zipped at the highest-level 
		of the directory structure (listed below). For example, the files in 
		the "georef" subdirectory are zipped into a zip file named "georef.zip". 
		Most zip files should be unzipped into a directory with the same name 
		as the zip file name without the .zip extension. The zip files with 
		names starting with "output" should be unzipped in the same manner as 
		other zip files but should be placed within an "output" subdirectory 
        created at the same level as the "georef" subdirectory created from 
        "georef.zip". 
        
        The highest-level directory structure of the original model archive is:
        
            rr_model_archive\
                ancillary\
                bin\
                georef\
                model\
				nonpublic\
                output\
                source\
				modelgeoref.txt
				readme.txt
                
        The full directory structure of the model archive and the files  
        within each subdirectory are listed below.       
		
		
		
		
		Summary of simulations:
		-----------------------
		
		Fourteen different simulations are included in this archive. The simulations are briefly described in the 
		table below. 
		
		
			MODEL SIMULATION    				SIMULATION            		SIMULATION       			TIME PERIOD
			SUBDIRECTORY         				ID                 			NAME          		 		SIMULATED
			----------------    				----------            		--------------      		-----------

			model01.hist_baseline    			hist_baseline               Historical baseline         1990-2015 
																			scenario 
																			(i.e. calibrated 
																			GSFLOW model)
																			

			model02.hist_unimpaired    			hist_unimpaired             Historical         		 	1990-2015
																			unimpaired 
																			flow scenario
																		 
			model03.hist_frost          		hist_frost            		Historical frost         	1990-2015  
																			protection scenario


			model04.hist_baseline_modsim        hist_baseline_modsim   		Historical baseline         1990-2015 
																			scenario with MODSIM

									 
			model05.hist_pv1_modsim           	hist_pv1_modsim            	Historical         			1990-2015 
																			run-of-river  
																			Potter Valley 
																			scenario
																			
			model06.hist_pv2_modsim    			hist_pv2_modsim				Historical  				1990-2015
																			cessation of 
																			Potter Valley 
																			inflows scenario
																			
			model07.CanESM2_rcp45  				CanESM2_rcp45				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			CanESM2-rcp45
																			
			model08.CanESM2_rcp85				CanESM2_rcp85				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			CanESM2-rcp85

			model09.CNRM-CM5_rcp45  			CNRM-CM5_rcp45				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			CNRM-CM5-rcp45

			model10.CNRM-CM5_rcp85				CNRM-CM5_rcp85				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			CNRM-CM5-rcp85

			model11.HadGEM2-ES_rcp45  			HadGEM2-ES_rcp45			Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			HadGEM2-ES-rcp45

			model12.HadGEM2-ES_rcp85			HadGEM2-ES_rcp85			Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			HadGEM2-ES-rcp85

			model13.MIROC5_rcp45  				MIROC5_rcp45				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			MIROC5-rcp45

			model14.MIROC5_rcp85				MIROC5_rcp85				Future water use  			1990-2099
																			and climate change  
																			scenario using 
																			MIROC5-rcp85



		
		Running the models:
        -------------------
		
        Each simulation has a batch file that will run it.  
		The batch file calls a model executable and a control file.  
		The control file specifies the input files to be used in the 
		simulation, as well as, the output files that are created. 

        Note: The output for these models is written directly to the output 
        directory.  Running the model will overwrite the existing files.
          
        The documented simulations can be run by running the 
		following Windows batch files (they can be run by double-clicking 
		the batch file): 
        
			rr_model_archive\model\model01.hist_baseline\gsflow_model\windows\run.bat         				[generates fewer outputs]
			rr_model_archive\model\model01.hist_baseline\gsflow_model\windows\run_heavy.bat   				[generates more outputs]
			rr_model_archive\model\model02.hist_unimpaired\gsflow_model\windows\run_heavy.bat 
			rr_model_archive\model\model03.hist_frost\gsflow_model\windows\run.bat          				[generates fewer outputs]
			rr_model_archive\model\model03.hist_frost\gsflow_model\windows\run_heavy.bat    				[generates more outputs]
			rr_model_archive\model\model04.hist_baseline_modsim\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model05.hist_pv1_modsim\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model06.hist_pv2_modsim\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model07.CanESM2_rcp45\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model08.CanESM2_rcp85\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model09.CNRM-CM5_rcp45\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model10.CNRM-CM5_rcp85\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model11.HadGEM2-ES_rcp45\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model12.HadGEM2-ES_rcp85\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model13.MIROC5_rcp45\gsflow_model\windows\run_heavy_w_modsim.bat
			rr_model_archive\model\model14.MIROC5_rcp85\gsflow_model\windows\run_heavy_w_modsim.bat
			
		
		
		
MODEL ARCHIVE FILES
-------------------

	readme.txt: This file documents the structure of the model archive.

	modelgeoref.txt: [ASCII file with the four corners of the model 
					 domain. Model data files are provided as decimal 
					 degrees in NAD 1983 projection.] 

	ancillary\
	----------

		Description: 
		This directory contains two subdirectories, calibration (contains scripts 
		used to generate calibration figures and tables) and zone_budget (contains
		inputs for the ZoneBudget program, used to process the MODFLOW cell-by-cell 
		output file, along with the ZoneBudget executable file). 
		
		To run the ZoneBudget program that processes the MODFLOW cell-by-cell output file (rr_tr.cbc):
			1) Go to: rr_model_archive\ancillary\zone_budget
			2) For zones set to subbasins: double-click on zb_subbasins_[model_name].bat
			3) For zones set to the entire Russian River watershed: double-click on zb_watershed_[model_name].bat
			4) Results will be sent to the modflow output folder for that model (i.e. the same folder that contains the rr_tr.cbc file)
		
		To run the calibration scripts that evaluate the calibration of the baseline model (hist_baseline), follow these steps:
			1) Go to: rr_model_archive\ancillary\calibration\scripts
			2) Open up plot_all_gsflow.py in a Python Integrated Development Environment (we used PyCharm).
			3) Make sure the correct option is chosen for the variable "mf_name_file_type", depending on whether 
			   you ran the model with all possible outputs or fewer outputs.
			4) Run plot_all_gsflow.py.  Plots and tables evaluating streamflow, groundwater heads, lake stages and volumes, 
			   and well pumping reduction will be sent to rr_model_archive\ancillary\calibration\results.  They will be 
			   organized into sub-directories as described in the directory structure below.
			5) Open up calculate_ag_water_use.py in a Python Integrated Development Environment.  In the 
			   "set model-simulated values" section, insert the simulated agricultural water use by wells, 
			   diversions, ponds, and total.  The simulated agricultural water use can be found in the volumetric 
			   agricultural budget listed at the last time step in the rr_tr.list file generated by the simulation.  
			   Run calculate_ag_water_use.py.  The water use in units of meters/yr will be printed to the screen 
			   and can be compared to literature values.
		

		calibration\
			
			results\
			results plots and tables generated by calibration scripts
			
				plots\
				results plots generated by calibration scripts
				
					gw_resid_boxplots\
					boxplots of groundwater head residuals
					
					gw_resid_map\
					map of groundwater head residuals
					
					gw_resid_vs_obs\
					scatter plots of groundwater head residuals vs. observed heads
					
					gw_resid_vs_sim\
					scatter plots of groundwater head residuals vs. simulated heads
					
					gw_sim_vs_obs\
					scatter plots of simulated heads vs. observed heads
					
					gw_time_series\
					time series plots of groundwater heads
					
					lakes\
					time series plots of lake stage and volume 
						
					pumping_reduction\
					time series plots of pumping reduction
					
					streamflow_annual\
					time series plots of annual streamflow
					
					streamflow_daily\
					time series plots of daily streamflow
					
					streamflow_monthly\
					time series plots of monthly streamflow
				
				tables\
				results tables generated by calibration scripts
			
			
			scripts\
			scripts used to generate calibration plots and tables

				script_inputs\
				inputs to calibration scripts
				

				Files: 

					calculate_ag_water_use.py: script that calculates agricultural water use
					
					plot_all_gsflow.py: script that calls other scripts that plot streamflow, 
										groundwater heads, lake outputs, and pumping reduction
					
					plot_gage_output.py: script that plots simulated vs. observed streamflow
					
					plot_hobs_output_combo_obs.py: script that plots simulated vs. observed 
												   groundwater heads
					
					plot_lake_outputs.py: script that plots simulated vs. observed lake 
										  stages and volumes
					
					plot_pumping_reduction_mnw.py: script that plots pumping reduction
					
					
					
		zone_budget\
		ZoneBudget input files and executable file used to process the MODFLOW cell-by-cell output file

               
  

	bin\ 
	----
		
		Description: 
		
			This directory contains the compiled code that was used in the study for each simulation.  
		
		Files:
		
			rr_model_archive\bin\bin01.hist_baseline\gsflow.exe: GSFLOW (version 2.3.0) 64-bit windows executable
			
			rr_model_archive\bin\bin02.hist_unimpaired\gsflow.exe: GSFLOW (version 2.3.0) 64-bit windows executable
			
			rr_model_archive\bin\bin03.hist_frost\gsflow.exe: GSFLOW (version 2.3.0) 64-bit windows executable
			
			rr_model_archive\bin\bin04.hist_baseline_modsim\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																				64-bit windows executable
			
			rr_model_archive\bin\bin05.hist_pv1_modsim\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		   64-bit windows executable
			
			rr_model_archive\bin\bin06.hist_pv2_modsim\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		   64-bit windows executable
			
			rr_model_archive\bin\bin07.CanESM2_rcp45\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		 64-bit windows executable
			
			rr_model_archive\bin\bin08.CanESM2_rcp85\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		 64-bit windows executable
			
			rr_model_archive\bin\bin09.CNRM-CM5_rcp45\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		  64-bit windows executable
			
			rr_model_archive\bin\bin10.CNRM-CM5_rcp85\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		  64-bit windows executable
			
			rr_model_archive\bin\bin11.HadGEM2-ES_rcp45\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																			64-bit windows executable
			
			rr_model_archive\bin\bin12.HadGEM2-ES_rcp85\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																			64-bit windows executable
			
			rr_model_archive\bin\bin13.MIROC5_rcp45\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		64-bit windows executable
			
			rr_model_archive\bin\bin14.MIROC5_rcp85\MWC_MS_GSF_Run.exe: MODSIM-GSFLOW (MODSIM version 8.6, GSFLOW version 2.3.0) 
																		64-bit windows executable
			
			readme.txt: ReadMe file
			
			


	georef\
	-------
		 
		Description: 
		
			This directory contains a polygon shapefile of the model grid 
			defining the active and inactive areas of the model documented 
			in the paper, 
			[insert link to paper]
		
		Files: 
		
			rr_model_grid.cpg:     part of the rr_model_grid.shp shapefile
			
			rr_model_grid.dbf:     part of the rr_model_grid.shp shapefile
			
			rr_model_grid.prj:     part of the rr_model_grid.shp shapefile
			
			rr_model_grid.sbn:     part of the rr_model_grid.shp shapefile

			rr_model_grid.sbx:     part of the rr_model_grid.shp shapefile

			rr_model_grid.shp:     part of the rr_model_grid.shp shapefile
			
			rr_model_grid.shp.xml: part of the rr_model_grid.shp shapefile
		 
			rr_model_grid.shx:     part of the rr_model_grid.shp shapefile
			
			readme.txt: ReadMe file

							

		
	model\
	------
		
		Description: 
		
			This directory contains fourteen subdirectories which contain all of the 
			input files for each of the fourteen simulations documented in the paper, 
			[insert link to paper]. 
			
		
		model01.hist_baseline\
		----------------------
			This subdirectory contains model input files specific to the simulation for the hist_baseline model.
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					gsflow_rr.control: GSFLOW control file with fewer model outputs
					gsflow_rr_heavy.control: GSFLOW control file with more model outputs 
					rr_tr.nam: MODFLOW name file with fewer model outputs
					rr_tr_heavy.nam: MODFLOW name file with more model outputs
					run.bat: Windows batch file that generates fewer model outputs
					run_heavy.bat: Windows batch file that generates more model outputs
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type


		
		
		model02.hist_unimpaired\
		------------------------
			This subdirectory contains model input files specific to the simulation for the hist_unimpaired model.
			
			gsflow_model\
			
				modflow\
								
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					gsflow_rr_heavy.control: GSFLOW control file with more model outputs 
					rr_tr_heavy.nam: MODFLOW name file with more model outputs
					run_heavy.bat: Windows batch file that generates more model outputs
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type
		 
		 
		 
		
		model03.hist_frost\
		-------------------
			This subdirectory contains model input files specific to the simulation for the hist_frost model.
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					gsflow_rr.control: GSFLOW control file with fewer model outputs
					gsflow_rr_heavy.control: GSFLOW control file with more model outputs 
					rr_tr.nam: MODFLOW name file with fewer model outputs
					rr_tr_heavy.nam: MODFLOW name file with more model outputs
					run.bat: Windows batch file that generates fewer model outputs
					run_heavy.bat: Windows batch file that generates more model outputs
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type


		
		
		model04.hist_baseline_modsim\
		-----------------------------
			This subdirectory contains model input files specific to the simulation for the hist_baseline_modsim model.

			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__hist_baseline: MODSIM input file
					gsflow_rr_heavy_MODSIM_hist_baseline.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__hist_baseline.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type



		
		model05.hist_pv1_modsim\
		------------------------
			This subdirectory contains model input files specific to the simulation for the hist_pv1_modsim model.

			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__hist_pv1: MODSIM input file
					gsflow_rr_heavy_MODSIM_hist_pv1.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__hist_pv1.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type


		
		
		model06.hist_pv2_modsim\
		------------------------
			This subdirectory contains model input files specific to the simulation for the hist_pv2_modsim model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__hist_pv2: MODSIM input file
					gsflow_rr_heavy_MODSIM_hist_pv2.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__hist_pv2.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model07.CanESM2_rcp45\
		----------------------
			This subdirectory contains model input files specific to the simulation for the CanESM2_rcp45 model.

			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__CanESM2_rcp45: MODSIM input file
					gsflow_rr_CanESM2_rcp45_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__CanESM2_rcp45.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model08.CanESM2_rcp85\
		----------------------
			This subdirectory contains model input files specific to the simulation for the CanESM2_rcp85 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__CanESM2_rcp85: MODSIM input file
					gsflow_rr_CanESM2_rcp85_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__CanESM2_rcp85.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model09.CNRM-CM5_rcp45\
		-----------------------
			This subdirectory contains model input files specific to the simulation for the CNRM-CM5_rcp45 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__CNRMCM5_rcp45: MODSIM input file
					gsflow_rr_CNRM-CM5_rcp45_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__CNRMCM5_rcp45.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model10.CNRM-CM5_rcp85\
		-----------------------
			This subdirectory contains model input files specific to the simulation for the CNRM-CM5_rcp85 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__CNRMCM5_rcp85: MODSIM input file
					gsflow_rr_CNRM-CM5_rcp85_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__CNRMCM5_rcp85.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model11.HadGEM2-ES_rcp45\
		-------------------------
			This subdirectory contains model input files specific to the simulation for the HadGEM2-ES_rcp45 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__HadGEM2ES_rcp45: MODSIM input file
					gsflow_rr_HadGEM2-ES_rcp45_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__HadGEM2ES_rcp45.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 



		
		
		model12.HadGEM2-ES_rcp85\
		-------------------------
			This subdirectory contains model input files specific to the simulation for the HadGEM2-ES_rcp85 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__HadGEM2ES_rcp85: MODSIM input file
					gsflow_rr_HadGEM2-ES_rcp85_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__HadGEM2ES_rcp85.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 

		
		
			
		model13.MIROC5_rcp45\
		---------------------
			This subdirectory contains model input files specific to the simulation for the MIROC5_rcp45 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__MIROC5_rcp45: MODSIM input file
					gsflow_rr_MIROC5_rcp45_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__MIROC5_rcp45.waprj: MODSIM input file
				
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 


		
		
		model14.MIROC5_rcp85\
		---------------------
			This subdirectory contains model input files specific to the simulation for the MIROC5_rcp85 model.
			
			
			gsflow_model\
			
				modflow\
								
					ag_diversions\: subdirectory of agricultural diversions for ponds
					Bevans_bathy.dat: bathymetry file for small lake 
					Bradford_bathy.dat: bathymetry file for small lake
					CoenC3_bathy.dat: bathymetry file for small lake
					Crawford_bathy.dat: bathymetry file for small lake
					Lolonis_bathy.dat: bathymetry file for small lake
					Mallacomes_bathy.dat: bathymetry file for small lake
					Mark_West_inflow.dat: Mark West inflows 
					Mendo_Lake_release.dat: Lake Mendocino release
					Meno_bathy.dat: bathymetry file for small lake
					Merlo_bathy.dat: bathymetry file for small lake
					Murray_bathy.dat: bathymetry file for small lake
					Potter_Valley_inflow.dat: Potter Valley inflows 
					redwood_valley_demand.dat: Redwood Valley outflows
					rr_tr.ag: MODFLOW agricultural water use file with fewer model outputs
					rr_tr.bas: MODFLOW basic file
					rr_tr.dis: MODFLOW discretization file
					rr_tr.gage: MODFLOW gage file with fewer model outputs
					rr_tr.ghb: MODFLOW general head boundary file
					rr_tr.hfb: MODFLOW horizontal flow barrier file
					rr_tr.hob: MODFLOW head observation file
					rr_tr.lak: MODFLOW lake file
					rr_tr.mnw2: MODFLOW multi-node well file
					rr_tr.mnwi: MODFLOW multi-node well information file
					rr_tr.nwt: MODFLOW Newton-Raphson file 
					rr_tr.oc: MODFLOW output control file with fewer model outputs
					rr_tr.sfr: MODFLOW streamflow routing file
					rr_tr.upw: MODFLOW upstream weighted file
					rr_tr.uzf: MODFLOW unsaturated zone flow file
					rr_tr_heavy.ag: MODFLOW agricultural water use file with more model outputs
					rr_tr_heavy.gage: MODFLOW gage file with more model outputs
					rr_tr_heavy.oc: MODFLOW output control file with more model outputs
					rubber_dam_gate_outflow.dat: rubber dam gate outflow
					rubber_dam_lake.dat: rubber dam bathymetry
					rubber_dam_pond_outflow.dat: rubber dam pond outflow
					rubber_dam_spillway_outflow.dat: rubber dam spillway outflow
					rural_pumping.wel: MODFLOW well file
					Sonoma_bathy.dat: Lake Sonoma bathymetry
					Sonoma_Lake_release.dat: Lake Sonoma releases
					Towibalyla_bathy.dat: bathymetry file for small lake
					
					
				prms\
				
					ag_pond_HRUs.param: PRMS parameter file for agricultural pond parameters
					prms_rr.dat: PRMS data file
					prms_rr.param: PRMS parameter file
				
				
				windows\
				
					BaseNet_OpsGSFLOWTS__MIROC5_rcp85: MODSIM input file
					gsflow_rr_MIROC5_rcp85_heavy_modsim.control: GSFLOW control file  
					rr_tr_heavy.nam: MODFLOW name file 
					RROpsModeling.sqlite: MODSIM sql file
					run_heavy_w_modsim.bat: Windows batch file 
					RussianRiverProject__MIROC5_rcp85.waprj: MODSIM input file
				
			
			Files:
				usgs.model.reference: contains information about model geographic coordinates, 
									  length units, time units, and model type 

		
		

		Files:
	
			readme.txt:
				



	output\
	-------
		This directory contains model output files for each of the fourteen 
		simulations in the model directory.

		
		
		output.model01.hist_baseline\

			This subdirectory contains model input files specific to the simulation 
			for the hist_baseline model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file (not included in model archive due to large file size)
				uzf_discharge.out: unsaturated zone flow discharge output file (not included in model archive due to large file size)
				zb_subbasin.csv: zone budget output log file, aggregated by subbasin
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, aggregated by watershed
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
			
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
				
				


		output.model02.hist_unimpaired\
		
			This subdirectory contains model input files specific to the simulation 
			for the hist_unimpaired model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				uzf_recharge.out: unsaturated zone flow recharge output file
				uzf_discharge.out: unsaturated zone flow discharge output file
				
				
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		 
		
		
		
		output.model03.hist_frost\
		
			This subdirectory contains model input files specific to the simulation 
			for the hist_frost model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file  (not included in model archive due to large file size)
				rr_tr.hds: MODFLOW heads output file  (not included in model archive due to large file size)
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file  (not included in model archive due to large file size)
				uzf_discharge.out: unsaturated zone flow discharge output file  (not included in model archive due to large file size)
				
				
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
			
		
		
		
		output.model04.hist_baseline_modsim\
		
			This subdirectory contains model input files specific to the simulation 
			for the hist_baseline_modsim model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file (not included in model archive due to large file size)
				uzf_discharge.out: unsaturated zone flow discharge output file (not included in model archive due to large file size)
				zb_subbasin.csv: zone budget output log file, aggregated by subbasin
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, aggregated by watershed
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
			
			
		
		
		output.model05.hist_pv1_modsim\

			This subdirectory contains model input files specific to the simulation 
			for the hist_pv1_modsim model.

			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file (not included in model archive due to large file size)
				uzf_discharge.out: unsaturated zone flow discharge output file (not included in model archive due to large file size)
				zb_subbasin.csv: zone budget output log file, aggregated by subbasin
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, aggregated by watershed
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
			
			
			
		
		output.model06.hist_pv2_modsim\

			This subdirectory contains model input files specific to the simulation 
			for the hist_pv2_modsim model.

			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file (not included in model archive due to large file size)
				uzf_discharge.out: unsaturated zone flow discharge output file (not included in model archive due to large file size)
				zb_subbasin.csv: zone budget output log file, aggregated by subbasin
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, aggregated by watershed
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model07.CanESM2_rcp45\

			This subdirectory contains model input files specific to the simulation 
			for the CanESM2_rcp45 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_CanESM2_rcp45.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model08.CanESM2_rcp85\

			This subdirectory contains model input files specific to the simulation 
			for the CanESM2_rcp85 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_CanESM2_rcp85.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file

			
			
			
		
		output.model09.CNRM-CM5_rcp45\

			This subdirectory contains model input files specific to the simulation 
			for the CNRM-CM5_rcp45 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_CNRM-CM5_rcp45.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model10.CNRM-CM5_rcp85\

			This subdirectory contains model input files specific to the simulation 
			for the CNRM-CM5_rcp85 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_CNRM-CM5_rcp85.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model11.HadGEM2-ES_rcp45\
		
			This subdirectory contains model input files specific to the simulation 
			for the HadGEM2-ES_rcp45 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_HadGEM2-ES_rcp45.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model12.HadGEM2-ES_rcp85\

			This subdirectory contains model input files specific to the simulation 
			for the HadGEM2-ES_rcp85 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_HadGEM2-ES_rcp85.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
		
		
		
		
		output.model13.MIROC5_rcp45\

			This subdirectory contains model input files specific to the simulation 
			for the MIROC5_rcp45 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_MIROC5_rcp45.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file
			
			
			
		
		output.model14.MIROC5_rcp85\

			This subdirectory contains model input files specific to the simulation 
			for the MIROC5_rcp85 model.
			
			modflow\
			
				rr_tr.list: MODFLOW list output file
				pumping_reduction.out: pumping reduction output file
				mnwi.out: MODFLOW MNW information output file
				rr_tr.cbc: MODFLOW cell-by-cell output file
				rr_tr.hds: MODFLOW heads output file
				rr_tr.sfr.out: MODFLOW streamflow routing output file
				rr_tr.uzf1008.out: MODFLOW unsaturated zone flow output file 
				rr_tr.hob.out: MODFLOW head observation output file
				RUSSIAN_R_JOHNSONS_BEACH_GUERNEVILLE.go: simulated streamflow output file
				AUSTIN_C_NR_CAZADERO.go: simulated streamflow output file
				RUSSIAN_R_NR_GUERNEVILLE.go: simulated streamflow output file
				RUSSIAN_R_NR_WINDSOR.go: simulated streamflow output file
				DRY_C_NR_MOUTH_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_NR_HEALDSBURG.go: simulated streamflow output file
				RUSSIAN_R_DIGGER_BEND_NR_HEALDSBURG.go: simulated streamflow output file
				MAACAMA_C_NR_KELLOGG.go: simulated streamflow output file
				DRY_C_BLW_LAMBERT_BR_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_JIMTOWN.go: simulated streamflow output file
				DRY_C_NR_GEYSERVILLE.go: simulated streamflow output file
				RUSSIAN_R_GEYSERVILLE.go: simulated streamflow output file
				BIG_SULPHUR_C_A_G_RESORT_NR_CLOVERDALE.go: simulated streamflow output file
				BIG_SULPHUR_C_NR_CLOVERDALE.go: simulated streamflow output file 
				RUSSIAN_R_NR_CLOVERDALE.go: simulated streamflow output file
				RUSSIAN_R_NR_HOPLAND.go: simulated streamflow output file
				RUSSIAN_R_NR_TALMAG.go: simulated streamflow output file
				RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_UKIAH.go: simulated streamflow output file
				EF_RUSSIAN_R_NR_CALPELLA.go: simulated streamflow output file
				mendo_lake_bdg.lak.out: Lake Mendocino budget output file
				sonoma_lake_bdg.lak.out: Lake Sonoma budget output file
				rubber_dam_lake_bdg.lak.out: rubber dam lake budget output file
				subbasin_22.go: simulated streamflow output file
				subbasin_21.go: simulated streamflow output file
				pumping_reduction_ag.out: agricultural pumping reduction output file
				ag_iupseg_[segment_number].out: streamflow from stream segments upstream of agricultural diversion segments
				div_seg_[segment_number]_flow.out: streamflow from agricultural diversion segments
				div_seg_[segment_number]_et.out: evapotranspiration from agricultural diversion segments
				ag_well_[well_number].out: agricultural well output file
				ag_wellet_[well_number].out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_[pond_number].out: agricultural pond output file
				ag_pondet_[pond_number].out: evapotranspiration from fields getting irrigated by agricultural ponds
				ag_well_all.out: agricultural well output file
				ag_wellet_all.out: evapotranspiration from fields getting irrigated by agricultural wells
				ag_pond_all.out: agricultural pond water balance
				ag_pondet_all.out: evapotranspiration from fields getting irrigated by agricultural ponds
				lake_1_outflow_seg_446.out: outflow streamflow from Lake 1
				lake_1_outflow_seg_447.out: outflow streamflow from Lake 1
				lake_2_outflow_seg_448.out: outflow streamflow from Lake 2
				lake_2_outflow_seg_449.out: outflow streamflow from Lake 2
				mendo_inflow_seg64_rch3.out: inflows into Lake Mendocino
				mendo_inflow_seg70_rch9.out: inflows into Lake Mendocino
				lake_3_inflow.out: inflows into Lake 3
				lake_4_inflow.out: inflows into Lake 4
				lake_5_inflow.out: inflows into Lake 5
				lake_6_inflow.out: inflows into Lake 6
				lake_7_inflow.out: inflows into Lake 7
				lake_9_inflow.out: inflows into Lake 9
				lake_10_inflow.out: inflows into Lake 10
				pond_div_[segment_number].txt: agricultural pond diversions
				pond_div_iupseg_[segment_number].out: streamflow from segments upstream of agricultural pond diversions
				uzf_recharge.out: unsaturated zone flow recharge output file 
				uzf_discharge.out: unsaturated zone flow discharge output file 
				zb_subbasin.csv: zone budget output log file, for zones set to subbasins 
				zb_subbasin.csv.2: zone budget output file with variable values aggregated by subbasin
				zb_watershed.csv: zone budget output log file, for zones set to the entire watershed 
				zb_watershed.csv.2: zone budget output file with variable values aggregated by watershed
				
				
			prms\
			
				gsflow_MIROC5_rcp85.csv: GSFLOW output file
				nhru_dprst_evap_hru_yearly.csv: PRMS yearly dprst_evap per HRU
				nhru_dprst_stor_hru_yearly.csv: PRMS yearly dprst_stor per HRU
				nhru_dunnian_flow_yearly.csv: PRMS yearly dunnian_flow per HRU
				nhru_hortonian_flow_yearly.csv: PRMS yearly hortonian_flow per HRU
				nhru_hortonian_lakes_yearly.csv: PRMS yearly hortonian_lakes per HRU
				nhru_hru_actet_yearly.csv: PRMS yearly hru_actet per HRU
				nhru_hru_ppt_yearly.csv: PRMS yearly hru_ppt per HRU
				nhru_imperv_evap_yearly.csv: PRMS yearly imperv_evap per HRU
				nhru_imperv_stor_yearly.csv: PRMS yearly imperv_stor per HRU
				nhru_intcp_evap_yearly.csv: PRMS yearly intcp_evap per HRU
				nhru_intcp_stor_yearly.csv: PRMS yearly intcp_stor per HRU
				nhru_lakein_sz_yearly.csv: PRMS yearly lakein_sz per HRU
				nhru_perv_actet_yearly.csv: PRMS yearly perv_actet per HRU
				nhru_potet_yearly.csv: PRMS yearly potet_yearly per HRU
				nhru_recharge_yearly.csv: PRMS yearly recharge per HRU
				nhru_snow_evap_yearly.csv: PRMS yearly snow_evap per HRU
				nhru_soil_moist_tot_yearly.csv: PRMS yearly soil_moist_tot per HRU
				nhru_sroff_yearly.csv: PRMS yearly sroff per HRU
				nhru_ssres_flow_yearly.csv: PRMS yearly ssres_flow per HRU
				nhru_swale_actet_yearly.csv: PRMS yearly swale_actet per HRU
				nsub_dprst_evap_hru.csv: PRMS daily dprst_evap per subbasin
				nsub_dprst_stor_hru.csv: PRMS daily dprst_stor per subbasin
				nsub_dunnian_flow.csv: PRMS daily dunnian_flow per subbasin
				nsub_hortonian_flow.csv: PRMS daily hortonian_flow per subbasin
				nsub_hortonian_lakes.csv: PRMS daily hortonian_lakes per subbasin
				nsub_hru_actet.csv: PRMS daily hru_actet per subbasin
				nsub_hru_ppt.csv: PRMS daily hru_ppt per subbasin
				nsub_imperv_evap.csv: PRMS daily imperv_evap per subbasin
				nsub_imperv_stor.csv: PRMS daily imperv_stor per subbasin
				nsub_intcp_evap.csv: PRMS daily intcp_evap per subbasin
				nsub_intcp_stor.csv: PRMS daily intcp_stor per subbasin
				nsub_lakein_sz.csv: PRMS daily lakein_sz per subbasin
				nsub_perv_actet.csv: PRMS daily perv_actet per subbasin
				nsub_potet.csv: PRMS daily potet per subbasin
				nsub_recharge.csv: PRMS daily recharge per subbasin
				nsub_snow_evap.csv: PRMS daily snow_evap per subbasin
				nsub_soil_moist_tot.csv: PRMS daily soil_moist_tot per subbasin
				nsub_sroff.csv: PRMS daily sroff per subbasin
				nsub_ssres_flow.csv: PRMS daily ssres_flow per subbasin
				nsub_swale_actet.csv: PRMS daily swale_actet per subbasin
				rr_budget.out2: GSFLOW summary output file
				RR_gsflow.out: GSFLOW volumetric budget output file



		
		Files:
	
			readme.txt: ReadMe file


	
	
	source\
	-------
	This directory contains the source code for the models used in the study.  
	The source code is organized in the following subdirectories:
				 
		rr_model_archive\source\gsflow
		rr_model_archive\source\modsim_gsflow
		
		Files:
	
			readme.txt: ReadMe file

	
		


