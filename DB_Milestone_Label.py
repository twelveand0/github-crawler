#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import datetime
import db_operation

class DB_Milestone_Label:
    """
        This class represents DB_Milestone_Label as a class descrilbe one label of one github.Milestone.Milestone
    """

    label = None
    milestone = None
    db = None
    table = "Milestone_Label"

    def __init__(self, label, milestone, db):
        self.label = label
        self.milestone = milestone
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

            sql = "insert into %s (color, name, url, milestone) values ('%s', '%s', '%s', %d);" \
                    %(self.table, self.label.color, self.label.name, self.label.url.replace("'", "\\'").replace('"', '\\"'), self.milestone.id)
            
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

            sql = "select count(*) from %s where url='%s';"%(self.table, self.label.url)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False