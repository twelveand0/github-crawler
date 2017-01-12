#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import datetime
import db_operation

class DB_IssueComment:
    """
        This class represents DB_IssueComment as a database operating class for github.IssueComment.IssueComment
    """

    comment = None
    issue = None
    db = None
    table = "IssueComment"


    def __init__(self, comment, issue, db):
        self.comment = comment
        self.issue = issue
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

            D = [(a,v) for (a, v) in self.comment.__dict__.iteritems() if \
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

            sql_fields = sql_fields + "issue,"
            sql_values = sql_values + str(self.issue.id) + ","
             
            sql = sql_header + sql_fields[:-1] + ") " + sql_values[:-1] + ");"

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

            sql = "select count(*) from %s where id=%d;"%(self.table, self.comment.id)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False