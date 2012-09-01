#-------------------------------------------------------------------------------
# Name:        maak een service van aangemaakte dataset
# Purpose:     maak een service van een automatisch aangemaakte dataset
#              versie voor VM_ware
# Author:      wubbels
#
# Created:     30-08-2012
# Copyright:   (c) wubbels 2012
#-------------------------------------------------------------------------------

import arcpy
import os
import shutil
import urllib
import urllib2
import json

def gentoken(url,username,password,expiration=60):
    query_dict = {'username': username,
                  'password': password,
                  'expiration': str(expiration),
                  'client': 'requestip'}
    query_string = urllib.urlencode(query_dict)
    return json.loads(urllib2.urlopen(url + "?f=json&request=gettoken&" + query_string).read())['token']

def deleteservice(server,service,username,password,id_group,token=None):
    if token is None:
        print("token wordt opgehaald")
        token_url = "https://{}/sharing/generateToken".format(server)
        token = gentoken(token_url,username,password)
    print("token = " + token)
    #request data van de gehele kerngroep-group
    #https://www.arcgis.com/sharing/rest/content/users/GCC_eli
    url_gr = "https://{}/sharing/rest/content/users/{}?token={}&f=pjson".format(server, username, token)
    print url_gr
    json_gr = json.loads(urllib2.urlopen(url_gr).read())["items"]
    print str(len(json_gr))
    for i in range(len(json_gr)):
        if str(json_gr[i]["name"]) == service:
            id_item = json_gr[i]["id"]
            print id_item
            delete_service_url = "https://{}/sharing/rest/content/users/{}/items/{}/delete".format(server, username, id_item)
            params = urllib.urlencode({"token" : token, "f" : "pjson"})
            print delete_service_url
            print params
            result = json.loads(urllib2.urlopen(delete_service_url, params).read())["success"]
            if result:
                print("delete succesvol")
            else:
                print("bestaande service kan niet verwijderd worden")
                exit()

def publishMxdToAgo(mapDoc,serviceNaam,summary,tags,id_group,username,password):
    wrkspc = os.path.dirname(mapDoc)
    # define local variables
    sddraftBackup = wrkspc + "\\" + "{}.sddraft_backup".format(serviceNaam)
    sddraft = wrkspc + "\\" + "{}.sddraft".format(serviceNaam)
    sd = wrkspc + "\\" + "{}.sd".format(serviceNaam)

    # copy BasisDraft naar een nieuw bestand
    if arcpy.Exists(sddraftBackup):
            os.remove(sddraftBackup)
    if arcpy.Exists(sddraft):
       shutil.copyfile(sddraft, sddraftBackup)
    if arcpy.Exists(sddraft):
            os.remove(sddraft)

    # Create service definition draft
    arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, serviceNaam,'MY_HOSTED_SERVICES', None, True, None, summary, tags)

    # Analyze the service definition draft
    analysis = arcpy.mapping.AnalyzeForSD(sddraft)

    # stage and upload the service if the sddraft analysis did not contain errors
    if analysis['errors'] == {}:
        #delete existing sd
        if arcpy.Exists(sd):
            os.remove(sd)
        # create service definition
        arcpy.StageService_server(sddraft, sd)
        #probeer de service op AGO te deleten
        deleteservice("www.arcgis.com",serviceNaam,username,password,id_group)
        # if required, sign in to My Hosted Services
        arcpy.SignInToPortal_server(username, password, 'http://www.arcgis.com/')
        # publish to My Hosted Services
        arcpy.UploadServiceDefinition_server(sd, 'My Hosted Services')
    else:
        # Print errors, warnings, and messages returned from the analysis
        print "The following information was returned during analysis of the MXD:"
        for key in ('messages', 'warnings', 'errors'):
          print '----' + key.upper() + '---'
          vars = analysis[key]
          for ((message, code), layerlist) in vars.iteritems():
            print '    ', message, ' (CODE %i)' % code
            print '       applies to:',
            for layer in layerlist:
                print layer.name,
            print

    pass
