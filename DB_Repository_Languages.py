#!/usr/bin/python
# -*- coding: UTF-8 -*-

import github.NamedUser
import datetime
import db_operation

class DB_Repository_Languages:
    """
        This class represent DB_Repository_Languages as a class describles languages of one repository
    """

    langs = None
    repo = None
    db = None
    table = "Repository_Language"

    def __init__(self, langs, repo, db):
        self.langs = langs
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
            
            for (lang, count) in self.langs.iteritems():

                if self.exist(lang):
                    continue

                sql = "insert into %s (%s, %s, %s) values ('%s', %d, %d);"%(self.table, "language", "count", "repository", lang, count, self.repo.id)

                cursor = self.db.cursor()

                cursor.execute(sql)

                self.db.commit()

            return True
        
        except Exception as e:
            print e
            return False


    def exist(self, lang):
        try:

            if self.open_if_connection_closed() == False:
                return False
            
            cursor = self.db.cursor()

            sql = "select count(*) from %s where repository=%d && language='%s';"%(self.table, self.repo.id, lang)

            cursor.execute(sql)

            result = cursor.fetchall()

            if result[0][0] == 0:
                return False
            
            return True

        except Exception as e:
            print e
            return False
