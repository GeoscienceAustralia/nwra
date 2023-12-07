#!/bin/bash

# Run HazImp in batch mode

# This shell script is not intended to be run directly. It is called by
# another script `run_hazimp_batch.sh`, which is designed to spawn a number of
# shell scripts in an MPI environment. See the comments in `run_hazimp_batch.sh`
#
# Craig Arthur
# 2023-11-23

umask 0002

module purge
module load pbs
module load dot

module load python3/3.7.4
module load netcdf/4.6.3
module load hdf5/1.10.5
module load geos/3.8.0
module load proj/6.2.1
module load gdal/3.0.2
module load openmpi/4.0.1

# Need to ensure we get the correct paths to access the local version of gdal bindings.
# The module versions are compiled against Python3.6, so we can't use them
export PYTHONPATH=/g/data/w85/.local/lib/python3.7/site-packages:$PYTHONPATH

# Add the local Python-based scripts to the path:
export PATH=/g/data/w85/.local/bin:$PATH

# Needs to be resolved, but this suppresses an error related to HDF5 libs
export HDF5_DISABLE_VERSION_CHECK=2

# Set the number of datasets that can be opened simultaneously by the
# GDALProxyPool mechanism (used by VRT).
# See https://gdal.org/user/configoptions.html
export GDAL_MAX_DATASET_POOL_SIZE=900

SOFTWARE=/g/data/w85/software

# Add HazImp code to the path:
export PYTHONPATH=$SOFTWARE/hazimp:$PYTHONPATH

cd $SOFTWARE/hazimp/

DATE=`date +%Y%m%d%H%M`
CONFIGDIR=$SOFTWARE/nwra

if [ $# -eq 0 ]; then
    # Use an environment variable
    RP=$RP
else
    RP=$1
fi

if [ $# -eq 0 ]; then
    # Use environment variable
    STATE=$STATE
else
    STATE=$2
fi

OUTPUTDIR=/scratch/w85/nwra/impact/$STATE

if [ ! -d $OUTPUTDIR ]; then
    mkdir -p --mode 775 $OUTPUTDIR
fi
echo "Running hazimp for $STATE and $RP"

CONFIGFILE=$CONFIGDIR/$RP.$STATE.yaml
OUTPUT=/scratch/w85/nwra/impact

# Substitute the paths into the template configuration file:
sed 's|RPX|'$RP'|g' /g/data/w85/software/nwra/hazimp_template.yaml > $CONFIGFILE
sed -i 's|STATE|'$STATE'|g' $CONFIGFILE
chmod 775 $CONFIGFILE

if [ ! -f "$CONFIGFILE" ]; then
    echo "Configuration file does not exist: $CONFIGFILE"
    exit 1
else
    echo $CONFIGFILE
fi

python3 $SOFTWARE/hazimp/hazimp/main.py -c $CONFIGFILE 

# Clean up to reduce inode usage
rm -rf $OUTPUTDIR/$RP.$STATE.png
#rm -rf $OUTPUTDIR/$RP.$STATE.xml
#rm -rf $CONFIGFILE
