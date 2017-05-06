# -----------------------------------------------
#  script to build a standalone app on MacOS 
#  run with   "python2.7 MarRISCo_MacOS_build.py"
# -----------------------------------------------

import os, sys
import shutil
from setuptools import setup

sys.argv.append('py2app')

APP = ['MaRISCo-X.py']
DATA_FILES = ['RGBA.tif']
OPTIONS = {'argv_emulation': True, 'iconfile': 'MaRISCo-X.icns',
           'excludes': ['numpy','xml','email','unittest','olefile',
           'packaging', 'distutils', 'Carbon', 'doctest', 'tarfile',
           'difflib', 'locale', 'threading', 'subprocess']}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

try:
    os.rename ('dist/MaRISCo-X.app', 'MaRISCo-X.app') # move app to actual dir
    shutil.rmtree('build')   # delete temp
    shutil.rmtree('dist')   # delete temp
    os.system ('rm MaRISCo-X.app/Contents/Frameworks/libcrypto*')
    os.system ('rm MaRISCo-X.app/Contents/Frameworks/libssl*')
    os.system ('rm MaRISCo-X.app/Contents/Frameworks/libiconv*') 
    os.system ('rm MaRISCo-X.app/Contents/Frameworks/libwebp*')     
    os.system ('rm MaRISCo-X.app/Contents/Resources/lib/python2.7/lib-dynload/pyexpat*')    
    os.system ('rm MaRISCo-X.app/Contents/Resources/lib/python2.7/lib-dynload/unicodedata.so')    
except: pass
os.system ("zip MaRISCo-X.zip -ry9 MaRISCo-X.app") # compress