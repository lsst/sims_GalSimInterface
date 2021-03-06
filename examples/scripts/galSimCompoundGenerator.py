"""
This script shows how to use our GalSim interface to create FITS images
that contain stars and galaxies
"""
from __future__ import print_function

import os
import galsim
from lsst.utils import getPackageDir
from lsst.sims.catalogs.db import CatalogDBObject
from lsst.sims.catUtils.utils import ObservationMetaDataGenerator
from lsst.sims.catUtils.baseCatalogModels import StarObj, GalaxyBulgeObj, GalaxyDiskObj, GalaxyAgnObj
from lsst.sims.GalSimInterface import LSSTCameraWrapper
from lsst.sims.GalSimInterface import SNRdocumentPSF, GalSimStars, GalSimGalaxies, \
                                               GalSimAgn

#if you want to use the actual LSST camera
#from lsst.obs.lsstSim import LsstSimMapper

class testGalSimStars(GalSimStars):
    #only draw images in the u and g band for speed
    bandpassNames = ['u','g']

    #convolve with a PSF; note that galaxies are not convolved with a PSF
    #PSF defined in galSimInterface/galSimUtilities.py
    PSF = SNRdocumentPSF()


class testGalSimGalaxies(GalSimGalaxies):
    bandpassNames = ['u', 'g']

    PSF = SNRdocumentPSF()


class testGalSimAgn(GalSimAgn):
    bandpassNames = ['u', 'g']

    #defined in galSimInterface/galSimUtilities.py
    PSF = SNRdocumentPSF()


#select an OpSim pointing
opsimdb = os.path.join(getPackageDir('sims_data'), 'OpSimData', 'opsimblitz1_1133_sqlite.db')
obs_gen = ObservationMetaDataGenerator(database=opsimdb)
obs_list = obs_gen.getObservationMetaData(obsHistID=10, boundLength=0.05)
obs_metadata = obs_list[0]

#grab a database of galaxies (in this case, galaxy bulges)
stars = CatalogDBObject.from_objid('allstars')

#now append a bunch of objects with 2D sersic profiles to our output file
stars_galSim = testGalSimStars(stars, obs_metadata=obs_metadata)
stars_galSim.camera_wrapper = LSSTCameraWrapper()

catName = 'galSim_compound_example.txt'
stars_galSim.write_catalog(catName, chunk_size=100)

print('done with stars')

bulges = CatalogDBObject.from_objid('galaxyBulge')
bulge_galSim = testGalSimGalaxies(bulges, obs_metadata=obs_metadata)

#This will make sure that the galaxies are drawn to the same images
#as the stars were.  It copies the GalSimInterpreter from the star
#catalog.  It also copies the camera.  The PSF in the GalSimInterpreter
#is updated to reflect the PSF in bluge_galSim
bulge_galSim.copyGalSimInterpreter(stars_galSim)

bulge_galSim.write_catalog(catName, write_header=False,
                            write_mode='a')

print('done with bulges')

disks = CatalogDBObject.from_objid('galaxyDisk')
disk_galSim = testGalSimGalaxies(disks, obs_metadata=obs_metadata)
disk_galSim.copyGalSimInterpreter(bulge_galSim)
disk_galSim.write_catalog(catName, write_header=False, write_mode='a')

print('done with disks')

agn = CatalogDBObject.from_objid('galaxyAgn')
agn_galSim = testGalSimAgn(agn, obs_metadata=obs_metadata)
agn_galSim.copyGalSimInterpreter(disk_galSim)
agn_galSim.write_catalog(catName, write_header=False, write_mode='a')

agn_galSim.write_images(nameRoot='compound')
