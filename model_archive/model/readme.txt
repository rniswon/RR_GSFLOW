Description: 

	This directory contains fourteen subdirectories which contain all of the 
	input files for each of the fourteen simulations documented in the paper, 
	[insert link to paper].



Directory structure: 

	model\
	------
		
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