# WLST Domain Summarizer Script
# This script launches either the WLST online or offline collection script depending on whether a connection can be made to the Admin Server
# Author: Daniel Mortimer
# Proactive Support Delivery
# Date: 7th May 2013
# Version 001

#IMPORTS

# import types;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import os
import sys
import string
from java.lang import *
from java.util import Date

# START OF SCRIPT

# Collect and Store Domain Home, Output Directory and Output File Name

progname = sys.argv[0].split(".")[0]

# The recommendation is to stick this script off from a wrapper os script e.g cmd (Windows) or .sh (Unix)		
v_domainHome = os.environ["DOMAIN_HOME"];
v_outputFilePath = os.environ["WLST_OUTPUT_PATH"];
v_outputFile = os.environ["WLST_OUTPUT_FILE"];


# Check the variable values to see if they are empty or valid. If yes, ask for values
# We could write something more sophisicated here, but it's a start

if v_domainHome == '':
 	raise Exception ('domain_home not specified, quitting')

if v_outputFilePath== '':	
	v_outputFilePath = './'
if v_outputFile== '':	
	v_outputFile = "%s.log" % progname

if os.path.isdir(v_domainHome) == false:
 	raise Exception ('Invalid Domain Home. The path does not exist. Check the start summarizer cmd or sh file.')

if os.path.isdir(v_outputFilePath) == false:
 	raise Exception ('Invalid Output Directory. The path does not exist')

try:
	print "Ok, no problem running an offline collection";
	execfile('WLSDomainInfoOfflineJson.py');
except Exception, err:
	import traceback
	print "Unexpected Exception: [%s]" % err
	traceback.print_exc()

exit();



	


