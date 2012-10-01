#-------------------------------------------------------------------------------
# Name:		maak een service van aangemaakte dataset
# Purpose:	 maak een service van een automatisch aangemaakte dataset
#			  versie voor VM_ware
# Author:	  wubbels
#
# Created:	 30-08-2012
# Copyright:   (c) wubbels 2012
# Version:	 Python 2.7
#-------------------------------------------------------------------------------

import arcpy
import AgoUtil
import os
import shutil
import urllib
import urllib2
import json

def publishSdToAgoArpPy(serviceNaam, id_group, username, password, server, token=None):
	if token is None:
		token = AgoUtil.gentoken(server, username, password, expiration=60)
	#probeer de service op AGO te deleten
	AgoUtil.deleteservice(server, serviceNaam, username, id_group, token)
	# if required, sign in to My Hosted Services
	arcpy.SignInToPortal_server(username, password, server)
	# publish to My Hosted Services
	arcpy.UploadServiceDefinition_server(sd, 'My Hosted Services')

	pass

def createSdFromMxd(mapDoc, serviceNaam, summary, tags):
	wrkspc = os.path.dirname(mapDoc)
	# define local variables
	sddraftBackup = os.path.join(wrkspc, "{}.sddraft_backup".format(serviceNaam))
	sddraft = os.path.join(wrkspc, "{}.sddraft".format(serviceNaam))
	sd = os.path.join(wrkspc, "{}.sd".format(serviceNaam))

	# copy BasisDraft naar een nieuw bestand
	if arcpy.Exists(sddraftBackup):
			os.remove(sddraftBackup)
	if arcpy.Exists(sddraft):
		shutil.copyfile(sddraft, sddraftBackup)
	if arcpy.Exists(sddraft):
		os.remove(sddraft)

	# Create service definition draft
	arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, serviceNaam, 'MY_HOSTED_SERVICES', None, True, None, summary, tags)

	# Analyze the service definition draft
	analysis = arcpy.mapping.AnalyzeForSD(sddraft)

	# stage and upload the service if the sddraft analysis did not contain errors
	if analysis['errors'] == {}:
		#delete existing sd
		if arcpy.Exists(sd):
			os.remove(sd)
		# create service definition
		arcpy.StageService_server(sddraft, sd)
	else:
		# Print errors, warnings, and messages returned from the analysis
		print "The following information was returned during analysis of the MXD:"
		for key in ('messages', 'warnings', 'errors'):
		  print '----' + key.upper() + '---'
		  vars = analysis[key]
		  for ((message, code), layerlist) in vars.iteritems():
			print '	', message, ' (CODE %i)' % code
			print '	   applies to:',
			for layer in layerlist:
				print layer.name,
			print
			sd = None
	return sd		
