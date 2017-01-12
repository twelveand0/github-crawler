#!/usr/bin/python
# -*- coding: UTF-8 -*-


from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import random
import time


RackeeperHOST=
RackeeperPORT=
ContainerVip = 
ContainerNormal = 
ImasDevUser = 
ImasDevPass = 


"""
    Upload a local file to CommonStorage
    Parameters:
        path, a file in current folder, type of string
    Return:
        status, True if success otherwise False
"""
def upload_to_commonstorage(path):
    try:
        

        return False

    except Exception,e:
        print e
        return False


'''
"""
    Upload a local file to CommonStorage
    Parameters:
        path, a file in current folder, type of string
    Return:
        status, True if success otherwise False
"""
def upload_to_commonstorage(path):
    try:
        url = "http://" +RackeeperHOST+ "/com-sm/upload-file/"

        random.seed()

        count = 3
        while count > 0:
            register_openers()
            datagen, headers = multipart_encode({"upload_file": open(path,"rb"),"storage_type":"ra","filename":path,"username":ImasDevUser,"password":ImasDevPass})
            request = urllib2.Request(url, datagen, headers)
            result = urllib2.urlopen(request).read()

            print result

            if r'success' in result:
                return True

            count = count - 1
            time.sleep(random.randint(1, 10))
        
        return False

    except Exception,e:
        print e
        return False 
'''

"""
    Download a file from CommonStorage to local drive
    Parameters:
        uri, filename in CommonStorage, type of string
        path, path in local drive, type of string
    Return:
        status, True if success otherwise False
"""
def download_from_commonstorage(uri,path):
    try:

        

        return True

    except Exception,e:
        print e
        return False


'''
"""
    Download a file from CommonStorage to local drive
    Parameters:
        uri, filename in CommonStorage, type of string
        path, path in local drive, type of string
    Return:
        status, True if success otherwise False
"""
def download_from_commonstorage(uri,path):
    try:

        url = "http://" + RackeeperHOST + "/com-sm/download-file/"

        register_openers()
        datagen, headers = multipart_encode({"storage_type":"ra","filename":uri,"username":ImasDevUser,"password":ImasDevPass})
        request = urllib2.Request(url, datagen, headers)
        soft_content = urllib2.urlopen(request).read()

        # download failed
        if(r'<xml>' in soft_content):
            print 'download file failed',soft_content
            return False

        f = open(path,"wb")
        f.write(soft_content)
        f.close()

        return True

    except Exception,e:
        print e
        return False
'''


"""
    Delete a file in CommonStorage
    Parameters:
        uri, filename in CommonStorage, type of string
    Return:
        status, True if success otherwise False
"""
def del_from_commonstorage(uri):
    try:

        
        return False

    except Exception as e:
        print e
        return False


"""
    Delete a file in CommonStorage
    Parameters:
        uri, filename in CommonStorage, type of string
    Return:
        status, True if success otherwise False
"""
def del_from_commonstorage(uri):
    try:

        url = "http://" +RackeeperHOST+ "/com-sm/delete-file/"

        register_openers()
        datagen, headers = multipart_encode({"storage_type":"ra","filename":uri,"username":ImasDevUser,"password":ImasDevPass})
        request = urllib2.Request(url, datagen, headers)
        result = urllib2.urlopen(request).read()

        if r'success' in result:
            return True

        # print result
        return False
    
    except Exception as e:
        print e
        return False


    
