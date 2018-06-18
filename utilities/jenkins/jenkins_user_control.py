#!/usr/bin/env python3.6

#-----------------------------------------------------------------
# Licensed Materials - Property of IBM
#
# WebSphere Commerce
#
# (C) Copyright IBM Corp. 2017 All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
#-----------------------------------------------------------------

import jenkins
import os
import sys
import json
import argparse
import tempfile
from jinja2 import Environment, FileSystemLoader

#input tenant_id to complete creation

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument("tenant_id", help="The tenant_id is used to create a unique group and two Jobs")
cmd_parser.add_argument("username", help="The user used to login")
cmd_parser.add_argument("password", help="The password of user")
cmd_parser.add_argument("jenkins_server",help="The current jenkins server ip")

args = cmd_parser.parse_args()

#connecting jenkins server

server = jenkins.Jenkins(args.jenkins_server, username=args.username, password=args.password)
print("Jenkis server " + server.server + " is connected")


#Copy Jobs "PrepareEnv" and "CreateWCSCloud"
copyEnvName = "PrepareEnv_" + args.tenant_id
copyCloudName = "DeployWCSCloud_" + args.tenant_id
copyBuildDockerName = "BuildDockerImage_" + args.tenant_id
copyTriggerIndexName = "TriggerBuildIndex_" + args.tenant_id
copyCustomTemp = "PopCustomTemp_" + args.tenant_id
copyIndexRep = "TriggerIndexReplica_" + args.tenant_id
copyBundleCert = "BundleCert_" + args.tenant_id
copyAddCert = "AddCert_" + args.tenant_id

server.copy_job('PrepareEnv_Base', copyEnvName)
server.copy_job('DeployWCSCloud_Base', copyCloudName)
server.copy_job('BuildDockerImage_Base', copyBuildDockerName)
server.copy_job('TriggerBuildIndex_Base', copyTriggerIndexName)
server.copy_job('PopCustomTemp_Base', copyCustomTemp)
server.copy_job('TriggerIndexReplica_Base', copyIndexRep)
server.copy_job('AddCert_Base', copyAddCert)
server.copy_job('BundleCert_Base', copyBundleCert)

#Create a unique group for the tenant_id.
templateVars = {
    "EnvName" : copyEnvName,
    "CloudName" : copyCloudName,
    "BuildDockerName": copyBuildDockerName,
    "TriggerIndexName": copyTriggerIndexName,
    "CustomTemp": copyCustomTemp,
    "IndexRep": copyIndexRep,
    "AddCert" : copyAddCert,
    "BundleCert": copyBundleCert,
    "name" : args.tenant_id
}
print(templateVars)
templatePaht = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape = False,
    loader = FileSystemLoader(os.path.join(templatePaht,)),
    trim_blocks = False
)
appXmlStr = TEMPLATE_ENVIRONMENT.get_template("viewTemplate.xml").render(templateVars)
print(appXmlStr)

server.create_view(args.tenant_id, appXmlStr)
server.reconfig_view(args.tenant_id, appXmlStr)
