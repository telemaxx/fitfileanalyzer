# fitfileanalyzer.py

### Fitfile are sometime mystic...
...this tool writes the content of fitfiles in a redible logfile


### HOWTO INSTALL
  * 1st install python 2.7 or python 3 or pypy or 'qpython on android'
  * Install fitparse modul
    [Available here](http://dtcooper.github.com/python-fitparse/)
description some where below
  * download fitfileanalyzer.py and save it some where
  * create a shortcut on the Desktop. Target:
  `C:\yourepythonprogrammfolder\python.exe C:\thefolderwhereyousavethefile\fitfileanalyzer.py`
### HOWTO USE
##### There are three different ways to use this tool:
1. doubleclick the shortcut, the script looking for fit files in the defaultdirectory, defined inside the python file
```python
# Directory where the FIT Files are located
# HOME stands for youre homedirectory e.g /home/pi 
HOME = os.path.expanduser('~')
FIT_DEFAULT_PATH = os.path.join(HOME,'BTSync','SA5','Documents','LezyneGpsAlly','6745th')
```

2. drag and drop one or more fit files to the shortcut. this files are analyzed
3. drag and drop ONE folder to the shortcut. all fitfiles in the first level of that folder are analyzed

Note: This tool using the fitparse modul, powerfull but slow. So please be patient.
##### The options:
* getting help and display version: `C:\thefolderwhereyousavethefile\fitfileanalyzer.py -h`
* setting verbosity `C:\thefolderwhereyousavethefile\fitfileanalyzer.py -v[0-2]`
* ignoring wrong crc `C:\thefolderwhereyousavethefile\fitfileanalyzer.py -i`
* ignoring unknown field `C:\thefolderwhereyousavethefile\fitfileanalyzer.py -u`

### HOWTO install fitparse
the normal way is now working (the old way below)
##### with python2
```sh
$ C:\yourepythonprogrammfolder\scripts\pip.exe install fitparse
```
##### with python3:
```sh
$ C:\yourepythonprogrammfolder\scripts\pip3.exe install fitparse
```


* ~~the description on the project webpage did not worked for me so i do it this way:~~
* ~~go to the [project github page](https://github.com/dtcooper/python-fitparse)~~
* ~~click on "clone or download" and select "download zip"~~
* ~~unzip this file into a new folder~~
* ~~open a command prompt and change in that folder and execude the `setup.py`:~~
```sh
$ cd youredownloadfolder\python-fitparse
$ C:\yourepythonprogrammfolder\python.exe setup.py install
```
#### for pypy:
```sh
$ cd youredownloadfolder\python-fitparse
$ C:\yourepypyprogrammfolder\pypy.exe setup.py install
```
#### for qpython:
##### New:
use the integrated QPYPI -> TOOLS -> INSTALL WITH PYTHONS PYPI and enter:
pip3 install fitparse
or
pip install fitparse
(depending which python version you use.

~~from the unzipped folder copy the whole folder to:~~
~~/internal_sdcard/qpython/lib/python2.7/site-packages~~


### TIP
instead of using the standard python, use [pypy](https://pypy.org)   
With pypy the script runs about 5 times faster.   
startup time is longer, but after that is faster.   
On Windows, there is only the python2 compliant 32bit version. but that version is ok.   

