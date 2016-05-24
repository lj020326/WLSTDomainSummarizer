# Prototype Script to perform WLST offline collection of managed server config MBeans
# The script retrieves a selection of config MBeans values. The values are printed as part of a HTML file which is built dynamically by this script.
# Author: Daniel Mortimer
# Proactive Support Delivery
# Date: 7th May 2013
# Version 007


## to write to json - see
## http://docs.oracle.com/middleware/1213/wls/WLPRG/java-api-for-json-proc.htm#WLPRG1060

#IMPORTS

# import types;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import os;
import string;

import javax.json.Json as Json
import java.io.StringWriter as StringWriter

# START OF FUNCTIONS

## python equiv to mysql ifnull()
def ifnull(var, val):
    if var is None:
        return val
    return var


# function to help locate whether MBean directory exists. 
# This does not perform a global search. It just checks whether a given MBean directory exists at the level the script is currently in 
def findMBean(v_pattern):
    # get a listing of everything in the current directory
    mydirs = ls(returnMap='true')
    v_compile_pattern = java.util.regex.Pattern.compile(v_pattern);
    found = 'false';
    for mydir in mydirs:
        x = java.lang.String(mydir);
        v_matched = v_compile_pattern.matcher(x);
        if v_matched.find():
            found = 'true';
        return found;

# function to strip the Bean Value which is returned as tuple (list). 
# We only want to return and print the target name and type
def stripMBeanValue (v_mbeanvalue):

    v_check_value = str(v_mbeanvalue);
    v_strippedValue01 = String.replace(v_check_value,'Proxy for ','');
    v_strippedValue02 = String.replace(v_strippedValue01,'Name=','');
    v_strippedValue03 = String.replace(v_strippedValue02,'Type=','');
    v_strippedValue04 = String.replace(v_strippedValue03,':',' ');
    v_strippedValue = v_strippedValue04.split();
    return v_strippedValue;

# END OF FUNCTIONS

# START OF SCRIPT

#debug("true")
# WLS.commandExceptionHandler.setSilent(1)
WLS.commandExceptionHandler.setSilent(1)
redirect('./wlst.log')

# Collect and Store Domain Home, Output Directory and Output File Name

v_domainHome = os.environ["DOMAIN_HOME"];

if v_domainHome == '':
    v_domainHome = raw_input('Enter DOMAIN_HOME, specify full path: ');

if os.path.isdir(v_domainHome) == false:
    raise Exception ('Invalid Domain Home. The path does not exist.')


#Some WLST commands throw output to stdout
#For a cleaner user experience we redirect that stuff to log in the online py file
#Unfortunately redirect function is not supported when WLST is in offline mode :-(
# e.g redirect('wlstonlinedomainsummarizer.log', 'false'); will not work

# Read in the Domain Configuration

print "v_domainHome=[%s]" % v_domainHome
readDomain(v_domainHome);

# OPEN the output HTML file and start to write to it

f = open(v_outputFilePath  + v_outputFile, 'w');

# BUILD the HTML, header includes javascript and css to enable table styling and sorting

## see more info to construct json in java
## http://docs.oracle.com/javaee/7/api/javax/json/JsonObject.html

model = Json.createObjectBuilder()

print "Scanning Domain Information"

domainNode = Json.createObjectBuilder()

v_DomainName = get('Name');
v_DomainVersion = get('DomainVersion');
v_ProductionModeEnabled = get('ProductionModeEnabled');

if v_ProductionModeEnabled == 0:
    v_ProductionModeEnabled = 'False';
else:
    v_ProductionModeEnabled = 'True';

v_ConsoleEnabled = get('ConsoleEnabled');

if v_ConsoleEnabled == 0:
    v_ConsoleEnabled = 'False';
else:
    v_ConsoleEnabled = 'True';

v_ConsoleContextPath = get('ConsoleContextPath');

domainNode.add("Domain Name", v_DomainName)
domainNode.add("Version", v_DomainVersion)
domainNode.add("Production Mode Enabled", v_ProductionModeEnabled)
domainNode.add("Console Enabled?", v_ConsoleEnabled)
domainNode.add("Console Context Path", v_ConsoleContextPath)

model.add("Domain Information", domainNode)

print "Scanning Server Info"

serverCollectionNode = Json.createArrayBuilder()

cd ('Server');
myservers = ls(returnMap='true');

# Here is where we loop through the servers in the tree,
# Note: we do not store the MBean values in an array, for simplicity we print the MBean value as soon as we have retrieved it

