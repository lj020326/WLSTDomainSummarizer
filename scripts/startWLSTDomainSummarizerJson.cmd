@ECHO ON

@REM Change the environment variables below to suit your target environment
@REM The WLST_OUTPUT_PATH and WLST_OUTPUT_FILE environment variables in this script
@REM determine the output directory and file of the script
@REM The WLST_OUTPUT_PATH directory value must have a trailing slash. If there is no trailing slash
@REM script will error and not continue.


SETLOCAL

@REM set WL_HOME=D:\product\FMW11g\wlserver_10.3
@REM set DOMAIN_HOME=D:\product\FMW11g\user_projects\domains\MyDomain
@REM set WLST_OUTPUT_PATH=D:\WLSTDomainSummarizer\output\
@REM set WLST_OUTPUT_FILE=WLST_Domain_Summary_Via_MBeans.html

set WL_HOME=D:\hosting\products\oracle\wls12210\wlserver
set DOMAIN_HOME=D:\hosting\configs\oracle\wls12210\domains\base_domain1
@REM set WLST_OUTPUT_PATH=D:\tmp\wlstdomainsummarizer\output\
set WLST_OUTPUT_PATH=.\..\output\
set WLST_OUTPUT_FILE=WLST_Domain_Summary_Via_MBeans.json

@REM from page 23 of
@REM http://docplayer.net/5620338-Understanding-the-weblogic-scripting-tool-12-1-3-12c-12-1-3.html
@REM http://www.oraworld.co.uk/weblogic-wlst-debugtrue-not-generating-debug-messages-not-working/

@REM set WLST_PROPERTIES="-Dweblogic.security.SSL.ignoreHostnameVerification=true, -Dweblogic.security.TrustKeyStore=DemoTrust"
@REM set WLST_PROPERTIES=" -Dwlst.debug.init=TRUE -Dwlst.offline.log.priority=debug -Dwlst.offline.log=/logs/test_wlst.log  weblogic.WLST"

call "%WL_HOME%\common\bin\wlst.cmd" StartDomainSummarizerJson.py

ENDLOCAL
