#!/usr/bin/env python
### Script provided by DataStax.

import shlex, subprocess, time, urllib2, os, re
import conf

nodetoolStatement = "nodetool -h localhost ring"

try:
    with open('/home/ubuntu/datastax_ami/presetup/VERSION', 'r') as f:
        version = f.readline().strip()
except:
    version = "<< $HOME/datastax_ami/presetup/VERSION missing >>"

req = urllib2.Request('http://instance-data/latest/meta-data/ami-launch-index')
launchIndex = urllib2.urlopen(req).read()
req = urllib2.Request('http://instance-data/latest/meta-data/public-hostname')
hostname = urllib2.urlopen(req).read()

try:
    req = urllib2.Request('http://instance-data/latest/user-data/')
    global userdata
    userdata = urllib2.urlopen(req).read()

    # Remove passwords from printing
    p = re.search('(-o\s*\w*:)(\w*)', userdata)
    if p:
        userdata = userdata.replace(p.group(2), '****')

    p = re.search('(-p\s*\w*:)(\w*)', userdata)
    if p:
        userdata = userdata.replace(p.group(2), '****')

    p = re.search('(-e\s*.*:.*:.*:)(\S*)', userdata)
    if p:
        userdata = userdata.replace(p.group(2), '****')

    print
    print "Cluster started with these options:"
    print userdata
    print
except:
    print "No cluster configurations set."


waitingforstatus = False
while True:
    status = conf.getConfig("AMI", "CurrentStatus")
    if not status == 'Complete!' and not status == False:
        print status
    elif status == 'Complete!':
        break
    else:
        if not waitingforstatus:
            print "Waiting for cluster to boot..."
            waitingforstatus = True
    time.sleep(5)

print """Waiting for nodetool...
The cluster is now in it's finalization phase. This should only take a moment...

Note: You can also use CTRL+C to view the logs if desired:
    AMI log: ~/datastax_ami/ami.log
    Cassandra log: /var/log/cassandra/system.log
"""

retcode = 0
while True:
    retcode = subprocess.call(shlex.split(nodetoolStatement), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if (int(retcode) != 3):
        break

stoppedErrorMsg = False
while True:
    nodetoolOut = subprocess.Popen(shlex.split(nodetoolStatement), stderr=subprocess.PIPE, stdout=subprocess.PIPE).stdout.read()
    if (nodetoolOut.lower().find("error") == -1 and nodetoolOut.lower().find("up") and len(nodetoolOut) > 0):
        if not stoppedErrorMsg:
            if waitingforstatus:
                time.sleep(15)
            stoppedErrorMsg = True
        else:
            break

startTime = time.time()
while True:
    if nodetoolOut.count("Up") == int(conf.getConfig("Cassandra", "ClusterSize")):
        break
    if time.time() - startTime > 15:
        break

nodetoolOut = subprocess.Popen(shlex.split(nodetoolStatement), stderr=subprocess.PIPE, stdout=subprocess.PIPE).stdout.read()
print nodetoolOut

opscenterIP = None
opscenterInstalled = None
try:
    opscenterIP = conf.getConfig("OpsCenter", "DNS")
    packageQuery = subprocess.Popen(shlex.split("dpkg-query -l 'opscenter'"), stderr=subprocess.PIPE, stdout=subprocess.PIPE).stdout.read()
    if packageQuery:
        opscenterInstalled = True
except:
    pass

print """
Nodetool: nodetool -h localhost ring
Cli: cassandra-cli -h localhost"""

if conf.getConfig("AMI", "Type") == "Brisk":
    print "Hive: brisk hive"
    print
    print "Sample Hive Demo:"
    print "    http://www.datastax.com/docs/0.8/brisk/brisk_demo"

if opscenterIP and opscenterInstalled:
    print "Opscenter: http://" + opscenterIP + ":8888/"
    print "    Please wait 60 seconds if this is the cluster's first start..."

substring = "Version: "
if conf.getConfig("AMI", "Type") == "Cassandra":
    versionInfo = subprocess.Popen(shlex.split("dpkg -s cassandra"), stdout=subprocess.PIPE).stdout.read()
    versionInfo = versionInfo[versionInfo.find(substring) + len(substring) : versionInfo.find("\n", versionInfo.find(substring))].strip()
    versionInfo = "Cassandra version " + versionInfo
if conf.getConfig("AMI", "Type") == "Brisk":
    versionInfo = subprocess.Popen(shlex.split("dpkg -s brisk"), stdout=subprocess.PIPE).stdout.read()
    versionInfo = versionInfo[versionInfo.find(substring) + len(substring) : versionInfo.find("\n", versionInfo.find(substring))].strip()
    versionInfo = "Brisk version " + versionInfo

print """

For first time users, refer to ~/datastax_ami/SWITCHES.txt.


Support Links:
    Cassandra:
        http://www.datastax.com/docs

    Brisk:
        http://www.datastax.com/docs/brisk

    AMI:
        http://www.datastax.com/ami

    Cassandra client libraries:
        http://www.datastax.com/docs/clients

    For quick support, visit:
        IRC: #datastax-brisk channel on irc.freenode.net

---------------------------------
DataStax AMI for Apache Cassandra
and DataStax' Brisk(TM)
AMI version """ + str(version) + """
""" + versionInfo + """

---------------------------------

"""

notices = ''
knownErrors = []
knownErrors.append("yes: write error\n")
knownErrors.append("java.io.ioexception: timedoutexception()\n")
knownErrors.append("caused by: timedoutexception()\n")
for line in open('/home/ubuntu/datastax_ami/ami.log'):
    if ('error' in line.lower() or '[warn]' in line.lower() or 'exception' in line.lower()) and not line.lower() in knownErrors:
        notices += line

if len(notices) > 0:
    print "These notices occurred during the startup of this instance:"
    print notices