for myserver in myservers:

    serverNode = Json.createObjectBuilder()

    x_server = java.lang.String(myserver);
    print "Scanning Server Info for server [%s]" % x_server

    cd(x_server);

    v_Cluster = get('Cluster');
    v_Cluster = stripMBeanValue(v_Cluster);

    v_ListenAddress = get('ListenAddress');
    v_ListenPort = get('ListenPort');

    v_Machine = get('Machine');
    v_Machine = stripMBeanValue(v_Machine);

    v_JavaCompilerPreClassPath = get('JavaCompilerPreClassPath');
    v_JavaCompilerPostClassPath = get('JavaCompilerPostClassPath');

    v_check_SSLexists = findMBean('SSL');
    v_check_CustomNetwork = findMBean('NetworkAccessPoint');

    print "Scanning Server Info - finished initial scan1"

    # Check to see if the Server has a SSL MBean Branch .. if yes we will try to find the SSL Listen Port
    if v_check_SSLexists == 'true':
        print "Scanning Server Info - SSL exists..."
        cd ('SSL');
        cd ('NO_NAME_0');

        print "Scanning Server Info - getting listenport..."
        try:
            # v_SSL_ListenPort = get('ListenPort');
            v_SSL_ListenPort = "null";
        except WLSTException, e:
            # The exception will still display to standard out, which may cause alarm
            # So adding this message telling the user the exception is expected and can be ignored
            v_SSL_ListenPort = "null";
            print "IGNORE this exception1 [%s]" % e
            pass
        except Exception, e:

            # The exception will still display to standard out, which may cause alarm
            # So adding this message telling the user the exception is expected and can be ignored
            v_SSL_ListenPort = "null";
            print "IGNORE this exception2 [%s]" % e
            pass

        v_check_SSLexists = '';
        # v_SSL_ListenPort = get('ListenPort');
        cd ('../../');
    else:
        v_SSL_ListenPort = "SSL not enabled";


    serverNode.add("Server Name",x_server)
    serverNode.add("Cluster",v_Cluster[0])
    serverNode.add("Machine",v_Machine[0])

    defaultNetworkNode = Json.createObjectBuilder()
    customNetworkArray = Json.createArrayBuilder()

    defaultNetworkNode.add("Listen Address",v_ListenAddress)
    defaultNetworkNode.add("Listen Port",v_ListenPort)
    defaultNetworkNode.add("SSL Listen Port",v_SSL_ListenPort)

    serverNode.add("Default Network Info", defaultNetworkNode)

    serverNode.add("JavaCompilerPreClassPath",ifnull(v_JavaCompilerPreClassPath,"None"))
    serverNode.add("JavaCompilerPostClassPath",ifnull(v_JavaCompilerPostClassPath,"None"))

    print "Scanning Server Info - finished initial scan2"

    # Check to see if the Server has a NetAccessPoint branch .. if yes we will try to find custom network channel information
    if v_check_CustomNetwork == 'true':
        print "Scanning Server Info - checking custom network info"

        cd ('NetworkAccessPoint');
        customNetChannels = ls(returnMap='true');

        # Obtain the number of custom network channels configured against a server
        # We need this value to set the rowspan HTML attribute
        v_no_of_netchannels = len(customNetChannels);

        # Set a flag to help determine whether we print sub rows if there are multiple channels
        v_count03 = 'false';
        # customNetworkNode.add("Number of Net Channels",v_no_of_netchannels)

        # Loop through the Custom Network channels and retrieve some MBean values
        for customNetChannel in customNetChannels:

            customNetChannelNode = Json.createObjectBuilder()

            v_CustomNetworkName = java.lang.String(customNetChannel);
            cd (v_CustomNetworkName);
            v_CustomNetworkAddress = get('ListenAddress');
            v_CustomNetworkPort = get('ListenPort');
            v_CustomProtocol = get('Protocol');

            customNetChannelNode.add("CustomNetworkName",v_CustomNetworkName)
            customNetChannelNode.add("CustomNetworkAddress",v_CustomNetworkAddress)
            customNetChannelNode.add("CustomProtocol",v_CustomProtocol)
            customNetChannelNode.add("CustomNetworkPort",v_CustomNetworkPort)

            customNetworkArray.add(customNetChannelNode)

            # Back to NetworkAccessPoint
            cd ('../');


        serverNode.add("Custom Networks",customNetworkArray)

        #Back to Server/Servername
        cd ('../');

    serverCollectionNode.add(serverNode)

    #Back to Servers
    v_check_CustomNetwork = 'false';
    cd ('../');

