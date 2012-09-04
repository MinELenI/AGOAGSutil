#-------------------------------------------------------------------------------
# Name:        maak een service van aangemaakte dataset
# Purpose:     maak een service van een automatisch aangemaakte dataset
#              versie voor VM_ware
# Author:      wubbels
#
# Created:     30-08-2012
# Copyright:   (c) wubbels 2012
#-------------------------------------------------------------------------------


import AgoUtil

def main():
    # define local variables
    mapDoc = r"D:\Data\test.mxd"
    serviceNaam = "test"
    summary = 'testje'
    tags = "test, gcc"
    id_group = "**"
    username = "***"
    password = "**"
    AgoUtil.publishMxdToAgo(mapDoc,serviceNaam,summary,tags,id_group,username,password)

#run main def
if __name__ == '__main__':
    main()