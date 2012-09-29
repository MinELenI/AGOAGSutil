#-------------------------------------------------------------------------------
# Name:        HarvestSD
# Purpose:     Harvest SD files from ArcGIS Online
# Author:      Tjibbe Wubbels
#
# Created:     05-09-2012
# Copyright:   (c) wubbels 2012
# Version:     Python 2.7
#-------------------------------------------------------------------------------
import os
import AgoUtil
import urllib2
import webbrowser
import getpass
import urlparse
import shutil

# From: http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way
def download(url, folder=None,fileName=None):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                filename = filename.replace('"', '').replace("'", "")
                if filename == '':
                    filename = "dummy.sd"
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        if folder:
            fileName = os.path.join(folder, fileName)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()

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
    downloadFolder = def_prompt("Download folder: ")
    downloadFolder = r"/Users/maartentromp/Documents/Temp"
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
            download(url, downloadFolder)

    print "Ready"

#run main def
if __name__ == '__main__':
    main()