model.add("Server Information", serverCollectionNode)

print "Finished Server scan"

# Return to MBean Tree Root
cd ('..');


# CHANGE to the Cluster MBean tree, loop through the clusters printing a selection of MBean values

clusterArray = Json.createArrayBuilder()

print "Scanning Cluster Information"

# Initialize Server in Cluster list
v_build_server_in_cluster_list = [];

# Check if Cluster MBean Directory exists

v_didyoufindit = 'Dummy Value';
v_didyoufindit = findMBean('Cluster');


if v_didyoufindit == 'true':
    cd ('Cluster');
    myclusters = ls(returnMap='true');

    for mycluster in myclusters:

        clusterNode = Json.createObjectBuilder()

        v_build_server_in_cluster_list = [];
        x_cluster = java.lang.String(mycluster);


        cd(x_cluster);

        v_ClusterMessagingMode = get('ClusterMessagingMode');
        v_WebLogicPluginEnabled = get('WebLogicPluginEnabled');
        v_ClusterAddress = get('ClusterAddress');
        v_MulticastAddress = get('MulticastAddress');
        v_MulticastPort = get('MulticastPort');

        # Now let's get the server names in the cluster
        cd ('../../');
        cd ('Server');



        for myserver in myservers:
            x_server = java.lang.String(myserver);
            # print x_server;
            cd(x_server);
            v_Cluster = get('Cluster');
            v_Cluster = stripMBeanValue(v_Cluster);
            v_check_cluster_value = java.lang.String(v_Cluster[0]);

            if v_check_cluster_value == x_cluster:
                v_build_server_in_cluster_list.append(x_server);
                # print v_build_server_in_cluster_list;
            cd ('../');


        # Back to the Cluster tree again

        cd ('../');
        cd ('Cluster');

        # Initialize loop count flag
        v_count01 = '';

        # We need to know length of cluster list to set the HTML rowspan value
        v_no_of_servers = len(v_build_server_in_cluster_list)

        clusterNode.add("Cluster Name",x_cluster)
        clusterNode.add("Cluster Address",ifnull(v_ClusterAddress,"None"))
        clusterNode.add("Cluster Messaging Mode",v_ClusterMessagingMode)
        clusterNode.add("Multicast Address",v_MulticastAddress)
        clusterNode.add("Multicast Port>",v_MulticastPort)
        clusterNode.add("WebLogicPluginEnabled",v_WebLogicPluginEnabled)

        if v_no_of_servers > 0:
            clusterServerArray = Json.createArrayBuilder()

            for value in v_build_server_in_cluster_list:
                clusterServerNode= Json.createObjectBuilder()
                clusterServerNode.add("Server",value)
                clusterServerArray.add(clusterServerNode)

            clusterNode.add("Servers In Cluster",clusterServerArray)

        clusterArray.add(clusterNode)

    v_didyoufindit = '';
    # Return to MBean Tree Root
    cd ('..');

else:
    print "No Clusters are configured in this domain";
    v_didyoufindit = '';
    # Return to MBean Tree Root
    cd ('..');

model.add("Cluster Information",clusterArray)
print "Finished Cluster scan"

# CHANGE to the Machines MBean tree, loop through the Machines Resources printing a selection of MBean values

print "Scanning for Machines (NodeManager) info"

machinesArray = Json.createArrayBuilder()

v_didyoufindit = findMBean('AnyMachine');

if v_didyoufindit == 'true':
    cd ('Machines')
    mymachines = ls(returnMap='true');

    for mymachine in mymachines:

        machineNode = Json.createObjectBuilder

        x_machine = java.lang.String(mymachine);
        machineNode.add("Machine Name", x_machine)

        cd (x_machine);


        # Some machines do not have a Node Manager association and therefore no Node Manager MBean tree to traverse
        # Need to check for this

        v_check_path01 = findMBean('NodeManager');

        if v_check_path01 == 'true':
            cd ('NodeManager');

            #Some setups have a different path to the NM ListenAddress and ListenPort
            #Need to check for this
            v_check_path02 = findMBean('NodeManager');

            if v_check_path02 == 'true':
                cd ('NodeManager');
            else:
                cd (x_machine);

            v_MachineListenAddress = get('ListenAddress');
            v_MachineListenPort = get('ListenPort');

            machineNode.add("Listen Address", v_MachineListenAddress)
            machineNode.add("Listen Port", v_MachineListenPort)

            cd ('../../../');
        else:
            machineNode.add("Listen Address", "Not Available (No NodeManager associated with this machine)")
            machineNode.add("Listen Port", "Not Available (No NodeManager associated with this machine)")

            cd ('../');

    machinesArray.add(machineNode)

    v_didyoufindit = '';

