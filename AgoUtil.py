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

import os
import shutil
import urllib
import urllib2
import json

def gentoken(server, username, password, expiration=60):
	# generate a token to access ArcGIS online
	# - returns token as string
	query_dict = {'username': username,
				  'password': password,
				  'expiration': str(expiration),
				  'client': 'requestip'}
	query_string = urllib.urlencode(query_dict)
	url = "https://{}/sharing/generateToken".format(server)
	return json.loads(urllib2.urlopen(url + "?f=json&request=gettoken&" + query_string).read())['token']

def checkrole(server, username, token, role):
	# check if the access level of the user is according to the specified role
	# -returns boolean true if this is the case, false if not.
	# -possible roles: org_admin, org_publisher, org_user
	url = "https://{}/sharing/rest/community/users/{}?f=pjson&token={}".format(server, username, token)
	check_role = json.loads(urllib2.urlopen(url).read())['role']
	if role == check_role:
		return True
	else:
		return False

def getusers(server, id_portal, token, returnitem):
	# request all users from portal
	# -returns a python dictionary with username as key and returnitem as value
	# -possible returnitems: fullname, preferredView, description, email, access,
	#						storageUsage, storageQuota, orgId,role, culture,
	#						tags, region, thumbnail, created, modified, groups
	user_dict = {}
	url = "https://{}/sharing/rest/portals/{}/users?token={}&num=100&f=pjson".format(server, id_portal, token)
	url_json = json.loads(urllib2.urlopen(url).read())['users']
	for i in range(len(url_json)):
		user_dict[url_json[i]["username"]] = url_json[i][returnitem]
	return user_dict

def requestitems(server, username, token, item_type=None):
	# request items of a certain type (default is all types) from a provided user
	# -returns python list of item ids
	# -possible item_types: Web Map, Feature Service, Map Service, WMS,
	#					   Service Definition, Web Mapping Application etc
	#					   (http://www.arcgis.com/apidocs/rest/itemtypes.html)
	folders_lst = []
	items_lst = []
	#request content from user
	url = "https://{}/sharing/rest/content/users/{}?token={}&f=pjson".format(server, username, token)
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
		url2 = "https://{}/sharing/rest/content/users/{}/{}?token={}&f=pjson".format(server, username, id_folder, token)
		url2_json = json.loads(urllib2.urlopen(url2).read())
		#loop through items in folder and add id to list if the type is as requested
		items_json_folder_lst = url2_json['items']
		for k in range(len(items_json_folder_lst)):
			if item_type is None:
				items_lst.append(items_json_folder_lst[k]['id'])
			elif items_json_folder_lst[k]['type'] == item_type:
				items_lst.append(items_json_folder_lst[k]['id'])
	return items_lst

def deleteservice(server, service, username, id_group, token):
	#request data from the entire group
	###THIS HAS BEEN CHANGED TO SEARCH THROUGH USER-CONTENT INSTEAD OF GROUP-CONTENT.
	###THIS MIGHT GO WRONG: TOKEN IS FROM ADMIN, SERVICE IS FROM SOMEONE ELSE. ADMIN CAN DELETE IT, BUT IT WON'T SHOW UP IN THIS SEARCH
	###SOLUTION: CHANGE BACK TO GROUP-SEARCH
	#####url_gr = "https://{}/sharing/rest/content/groups/{}?token={}&f=pjson".format(server, id_group, token)
	url_gr = "https://{}/sharing/rest/content/users/{}?token={}&f=pjson".format(server, username, token)
	print url_gr
	json_gr = json.loads(urllib2.urlopen(url_gr).read())["items"]
	print str(len(json_gr))
	for i in range(len(json_gr)):
		if str(json_gr[i]["name"]) == service:
			id_item = json_gr[i]["id"]
			print id_item
			###HERE YOU CAN USE THE USERNAME, BECAUSE IT DELETES ITEMS OWNED OR ADMINISTERED BY CALLING USER.
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

