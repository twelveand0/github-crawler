#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import db_operation
import datetime

NONEINT = -1

class DB_Repository:
    """
        This class represents DB_Repository as a database operating class for github.Repository.Repository
    """

    repo = None
    db = None
    table = "Repository"

    def __init__(self, repo, db):
        self.repo = repo
        self.db = db


    def open_if_connection_closed(self):
        try:

            if self.db is None:
                return False

            if self.db.open == 0:
                self.db = db_operation.connect_to_db_simple()
            
                if self.db is None:
                    return False
        
            return True

        except Exception, e:
            print e
            return False


    def save(self):
        try:

            if self.open_if_connection_closed() == False:
                return False

            if self.exist():
                return True

            D = [(a,v) for (a, v) in self.repo.__dict__.iteritems() if \
                    (a,) not in github.GithubObject.CompletableGithubObject.__dict__.iteritems() \
                    and (a,) not in github.GithubObject.GithubObject.__dict__.iteritems()]


            '''
                construct sql statement
            '''
            sql_header = "insert into %s "%(self.table)
            sql_fields = "("
            sql_values = "values ("

            for (attr, value) in D:
                
                if attr == "_CompletableGithubObject__completed" or attr == "_headers" or \
                    attr == "_rawData" or attr == "_requester":
                    continue
                
                if isinstance(value, github.GithubObject._NotSetType):
                    continue

                v = value.value
                if isinstance(v, bool):
                    sql_fields = sql_fields + attr[1:] + ","
                    if v:
                        sql_values = sql_values + str(1) + ","
                    else:
                        sql_values = sql_values +  str(0) + ","

                elif isinstance(v, int):
                    sql_fields = sql_fields + attr[1:] + ","
                    sql_values = sql_values + str(v) + ","

                elif isinstance(v, basestring):
                    sql_fields = sql_fields + attr[1:] + ","
                    # escape
                    v = v.replace("'", "\\'").replace('"', '\\"')
                    sql_values = sql_values + "'" + v + "',"

                elif isinstance(v, datetime.datetime):
                    sql_fields = sql_fields + attr[1:] + ","
                    sql_values = sql_values + "'" + str(v) + "',"

                elif isinstance(v, github.NamedUser.NamedUser):
                    sql_fields = sql_fields + attr[1:] + ","
                    sql_values = sql_values + str(v.id) + ","

                elif isinstance(v, github.Organization.Organization):
                    sql_fields = sql_fields + attr[1:] + ","
                    sql_values = sql_values + str(v.id) + ","
                
                elif isinstance(v, github.Repository.Repository):
                    sql_fields = sql_fields + attr[1:] + ","
                    sql_values = sql_values + str(v.id) + ","
 
            sql = sql_header + sql_fields[:-1] + ") " + sql_values[:-1] + ");"

            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()            

            return True

        except Exception as e:
            print e
            return False
    

    def update_one(self, field, value):
        try:

            if self.open_if_connection_closed() == False:
                return False


            sql = None
            if isinstance(value, basestring):
                sql = "update %s set %s='%s' where id=%d;"%(self.table, field, value, self.repo.id)
            elif isinstance(value, int):
                sql = "update %s set %s=%d where id=%d;"%(self.table, field, value, self.repo.id)
            elif isinstance(value, datetime.datetime):
                sql = "update %s set %s='%s' where id=%d;"%(self.table, field, value, self.repo.id)

            if sql is None:
                return False
            
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()

            return True

        except Exception as e:
            print e
            return False


    def exist(self):
        try:

            if self.open_if_connection_closed() == False:
                return False
            
            cursor = self.db.cursor()

            sql = "select count(*) from %s where id=%d;"%(self.table, self.repo.id)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False

