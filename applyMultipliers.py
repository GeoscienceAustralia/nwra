"""
Apply local site exposure multiplers (maximum of all directions) to a
smoothed regional wind hazard data.

This script will cycle through the available regional hazard layers and
combine with the site exposure multiplier tiles

Author: Craig Arthur
Created: 2023-10-16
"""

import os
import sys
import glob
import getpass
import argparse
import logging
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation

from osgeo import gdal
from osgeo import gdalconst
import numpy as np

from prov.model import ProvDocument

from process import pAlreadyProcessed, pWriteProcessedFile, pArchiveFile, pInit
from files import flStartLog, flGetStat, flSize, flGitRepository
from files import flModDate, flPathTime

gdal.UseExceptions()

LOGGER = logging.getLogger()
DATEFMT = "%Y-%m-%dT%H:%M:%S"

prov = ProvDocument()
prov.set_default_namespace("")
prov.add_namespace("prov", "http://www.w3.org/ns/prov#")
prov.add_namespace("xsd", "http://www.w3.org/2001/XMLSchema#")
prov.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")
prov.add_namespace("void", "http://vocab.deri.ie/void#")
prov.add_namespace("dcterms", "http://purl.org/dc/terms/")
prov.add_namespace("git", "http://github.com/GeoscienceAustralia")
prov.add_namespace("nwra", "http://www.ga.gova.au/hazards")
provlabel = ":LocalHazardGeneration"
provtitle = "Local wind hazard generation"


