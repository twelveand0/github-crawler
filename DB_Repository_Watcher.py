#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github
import db_operation
import datetime


class DB_Repository_Watcher:
    """
        This class represents DB_Repository_Watcher as a class descrbles watch-ship between \
        github.Repository.Repository and github.NamedUser.NamedUser
    """

    repo = None
    watcher = None
    db = None
    table = "Repository_Watcher"


    def __init__(self, repo, watcher, db):
        self.repo = repo
        self.watcher = watcher
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

            sql = "insert into %s (%s, %s) values (%d, %d)"%(self.table, "repository", "watcher", self.repo.id, self.watcher.id)

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

            sql = "select count(*) from %s where repository=%d && watcher=%d;"%(self.table, self.repo.id, self.watcher.id)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False