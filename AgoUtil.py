#-------------------------------------------------------------------------------
# Name:        maak een service van aangemaakte dataset
# Purpose:     maak een service van een automatisch aangemaakte dataset
#              versie voor VM_ware
# Author:      wubbels
#
# Created:     30-08-2012
# Copyright:   (c) wubbels 2012
# Version:     Python 2.7
#-------------------------------------------------------------------------------

#import arcpy
import os
import shutil
import urllib
import urllib2
import json

# generate a token to access ArcGIS online
    # returns token as string
def gentoken(server,username,password,expiration=60):
    query_dict = {'username': username,
                  'password': password,
                  'expiration': str(expiration),
                  'client': 'requestip'}
    query_string = urllib.urlencode(query_dict)
    url = "https://{}/sharing/generateToken".format(server)
    return json.loads(urllib2.urlopen(url + "?f=json&request=gettoken&" + query_string).read())['token']

# check if the access level of the user is according to the specified role
    # returns boolean true if this is the case, false if not.
    # possible roles: org_admin, org_publisher, org_user
def checkrole(server,username,token,role):
    url = "https://{}/sharing/rest/community/users/{}?f=pjson&token={}".format(server,username,token)
    check_role = json.loads(urllib2.urlopen(url).read())['role']
    if role == check_role:
        return True
    else:
        return False

# request all users from portal
    # returns a python dictionary with username as key and returnitem as value
    # possible returnitems: fullname, preferredView, description, email, access,
    #                       storageUsage, storageQuota, orgId,role, culture,
    #                       tags, region, thumbnail, created, modified, groups
def getusers(server,id_portal,token,returnitem):
    user_dict={}
    url = "https://{}/sharing/rest/portals/{}/users?token={}&num=100&f=pjson".format(server,id_portal,token)
    url_json = json.loads(urllib2.urlopen(url).read())['users']
    for i in range(len(url_json)):
        user_dict[url_json[i]["username"]]=url_json[i][returnitem]
    return user_dict

# request items of a certain type (default is all types) from a provided user
    # returns python list of item ids
    # possible item_types: Web Map, Feature Service, Map Service, WMS,
    #                      Service Definition, Web Mapping Application etc
    #                      (http://www.arcgis.com/apidocs/rest/itemtypes.html)
def requestitems(server,username,token,item_type=None):
    folders_lst = []
    items_lst = []
    #request content from user
    url = "https://{}/sharing/rest/content/users/{}?token={}&f=pjson".format(server,username,token)
    url_json = json.loads(urllib2.urlopen(url).read())
    #loop through items in root and add id to list if the type is as requested
    items_json_root_lst = url_json['items']
    for i in range(len(items_json_root_lst)):
        if item_type is None:
            items_lst.append(items_json_root_lst[i]['id'])
        elif items_json_root_lst[i]['type'] == item_type:
            items_lst.append(items_json_root_lst[i]['id'])
    #loop through folders in root and add id to list
    folders_json_lst = url_json['folders']
    for i in range(len(folders_json_lst)):
        #request content from  user in specific folder
        id_folder = folders_json_lst[i]['id']
        url2 = "https://{}/sharing/rest/content/users/{}/{}?token={}&f=pjson".format(server,username,id_folder,token)
        url2_json = json.loads(urllib2.urlopen(url2).read())
        #loop through items in folder and add id to list if the type is as requested
        items_json_folder_lst = url2_json['items']
        for k in range(len(items_json_folder_lst)):
            if item_type is None:
                items_lst.append(items_json_folder_lst[k]['id'])
            elif items_json_folder_lst[k]['type'] == item_type:
                items_lst.append(items_json_folder_lst[k]['id'])
    return items_lst

def deleteservice(server,service,username,id_group,token=None):
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
