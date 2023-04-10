Folder for climate scenarios

Data for climate scenarios was downloaded from Cal-Adapt: https://cal-adapt.org/data/download/
Models include both RCP45 and 85 scenarios
	CanESM2
	CNRM-CM5
	HadGEM2-ES
	MIROC5
	
Data units		GCM			SRPHM	Russian River
	Temperature: 	Kelvin (-273.15 C)	deg F		deg C
	PPT		kg/m2/s (mm/s)		in/d		mm/d

The various csv files downloaded were processed and converted into correct units,
and saved in a single csv file for the historical period and another for the future
period.

There are two weather stations that the SRPHM uses in the PRMS data file, one near 
Santa Rosa, and the other near the airport. Data for both locations were downloaded
and stored in two folders
	/climate_scenarios/SRP/
		/airport
			/download
			/corrected
		/santa_rosa
			/download
			/corrected

Scripts for processing are saved in the respective model folders