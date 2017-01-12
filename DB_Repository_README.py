#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import datetime
import db_operation

class DB_Repository_README:
    """
        This class represents DB_Repository_README as a class describles README (github.ContentFile.ContentFile) \
        of one repository
    """

    readme = None
    repo = None
    db = None
    table = "Repository_README"

    
    def __init__(self, readme, repo, db):
        self.readme = readme
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

            D = [(a,v) for (a, v) in self.readme.__dict__.iteritems() if \
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

                if attr == "_content" or attr == "_decoded_content":
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

            
            sql_fields = sql_fields + "repository,"
            sql_values = sql_values + str(self.repo.id) + ","

             
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
                sql = "update %s set %s='%s' where sha='%s';"%(self.table, field, value, self.readme.sha)
            elif isinstance(value, int):
                sql = "update %s set %s=%d where sha='%s';"%(self.table, field, value, self.readme.sha)
            elif isinstance(value, datetime.datetime):
                sql = "update %s set %s='%s' where sha='%s';"%(self.table, field, value, self.readme.sha)

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

            sql = "select count(*) from %s where sha='%s';"%(self.table, self.readme.sha)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False