else:
    print "No Machines are configured within this domain.";
    v_didyoufindit = '';


model.add("Machine Information", machinesArray)

# Return to MBean Tree Root
cd ('../');

print "Finished scanning machine info"


# CHANGE to the JDBC MBean tree, loop through the JDBC Resources printing a selection of MBean values

print "Scanning JDBC System Resources"

# Check if JDBC System Resource MBean Directory exists
print "Scanning JDBC Data Source System Resources"

v_didyoufindit = findMBean('JDBCSystemResource');

#Initializing variables which are use to flag whether data source is Multi and if yes, to collect data
v_MultiSourceFlag = 'false';
v_isMultiLink = 'false';

jdbcResourcesNode = Json.createObjectBuilder()
jdbcResourcesArray = Json.createArrayBuilder()

if v_didyoufindit == 'true':

    cd ('JDBCSystemResource');
    myjdbcresources = ls(returnMap='true');

    for myjdbcresource in myjdbcresources:

        jdbcResourceNode = Json.createObjectBuilder()

        x_jdbc = java.lang.String(myjdbcresource);

        v_JDBC_Type = 'Generic';

        # Change to the JDBC Resource
        cd(x_jdbc);

        # If a resource has no targets, the get will fail with an error, so we need to code for this scenario
        try:
            v_any_targets = '';
            v_jdbc_target = get('Target');

            # Even if the get fails, the variable is assigned a value of none, set the flag variable accordingly
            if v_jdbc_target == 'None':
                v_any_targets = 'None';
                v_no_of_targets = 1;
            else:
                # If the get has succeeded then set flag accordingly and obtain length of array returned by the get
                # The array length will be used to determine the HTML rowspan value

                v_any_targets ='Use v_jdbc_target';
                v_no_of_targets = len(v_jdbc_target);

        except:

            # Setting flag and rowspan variable here as well .. belt and braces
            v_any_targets = 'None';
            v_no_of_targets = 1;

            # The exception will still display to standard out, which may cause alarm
            # So adding this message telling the user the exception is expected and can be ignored
            print "IGNORE this exception";


        # Get the other attribute values
        cd ('JdbcResource');

        cd (x_jdbc);

        #If JDBCOracleParams is found we know this to be a Gridlink data source
        v_isGridLink = findMBean('JDBCOracleParams');

        #If JDBCDriverParams is not found then we know the Data Source must a multi source definition
        v_isMultiLink = findMBean('JDBCDriverParams');

        if v_isGridLink == 'true':
            v_JDBC_Type = 'Gridlink';

        if v_isMultiLink == 'false':
            v_JDBC_Type = 'Multi';
            v_MultiSourceFlag = 'true';
        else:

            ls();

            cd ('JDBCDriverParams');
            cd ('NO_NAME_0');
            v_DriverName = get('DriverName');
            v_JDBC_URL = get('URL');
            cd ('../../');

        cd ('JDBCDataSourceParams');
        cd ('NO_NAME_0');

        v_GlobalTransactionsProtocol = get('GlobalTransactionsProtocol');

        cd ('../../../../../');

        if v_JDBC_Type != 'Multi':

            jdbcResourceNode.add("JDBC Name",x_jdbc)
            jdbcResourceNode.add("JDBC Type",v_JDBC_Type)

            jdbcResourceNode.add("Driver Name",v_DriverName)
            jdbcResourceNode.add("Global Transactions Protocol",v_GlobalTransactionsProtocol)
            jdbcResourceNode.add("JDBC URL",v_JDBC_URL)

            if v_any_targets == 'Use v_jdbc_target':

                v_count02 = 'false';


                jdbcTargetArray = Json.createArrayBuilder()

                for value in v_jdbc_target:

                    jdbcTargetNode = Json.createObjectBuilder
                    value = stripMBeanValue(value);
                    jdbcTargetNode.add("Target",value[0] +"-"+ value[2])
                    jdbcTargetArray.add(jdbcTargetNode)

                jdbcResourceNode.add("JDBC Target(s)", jdbcTargetArray)

    jdbcResourcesArray.add(jdbcResourceNode)

    v_didyoufindit = '';
    # Return to MBean Tree Root
    cd ('..');

