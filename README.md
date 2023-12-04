# National Wind Risk Assessment

This repo collects the code developed as part of Geoscience Australia's contribution to the National Wind Risk Assessment (NWRA), a component of the National Climate Risk Assessment (NCRA; 2023-24).


## Regional wind hazard

The regional hazard data is generated in ArcGIS Pro, using geoprocessing functions to convert shapefiles to rasters. 

The `Regional wind hazard provenance.ipynb` notebook is used to generate provenance information for the regional hazard data. Running the code in the notebook will generate the provenance file. 

`applyMultpliers.cmd` is a Windows command file to run the `applyMultipliers.py` script. This will combine the regional wind hazard data with the M3_max site exposure data to generate local wind hazard data. 

## Vulnerability

`Validate vulnerability file.ipynb` is used to ensure the XML file that holds the vulnerability files is correctly formed NRML v0.5 data. 

`Vulnerability model NRML file provenance.ipynb` generates the provenance information for the vulnerability model file. 

## Impact calculations

`run_hazimp_batch.sh` is submitted to the job queue on gadi.nci.org.au to run a collection of HazImp simulations in parallel. This script bulds a list of commands based on the available wind hazard layers in the scratch partition, and then calls `run_hazimp.sh` to execute HazImp for each wind hazard layer. 

`run_hazimp_batch.sh` is set up to run a single region (i.e. State/Territory), which is specified when submitting the job. 

To run, edit the tmeplate configuration file `hazimp_template.yaml`. `RPX` will be replaced with strings like `RP100`, while `STATE` will be replaced with the string value for the region ("WA", "NT", etc.). In most cases, the output folders (and any required parent directories) will be created in `run_hazimp.sh`. 

Submit the job script to the queue, specifying the region::

    qsub -v STATE=QLD run_hazimp_batch.sh

There is no checking done on the regions - if you try "NSZ", then the job will fail when it tries to actually run HazImp and finds there's no exposure file that starts with "NSZ". Currently the list of regions is "WA", "SA", "NT", "TAS", "VIC", "NSW", "ACT" and "QLD". "OT" won't work, because there is no hazard data for the other territories. 

The resources specified in `run_hazimp_batch.sh` _should_ be sufficient for all regions. Check the bigger ones ("NSW", "VIC") - increasing memory should do the trick. 

### Copyright
This work © 2023 by Commonwealth of Australia (Geoscience Australia) is licensed under CC BY 4.0 International

### Contacts

Craig Arthur, craig.arthur@ga.gov.au