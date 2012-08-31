#-------------------------------------------------------------------------------
# Name:        maak een service van aangemaakte dataset
# Purpose:     maak een service van een automatisch aangemaakte dataset
#              versie voor VM_ware
# Author:      wubbels
#
# Created:     30-08-2012
# Copyright:   (c) wubbels 2012
#-------------------------------------------------------------------------------

import arcpy, os, shutil
import urllib,urllib2
import json
import ProjectStat_VM
#Genereren van een token
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
    url_gr = "https://{}/sharing/rest/content/groups/{}?token={}&f=pjson".format(server, id_group, token)
    print url_gr
    json_gr = json.loads(urllib2.urlopen(url_gr).read())["items"]
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

def main():
    ProjectStat_VM.main()

    # define local variables
    wrkspc = r"Z:\E\_temp\AGO\Gebiedsteams\Werk"
    mxd = "Projectgrenzen_eBS2.mxd"
    mapDoc = arcpy.mapping.MapDocument(wrkspc + "\\" + mxd)
    service = "Projectgrenzen_eBS"
    BasisDraft = wrkspc + "\\" + "BasisDraft.sddraft"
    sddraft = wrkspc + "\\" + "{}.sddraft".format(service)
    sd = wrkspc + "\\" + "{}.sd".format(service)
    id_group = "ce0bb763334548caa096abdfd135df36"
    username = "GCC_eli"
    password = "GCC_ago"

    # copy BasisDraft naar een nieuw bestand
    shutil.copyfile(BasisDraft, sddraft)

    # create service definition draft
    #analysis = arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service,'MY_HOSTED_SERVICES', None, True, None, 'Projectgrenzen eBS mockup', 'eBS, Grenzen, test')
    analysis = arcpy.mapping.AnalyzeForSD(sddraft)

    # stage and upload the service if the sddraft analysis did not contain errors
    if analysis['errors'] == {}:
        #delete existing sddraft
        if arcpy.Exists(sd):
            os.remove(sd)
        # create service definition
        arcpy.StageService_server(sddraft, sd)
        #probeer de service op AGO te deleten
        deleteservice("www.arcgis.com",service,username,password,id_group)
        # if required, sign in to My Hosted Services
        arcpy.SignInToPortal_server(username, password, 'http://www.arcgis.com/')
        # publish to My Hosted Services
        arcpy.UploadServiceDefinition_server(sd, 'My Hosted Services')
    else:
        # if the sddraft analysis contained errors, display them
        print analysis['errors']

    pass

#run main def
if __name__ == '__main__':
    main()