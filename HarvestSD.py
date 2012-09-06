#-------------------------------------------------------------------------------
# Name:        HarvestSD
# Purpose:     Harvest SD files from ArcGIS Online
# Author:      Tjibbe Wubbels
#
# Created:     05-09-2012
# Copyright:   (c) wubbels 2012
# Version:     Python 2.7
#-------------------------------------------------------------------------------

import AgoUtil
import urllib2
import webbrowser
import getpass

def def_prompt(msg):
    prompt = msg
    while True:
        ans = raw_input(prompt)
        if not ans:
            print "Enter " + msg
            continue
        else:
            return ans

def main():

    # define local variables
    server = "www.arcgis.com"
    username = def_prompt("Username: ")
    password = getpass.getpass("Password: ")
    id_portal = "kE0BiyvJHb5SwQv7"

    # request token from AGO
    token = AgoUtil.gentoken(server,username,password)

    # check if user is administrator
    role = "org_admin"
    if AgoUtil.checkrole(server,username,token,role):
        print "user has admin privileges"
        pass
    else:
        print "log in as user with admin privileges"
        exit()

    # request all users from portal
    returnitem = "email"
    myUsers_dict = AgoUtil.getusers(server,id_portal,token,returnitem)
    print "requested all users "

    # request all items per user
    item_type = "Service Definition"
    for user in myUsers_dict.keys():
        print user + " wordt verwerkt.."
        myItems_lst = AgoUtil.requestitems(server,user,token,item_type)
        for item in myItems_lst:
            url = "https://{}/sharing/content/items/{}/data?token={}".format(server,item,token)
            webbrowser.open(url)

    print "Ready"

#run main def
if __name__ == '__main__':
    main()