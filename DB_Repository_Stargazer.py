#!/usr/bin/python
# -*- coding: UTF-8 -*-


import github
import db_operation
import datetime

class DB_Repository_Stargazer:
    """
        This class represents DB_Repository_Stargazer as a class describles star-ship between \
        github.Repository.Repository and github.NamedUser.NamedUser
    """

    repo = None
    stargazer = None
    db = None
    table = "Repository_Stargazer"

    
    def __init__(self, repo, stargazer, db):
        self.repo = repo
        self.stargazer = stargazer
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

            sql = "insert into %s (%s, %s) values (%d, %d)"%(self.table, "repository", "stargazer", self.repo.id, self.stargazer.id)

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

            sql = "select count(*) from %s where repository=%d && stargazer=%d;"%(self.table, self.repo.id, self.stargazer.id)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False
