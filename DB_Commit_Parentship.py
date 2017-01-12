#!/usr/bin/python
# -*- coding: UTF-8 -*-


import github
import db_operation
import datetime

class DB_Commit_Parentship:
    """
        This class represents DB_Commit_Parentship as a class describles the parentship between 2 \
        github.Commit.Commit
    """

    parent = None
    child = None
    db = None
    table = "Commit_Parentship"

    def __init__(self, parent, child, db):
        self.parent = parent
        self.child = child
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

            sql = "insert into %s (%s, %s) values ('%s', '%s')"%(self.table, "parent", "child", self.parent.sha, self.child.sha)

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

            sql = "select count(*) from %s where parent='%s' && child='%s';"%(self.table, self.parent.sha, self.child.sha)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False