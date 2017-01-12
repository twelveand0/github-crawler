#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import time
import random

"""
    Configure settings
"""
DB_IP=
DB_NAME=
DB_VM_NAME=
DB_USER=
DB_PASS =

"""
    connect to database
    Parameters:
        db_ip, ip address of database
        db_user, username of database
        db_pass, password of database
        db_name, name of database
    Return:
        a handle of the connected database if success
        or None
"""
def connect_to_db(db_ip,db_user,db_pass,db_name):
    try:

        db = MySQLdb.connect(db_ip,db_user,db_pass,db_name)
        db.set_character_set('utf8')

        if(db == None):
            return None
    
        return db
    except Exception as e:
        print e
        return None


"""
    Connect to database with default setting
    Parameters:
    Return:
        a handle of the connected database if success
        or None
"""
def connect_to_db_simple():
    db = None
    count = 5
    while True:
        count = count - 1
        db = connect_to_db(DB_IP,DB_USER,DB_PASS,DB_NAME)
        if db is not None or count < 0:
            break

        random.seed()
        time.sleep(random.randint(1, 5))
    return db


#=============================================================#
#select one field value from  table
#@para db, database pointer
#@para table_name, table name
#@para field_name, the name of indexed field,
#       value is static_dot_uri or static_path_image_uri
#@para r_id, index a record
#@return value of indexed field
#=============================================================#
def select_field_from_table(db,table_name,field_name,r_id):    
    cursor = db.cursor()
    
    sql="select %s from %s where id = %s;"%(field_name,table_name,r_id)
    
    try:
       cursor.execute(sql)
       result=cursor.fetchall()
       result=str(result[0])
       result=result.split('(')[1].split(',')[0]

    except Exception,e:
        print "error to task table:",e
        return ''

    return result

def select_field_by_vmip(db,table_name,field_name,ip):
    cursor=db.cursor()
    sql="select %s from %s where vm_ip = '%s';"%(field_name,table_name,ip)

    print sql
    try:
       cursor.execute(sql)
       result=cursor.fetchall()
       if(len(result)>0):
           result=str(result[0])
           result=result.split('(')[1].split(',')[0]
       else:
            result=''
    except Exception,e:
        print "error to task table:",e
        return ''

    return result

#=========================================================#
#insert a record with field=value
#@para db, db handle
#@para field, field name
#@para value, field value
#=========================================================#
def insert_into_db(db,table_name,field,value):
    cursor = db.cursor()
    sql="insert into %s (%s) values ('%s');"%(table_name,field,value)
    #print sql

    try:
        cursor.execute(sql)
    except Exception,e:
        print 'some exception has happened when insert into db',e
        return


#========================================================#
#update a record with field=value
#@para db, db handle
#@para table_name, table name
#@para field, field name
#@para value, field value
#@para r_id, index of record
#========================================================#
def update_one_record(db,table_name,field,value,r_id):
    cursor=db.cursor()
    sql="update %s set %s = '%s' where id = %s;"%(table_name,field,value,r_id)

    #print sql
    try:
        cursor.execute(sql)
    except Exception,e:
        print 'some exception has happened when update db',e
        return

#==========================================================#
#update table 'vm' by ip address
#==========================================================#
def update_one_vm(db,table_name,field,value,ip):
    cursor=db.cursor()
    sql="update %s set %s = '%s' where vm_ip = '%s';"%(table_name,field,value,ip)
    #print sql
    try:
        cursor.execute(sql)
    except Exception,e:
        print 'some exception has happened when update db',e
        return

    
#===========================================================#
#update a record in task table with new values of dot&svg uris
#@para db, handle of db
#@para r_id, index of a record
#@para dot_uri, uri of static call graph dot file
#@para svg_uri, uri of static call svg file
#===========================================================#
def update_one_record_simple(db,r_id,dot_uri,svg_uri):
    cursor=db.cursor()
    sql="update %s set %s = '%s', %s = '%s' where id = %s;"%(TABLE_TASK_NAME,FN_S_DOT_URI,dot_uri,FN_S_SVG_URI,svg_uri,r_id)

    #print sql
    try:
        cursor.execute(sql)
    except Exception,e:
        print 'some exception has happened when update db',e
        return



#============================================================#
#db=connect_to_db(DB_IP,DB_USER,DB_PASS,DB_NAME)
#
#if(db == None):
#    print 'connect to db error'
#else:
#    result=select_field_from_table(db,TABLE_TASK_NAME,"static_dot_uri",338)
#    #print select_field_from_table(db,TABLE_TASK_NAME,"")
#    print result
#    db.close()
#
#==================================================================#
#db=connect_to_db(DB_IP,DB_USER,DB_PASS,DB_NAME)
#if (db == None):
#    print 'failed to connect to db'
#else:
#    #insert_into_db(db,'dynamic_dot_uri','20bd793e141d9b5967f1061f483b27eb')
#    #update_one_record(db,'dynamic_dot_uri','44ffbad6fe4adbb347a67fa87ffafab9',1)
#    update_one_record_simple(db,338,'30f714a740a51560f0fda4513eedfa23','601197cff878760874ea019cea30e4a1')
#    db.close()
#==================================================================#

 