def start():
    """
    Parse command line arguments, initiate the processing module and start
    the main loop.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config_file",
        help="Configuration file")
    parser.add_argument(
        "-v", "--verbose",
        help="Print verbose output to STDOUT")
    args = parser.parse_args()

    configFile = args.config_file
    verbose = args.verbose
    config = ConfigParser(
        allow_no_value=True,
        interpolation=ExtendedInterpolation())

    config.optionxform = str
    config.read(configFile)
    config.configFile = configFile

    pInit(configFile)
    main(config, verbose)


def main(config: str, verbose=False):
    """
    Start logger and call the loop to process source files.

    :param config: `ConfigParser` object with configuration loaded
    :param boolean verbose: If `True`, print logging messages to STDOUT
    """

    logfile = config.get("Logging", "LogFile")
    loglevel = config.get("Logging", "LogLevel", fallback="INFO")
    verbose = config.getboolean("Logging", "Verbose", fallback=verbose)
    datestamp = config.getboolean("Logging", "Datestamp", fallback=False)
    LOGGER = flStartLog(logfile, loglevel, verbose, datestamp)
    outputDir = config.get("Output", "Path", fallback="")
    starttime = datetime.now().strftime(DATEFMT)
    commit, tag, dt, url = flGitRepository(sys.argv[0])

    prov.agent(
        sys.argv[0],
        {
            "dcterms:type": "prov:SoftwareAgent",
            "git:commit": commit,
            "git:tag": tag,
            "dcterms:date": dt,
            "prov:url": url,
        },
    )

    # We use the current user as the primary agent:
    useragent = prov.agent(f":{getpass.getuser()}", {"prov:type": "prov:Person"})

    orgagent = prov.agent(
        "GeoscienceAustralia",
        {
            "prov:type": "prov:Organisation",
            "foaf:name": "Geoscience Australia"},
    )
    prov.actedOnBehalfOf(useragent, orgagent)

    configent = prov.entity(
        ":configurationFile",
        {
            "dcterms:title": "Configuration file",
            "dcterms:type": "foaf:Document",
            "dcterms:format": "Text file",
            "prov:atLocation": os.path.basename(config.configFile),
        },
    )

    ListAllFiles(config)
    processFiles(config)

    endtime = datetime.now().strftime(DATEFMT)
    processingact = prov.activity(
        provlabel,
        starttime,
        endtime,
        {"dcterms:title": provtitle, "dcterms:type": "void:Dataset"},
    )

    prov.wasAttributedTo(processingact, f":{getpass.getuser()}")
    prov.actedOnBehalfOf(f":{getpass.getuser()}", "GeoscienceAustralia")
    prov.used(provlabel, configent)
    prov.used(provlabel, "nwra:smoothedregionalwindrasters")
    prov.wasAssociatedWith(processingact, sys.argv[0])

    prov.serialize(os.path.join(outputDir, "applymultipliers.xml"), format="xml")

    for key in g_files.keys():
        LOGGER.info(f"Processed {len(g_files[key])} {key} files")
    LOGGER.info("Completed")


def ListAllFiles(config):
    """
    For each item in the 'Categories' section of the configuration file, load
    the specification (glob) for the files, then pass to `expandFileSpecs`

    :param config: `ConfigParser` object
    """
    global g_files
    g_files = {}
    categories = config.items("Categories")
    for idx, category in categories:
        specs = []
        items = config.items(category)
        for k, v in items:
            if v == "":
                specs.append(k)
        expandFileSpecs(config, specs, category)


def expandFileSpec(config, spec, category):
    """
    Given a file specification and a category, list all files that match the
    spec and add them to the :dict:`g_files` dict.
    The `category` variable corresponds to a section in the configuration file
    that includes an item called 'OriginDir'.
    The given `spec` is joined to the `category`'s 'OriginDir' and all matching
    files are stored in a list in :dict:`g_files` under the `category` key.

    :param config: `ConfigParser` object
    :param str spec: A file specification. e.g. '*.*' or 'IDW27*.txt'
    :param str category: A category that has a section in the source
        configuration file
    """
    if category not in g_files:
        g_files[category] = []

    origindir = config.get(
        category, "OriginDir", fallback=config.get("Defaults", "OriginDir")
    )
    dirmtime = flPathTime(origindir)
    specent = prov.collection(
        f":{spec}",
        {
            "dcterms:type": "prov:Collection",
            "dcterms:title": category,
            "prov:atLocation": origindir,
            "prov:GeneratedAt": dirmtime,
        },
    )
    prov.used(provlabel, specent)
    specpath = os.path.join(origindir, spec)
    files = glob.glob(specpath)
    entities = []
    LOGGER.info(f"{len(files)} {spec} files to be processed")
    for file in files:
        if os.stat(file).st_size > 0:
            if file not in g_files[category]:
                g_files[category].append(file)
                entities.append(
                    prov.entity(
                        f":{os.path.basename(file)}",
                        {
                            "prov:atLocation": origindir,
                            "dcterms:created": flModDate(file),
                        },
                    )
                )
    for entity in entities:
        prov.hadMember(specent, entity)


def expandFileSpecs(config, specs, category):
    """
    Expand a collection of file specifications

    :param config: `ConfigParser` object
    :param list specs: list of file specifications to expand
    :param str category: A category that has a section in the source
        configuration file
    """
    for spec in specs:
        expandFileSpec(config, spec, category)


def processFiles(config):
    """
    Process a list of files in each given category

    :param config: :class:`ConfigParser` instance
    """
    global g_files
    unknownDir = config.get("Defaults", "UnknownDir")
    defaultOriginDir = config.get("Defaults", "OriginDir")
    deleteWhenProcessed = config.getboolean(
        "Files", "DeleteWhenProcessed", fallback=False
    )
    archiveWhenProcessed = config.getboolean(
        "Files", "ArchiveWhenProcessed", fallback=False
    )
    outputDir = config.get("Output", "Path", fallback=unknownDir)
    LOGGER.debug(f"DeleteWhenProcessed: {deleteWhenProcessed}")
    LOGGER.debug(f"Output directory: {outputDir}")

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    category = "RegionalHazard"
    originDir = config.get(category, "OriginDir", fallback=defaultOriginDir)
    LOGGER.debug(f"Origin directory: {originDir}")

    for f in g_files[category]:
        LOGGER.info(f"Processing {f}")
        directory, fname, md5sum, moddate = flGetStat(f)
        if pAlreadyProcessed(directory, fname, "md5sum", md5sum):
            LOGGER.info(f"Already processed {f}")
        else:
            if processFile(f, config):
                LOGGER.info(f"Successfully processed {f}")
                pWriteProcessedFile(f)
                if archiveWhenProcessed:
                    pArchiveFile(f)
                elif deleteWhenProcessed:
                    os.unlink(f)


def processFile(filename, config):
    """
    Process a file and store the data in the output directory. The list of
    multiplier files has already been compiled previously (in the call to
    `expandFileSpecs`). Here we are looping over the files in the `Multiplier`
    category for a given regional wind hazard file (which we cycle through
    in `processFiles`)

    :param str filename: File path for a regional wind hazard file
    :param config: :class:`ConfigParser` object
    """
    unknownDir = config.get("Defaults", "UnknownDir")
    outputDir = config.get("Output", "Path", fallback=unknownDir)
    filebase = os.path.splitext(os.path.basename(filename))[0]
    category = "Multipliers"
    # Set the return code `rc` to True. If a file is not processed properly,
    # then set it to False.
    rc = True
    vrtfiles = []
    for mfile in g_files[category]:
        outputFile = os.path.join(outputDir, filebase, os.path.basename(mfile))

        if not os.path.exists(os.path.join(outputDir, filebase)):
            os.makedirs(os.path.join(outputDir, filebase))
        rcp = process(filename, mfile, outputFile)
        if not rcp:
            rc = rcp
        else:
            vrtfiles.append(outputFile)

    vrtopts = gdal.BuildVRTOptions(resampleAlg='bilinear')
    vrtFileName = os.path.join(outputDir, filebase, f"{filebase.replace('smooth', 'local')}.vrt")
    try:
        gdal.BuildVRT(vrtFileName, vrtfiles, options=vrtopts)
    except:
        LOGGER.exception(f"Cannot create VRT file {vrtFileName}")

    return rc

def process(regional_raster: str, multiplier: str, output_raster: str):
    """
    Combine the regional hazard and the local site exposure multipliers

    :param str regional_raster: Path for the regional hazard file
    :param str multiplier: Path for the site exposure multiplier tile
    :param str output_raster: Path for the output raster dataset

    :return: Returns `True` if successful, `False` otherwise
    :rtype: boolean
    """
    # Open the input raster datasets
    ds1 = gdal.Open(regional_raster, gdal.GA_ReadOnly)
    ds2 = gdal.Open(multiplier, gdal.GA_ReadOnly)

    if ds1 is None or ds2 is None:
        LOGGER.exception("Error: One or both input datasets could not be opened.")
        return False

    # Read the data from the input rasters into NumPy arrays
    data1 = ds1.ReadAsArray()
    data2 = ds2.GetRasterBand(1).ReadAsArray()

    LOGGER.debug("Get geotransform and projection info from input rasters")
    geotransform1 = ds1.GetGeoTransform()
    geotransform2 = ds2.GetGeoTransform()
    src_proj = ds1.GetProjection()
    match_proj = ds2.GetProjection()

    LOGGER.debug("Resample data1 to match the resolution and extent of data2")
    resampled_data1 = np.empty(data2.shape, dtype=np.float32)
    tmpdrv = gdal.GetDriverByName("MEM")
    tmpds = tmpdrv.Create(
        "",
        ds2.RasterXSize,
        ds2.RasterYSize,
        1,
        gdal.GDT_Float32
        )
    tmpds.SetGeoTransform(geotransform2)
    tmpds.SetProjection(match_proj)
    gdal.ReprojectImage(ds1, tmpds, src_proj, match_proj, gdalconst.GRA_Bilinear)
    resampled_data1 = tmpds.GetRasterBand(1).ReadAsArray()

    LOGGER.debug("Apply the mask to multiplier data")
    data2 = np.where(data2 < 0, 1, data2)

    # Perform the multiplication
    result = resampled_data1 * data2

    LOGGER.debug(f"Create the output raster: {output_raster}")
    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(
        output_raster, ds2.RasterXSize, ds2.RasterYSize, 1, gdal.GDT_Float32,
        options=['COMPRESS=LZW']
    )

    LOGGER.debug("Set the geotransform and projection for the output raster")
    output_ds.SetGeoTransform(geotransform2)
    output_ds.SetProjection(match_proj)
    output_dsBand = output_ds.GetRasterBand(1)
    output_dsBand.SetNoDataValue(-9999)

    # Write the result array to the output raster
    output_ds.GetRasterBand(1).WriteArray(result)

    # Close the raster datasets
    ds1 = None
    ds2 = None
    output_ds = None

    LOGGER.info(f"Local wind hazard saved to {output_raster}")
    return True


start()