#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github.NamedUser
import db_operation

class DB_NamedUser_Followship:
    """
        This class represents DB_NamedUser_Followship as a class describles followship between two UserWarning
            followee --IS FOLLOWING-- follower, which is similar with employee and employer
    """

    followee = None
    follower = None
    db = None
    table = "nameduser_followship"

    def __init__(self, followee, follower, db):
        self.followee = followee
        self.follower = follower
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

            cursor = self.db.cursor()

            sql = "insert into %s (followee_id, followee_login, follower_id, follower_login) values (%d, '%s', %d, '%s');"%(self.table, 
            self.followee.id, self.followee.login, self.follower.id, self.follower.login)

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

            sql = "select count(*) from %s where followee_id=%d && follower_id=%d;"%(self.table, self.followee.id, self.follower.id)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False

            return True

        except Exception as e:
            print e
            return False
