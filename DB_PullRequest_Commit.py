#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import datetime
import db_operation


class DB_PullRequest_Commit:
    """
        This class represents DB_PullRequest_Commit as a class describles pull-commit relationship
    """

    commit = None
    pull = None
    db = None
    table = "PullRequest_Commit"

    def __init__(self, commit, pull, db):
        self.commit = commit
        self.pull = pull
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

            sql = "insert into %s (%s, %s) values ('%s', %d);" \
                    %(self.table, "commit", "pull", self.commit.sha, self.pull.id)
            
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

            sql = "select count(*) from %s where pull=%d && commit='%s';"%(self.table, self.pull.id, self.commit.sha)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False