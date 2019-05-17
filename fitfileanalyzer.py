#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

#qpy:console
#qpy:2

""" fitfileanalyzer.py
With this Script you can ...
return codes:
0 = ok
1 = argument given, but nothing found
2 = No Argument given and Defaultlocation does not exist
6 = Arguments given but not a fitfiles found

release infos:
0.01: first version

"""

__version__ = '0.01'
__author__ = 'telemaxx'

import os
import sys
import argparse
import datetime
import time
import glob
import codecs
import io
from fitparse import FitFile, FitParseError

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

#try to detect QPython on android
ROA = True
try: #check if android and import gui tools
    import androidhelper.sl4a as sl4a # try new location
except: #otherwise its not android or old location
    #print('not qpython 3.6 or QPython 2')
    ROA = None
if not ROA:
    ROA = True
    try:
        import sl4a # try old location
    except:
        #print('not qpython 3.2')
        ROA = None

DEFAULT_MANUFACTURER = u'Garmin-corrected' # used, when no manufacturer given or manufacturer is set garmin by oruxmaps
DEFAULT_EVENT_TYPE = u'Cycling'
WAIT_AFTER_JOB_DONE = 10

# Directory where the FIT Files are located
if ROA: # android
    FIT_DEFAULT_PATH = os.path.abspath(os.path.join(os.sep,'sdcard','Documents','LezyneGpsAlly','6745th'))
else:
    # HOME stands for youre homedirectory e.g /home/pi 
    HOME = os.path.expanduser('~')
    FIT_DEFAULT_PATH = os.path.join(HOME,'BTSync','SA5','Documents','LezyneGpsAlly','6745th')

    

def main():
    global verbosity, also_unknown
    starttime = time.time()
    parser = argparse.ArgumentParser(description='The fitfilerenamer tool',epilog = '%(prog)s {version}'.format(version=__version__))
    parser.add_argument('-v', '--verbosity', type = int, choices = range(0,3), default=1, help='0= silent, 1= a bit output, 2= many output')
    parser.add_argument('fit_files_or_folder',nargs="*",  help='w/o default Dir is used')
    parser.add_argument('-i', '--ignore_crc', action = 'store_false', help='no crc check')
    parser.add_argument('-u', '--also_unknown', action = 'store_false', help='write also fields which starts with unknown')
    arguments = vars(parser.parse_args())
    args = arguments['fit_files_or_folder']
    verbosity = arguments['verbosity']
    ignore_crc = arguments['ignore_crc']
    also_unknown = arguments['also_unknown']

    #    (optionen, args) = parser.parse_args()
    #Iprint('Argumentlength %s' % (len(args)))
    if ROA:
        Dprint('Android (qpython) detectet')
        droid = sl4a.Android()
    else:
        Dprint('Android not detectet')

    if len(args) == 1:
        Dprint("Looking for File or Directory: %s" % args[0])
        if args[0][-4:].lower()=='.fit' and os.path.isfile(args[0]): # if the one argument is a file, create a list with one entry
            filelist = [args[0]]
        elif os.path.isdir(args[0]): #if the one argument is a dir, create a list with the fit files
            Dprint("argument given, it is a directory: %s" % (args[0]))
            filelist = create_filelist(args[0])
        else:
            Iprint('argument given, but nothing found')
            final_message('wait %d sec or press strg c' % (WAIT_AFTER_JOB_DONE))
            sys.exit(1)

    elif  len(args) == 0: # no argument given
        Dprint('No argument, looking at default Path: %s' % (FIT_DEFAULT_PATH))
        if os.path.isdir(FIT_DEFAULT_PATH):
            Dprint('No argument, but default path exist: %s' % (FIT_DEFAULT_PATH))
            filelist = create_filelist(FIT_DEFAULT_PATH)
        else: # no argument and no defaultlocation found
            Iprint("No Argument given and Defaultlocation does not exist: %s" % (FIT_DEFAULT_PATH))
            final_message('wait %d sec or press strg c' % (WAIT_AFTER_JOB_DONE))
            sys.exit(2)
    else: # more than 1 arguments, todo: filtering *.fit
        Dprint('much arguments.  %d' % (len(args)))
        filelist = []
        for next_file in args:
            if next_file[-4:].lower()=='.fit' and os.path.isfile(next_file):
                Dprint('file %s' % (next_file))
                filelist.append(next_file)
        if len(filelist) == 0:
            Iprint('Arguments given but not a fitfiles found')
            final_message('wait %d sec or press strg c' % (WAIT_AFTER_JOB_DONE))
            sys.exit(6)
    Dprint('fitfiles: %s' % (filelist))

    n = len(filelist)
    if ROA:
        # create progressbar for download
        droid.dialogCreateHorizontalProgress(
        'Analyzing and Renaming',
        'please be patient',
        n)
        droid.dialogShow()
        Dprint('creating progressbar')

    Iprint('please be patient, i am parsing. This can take a minute')

    file_count = skipped_count = analyzed_count = simulated_count = skipped_defective_count = 0
    for file in filelist:
        Dprint('processing %s' % (file))
        Dprint('start datafitprocessor')
        if not os.path.isfile(file):
            Iprint('skipping folder: %s' % (file))
            continue
        try:
            fitfile = FitFile(file, check_crc = ignore_crc)
            Dprint('parsing start')
            fitfile.parse()
            Dprint('parsing done')
        except FitParseError as e:
            Iprint('skipping defective fitfile %s' % (file))
            skipped_defective_count +=1
            for m in e.args:
                Dprint('Exception: %s' % (m))
            continue
        #Dprint('rename arguments: %s , %s , %d' % (fitfile, file, file_count))
        analyzestatus = analyze_fitfile(fitfile, file, file_count)
        if   analyzestatus == 'done':
            analyzed_count += 1
        elif analyzestatus == 'simulated_renaming':
            simulated_count +=1
        elif analyzestatus == 'skipped':
            skipped_count +=1
        if ROA:
            droid.dialogSetCurrentProgress(file_count + 1)
        file_count += 1
    difftime = time.time() - starttime
    Iprint('finished processing %d file(s) in %d seconds' % (file_count, difftime))
    summary = 'analyzed: %d, skipped defective: %d' % (analyzed_count, skipped_defective_count)
    Iprint(summary)
    if ROA:
        droid.dialogDismiss()
        title='I have processed %d File(s) in %d seconds' % (file_count, difftime)
        droid.dialogCreateAlert(title, summary)
        droid.dialogSetPositiveButtonText('OK')
        droid.dialogShow()
        dummy = droid.dialogGetResponse().result
    else:
        final_message('wait %d sec or press strg c' % (WAIT_AFTER_JOB_DONE))