else:
    print "No JDBC Data Sources are configured within this domain.";
    v_didyoufindit = '';
    # Return to MBean Tree Root
    cd ('..');


jdbcResourcesNode.add("JDBC Data Sources", jdbcResourcesArray)

jdbcResourcesArray = Json.createArrayBuilder()

print "Scanning JDBC Multi-Data Source System Resources"

# Print out the Multi Data Sources if they exist

if v_MultiSourceFlag == 'true':

    cd ('JDBCSystemResource');

    for myjdbcresource in myjdbcresources:

        jdbcResourceNode = Json.createObjectBuilder()

        x_jdbc = java.lang.String(myjdbcresource);

        cd (x_jdbc);
        cd('JdbcResource');
        cd (x_jdbc);
        cd('JDBCDataSourceParams/NO_NAME_0');

        v_DataSourceList00 = get('DataSourceList');

        # Return to MBean Tree Root
        cd ('../../../../../');

        if str(v_DataSourceList00) != 'None':

            #Data Sources List is returned as a comma delimited string.
            #We need to turn it into a list if we want to print the data in sub rows
            v_DataSourceList01 = String.replace(v_DataSourceList00,',',' ');
            v_DataSourceList = v_DataSourceList01.split();
            v_no_of_datasources = len(v_DataSourceList);

            jdbcResourceNode.add("JDBC Data Source Name",x_jdbc)
            jdbcTargetArray = Json.createArrayBuilder()

            for value in v_DataSourceList:
                jdbcTargetNode = Json.createObjectBuilder
                jdbcTargetNode.add("Target", value)
                jdbcTargetArray.add(jdbcTargetNode)

            jdbcResourceNode.add("Contains",jdbcTargetArray)

    jdbcResourcesArray.add(jdbcResourceNode)

# Return to MBean Tree Root
cd ('..');

jdbcResourcesNode.add("JDBC Multi Data Sources", jdbcResourcesArray)

model.add("JDBC Resource Information", jdbcResourcesNode)

print "Finished Scanning JDBC Info"

# CHANGE to the JMS Server MBean tree, loop through the JMS Servers printing a selection of MBean values

print "Scanning for JMS Info"

jmsResourceArray = Json.createArrayBuilder()

# Check if JMS Server MBean Directory exists

v_didyoufindit = findMBean('JMSServer');

if v_didyoufindit == 'true':
    cd ('JMSServer');
    myjmsservers = ls(returnMap='true');

    for myjmsserver in myjmsservers:
        jmsResourceNode = Json.createObjectBuilder()

        x_jms = java.lang.String(myjmsserver);
        cd(x_jms);
        v_jms_target = get('Target');

        jmsResourceNode.add("JMS Server Name", x_jms)

        # Some MBeans values are returned as an array or list.
        # Therefore to display the array contents in a more friendly way,
        # we loop through the array and print each content followed by a line break

        jmsTargetArray = Json.createArrayBuilder()

        for value in v_jms_target:
            jmsTargetNode = Json.createObjectBuilder()
            value = stripMBeanValue(value);
            jmsTargetNode.add("Target",value)
            jmsTargetArray.add(jmsTargetNode)

        jmsResourceNode.add("Targets",jmsTargetArray)

        v_PersistentStore = get('PersistentStore');
        v_PersistentStore = stripMBeanValue(v_PersistentStore);

        persistentStore=v_PersistentStore[0];

        if v_PersistentStore[0] != 'None':
            persistentStore += ",&nbsp"
            persistentStore += v_PersistentStore[2];

        jmsResourceNode.add("PersistentStore", persistentStore)

        cd ('../');

        jmsResourceArray.add("JMS Server", jmsResourceNode)

    v_didyoufindit = '';

else:
    print "No JMS Servers are configured within this domain.";
    v_didyoufindit = '';

# This piece of javascript enabled the Tabs to work

print "Finished scanning JMS info"
# CLOSE output file, program end

model.add("JMS Resource Information", jmsResourceArray)

"Writing JSON to file"
modelobj = model.build()

## now to print
stWriter = StringWriter();
jsonWriter = Json.createWriter(stWriter);
jsonWriter.writeObject(modelobj);
jsonWriter.close();

jsonData = stWriter.toString();

print >>f, jsonData

f.close()

closeDomain();

print "Finished Scan report - output file completed"

exit();