def Dprint(text2print):
    if verbosity == 2:
        print(u"" + text2print)

def Iprint(text2print):
    if verbosity != 0:
        print(u"" + text2print)


def get_alldata(messages):
    my_enh_alt_max = 0.0
    my_manufacturer = DEFAULT_MANUFACTURER
    my_eventtype = DEFAULT_EVENT_TYPE
    my_timestamp = None
    for m in messages:
        fields = m.fields
        for f in fields:
            # the old "get_enhanced_altitude(messages)"
            if f.name == 'total_ascent' and f.value != None:
                if f.value > my_enh_alt_max:
                    my_enh_alt_max = f.value  
    
            #the old "get_manufacturer(messages)"
            if f.name == 'manufacturer':
                if f.value == None or isinstance(f.value,int):
                    #Iprint('manufacteur was None')
                    my_manufacturer = DEFAULT_MANUFACTURER
                else:
                    my_manufacturer = f.value
            
            #the old "get_event_type(messages)"
            if f.name == 'sport':
                event_type = f.value
             
            # the old "get_timestamp(messages)"
            if f.name == 'time_created':
                if isinstance(f.value,int):
                    Dprint('timestamp is integer: %d' % (f.value))
                    my_timestamp = None
                else:
                    my_timestamp = f.value
    return  my_timestamp , str(int(float(my_enh_alt_max))) , my_manufacturer , my_eventtype
    
def create_filelist(dir):
    fit_files = glob.glob(os.path.join(dir,'*.[fF][iI][tT]'))
    return(fit_files)

def final_message(msg):
    Iprint(msg)
    if verbosity > 0:
        try:
            time.sleep(WAIT_AFTER_JOB_DONE)
        except KeyboardInterrupt:
            pass

#(fitfile, file, file_count)
def analyze_fitfile(fitfile, original_filename = None, counter=0):
    global also_unknown

    messages = fitfile.messages

    timestamp , climb , manufacturer , event_type = get_alldata(messages)
    
    log_filename = original_filename.replace('.fit','.log')
    log_file = io.open(log_filename, 'w+', encoding='utf8')
    
    Iprint(u'start writing log file: %s' % log_filename)
    log_file.write(u'analyzing done, now writing logfile %s\n' % log_filename)
    
     #for record in fitfile.get_messages():
    for record in messages:
        Dprint(record.name)
        if (not also_unknown):  #records, write also unknown names
            #Iprint('writing also unkown record names')
            log_file.write(u'' + record.name + '\n')
        else: #still records, but dont write unkown names
            #Iprint('writing NOT unkown record names')
            if(not record.name.startswith('unknown')):
                log_file.write(u'' + record.name + '\n')
        if record.type == 'data':  #data
            for field_data in record:
                if (not also_unknown):  #data, write also unknown names
                    #Iprint('writing also unkown data names')
                    log_file.write(u' * %s: %s\n' % (field_data.name, field_data.value))
                    Dprint(' * %s: %s' % (field_data.name, field_data.value))
                else: #still data, dont write unknown
                    #Iprint('writing not unkown data names')
                    if(not field_data.name.startswith('unknown')):
                        log_file.write(u' * %s: %s\n' % (field_data.name, field_data.value))
                        Dprint(' * %s: %s' % (field_data.name, field_data.value))

    Dprint('orignal filename: %s' % original_filename)
    Dprint('log filename: %s' % log_filename)
    Dprint('timestamp: %s' % timestamp)
    Dprint('manufacturer: %s' % manufacturer)
    Dprint('event_type: %s' % event_type)
    Dprint('climb: %s' % climb)
    Dprint('enhanced_altitude %s' % (climb))
    Dprint('writing logfile done to: %s' % (log_filename))

    log_file.flush()
    log_file.write(u'writing logfile done to: %s' % (log_filename))
    log_file.close()

    Dprint ('-------------------')
    return('done')

if __name__=='__main__':
    main()


