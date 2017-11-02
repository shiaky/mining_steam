#!/usr/bin/env python3

import sqlite3 as l3
import os
import io


#-------------- db class for db connection ----------------

class Dbcon:
    def __init__(self,
                 sPathToDB=""
                 ):

        self.sPathToDB = self.set_PathToDB(sPathToDB)

        self.con = None
        self.cur = None

        self.connect_to_db()


# ------------ util ------------------------

    def __escape_home_in_path(self, sPath):
        return os.path.expanduser(sPath)

    def __check_whether_file_exists(self, sPathToFile):
        return os.path.isfile(self.__escape_home_in_path(sPathToFile))

# ------------ public methods --------------

    def set_PathToDB(self, sPathToDB):
        if not self.__check_whether_file_exists(sPathToDB):
            raise Exception("The DB file %s does not exist" % sPathToDB)
        self.sPathToDB = self.__escape_home_in_path(sPathToDB)
        return self.sPathToDB

    def connect_to_db(self):
        try:
            self.con = l3.connect(
                self.sPathToDB, detect_types=l3.PARSE_DECLTYPES)
            self.cur = self.con.cursor()
            self.cur.execute("PRAGMA foreign_keys = ON;")

        except l3.Error as e:
            print("Error while connecting to db: ", e.args[0])
            self.close_db_connection()

    def close_db_connection(self):
        if self.con:
            self.con.close()

    def rollback_sql_query(self):
        if self.con:
            self.con.rollback()

    def execute_sql_query_manipulation(self, sQuery, tpValues=None):
        """ returns the id of the inserted dataset if id is autoincremented
            except of giving:
            sQuery = "INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)"
            you can also give
            sQuery = "INSERT INTO stocks VALUES (?,?,?,?,?)"
            tpValues = ('2017-01-05','BUY','RHAT',100,35.14)
         """
        if not self.con:
            raise Exception(
                "You have to establish a connection to a database before you can execute sql queries.")
        if not l3.complete_statement(sQuery):
            raise Exception(
                "The sql query %s is no valide sql statement" % sQuery)
        try:
            if not tpValues:
                self.cur.execute(sQuery)
            else:
                self.cur.execute(sQuery, tpValues)
            self.con.commit()
            return self.cur.lastrowid
        except l3.Error as e:
            print("An error occurred: ", e.args[0])
            self.rollback_sql_query()

    def execute_sql_query_select(self, sQuery, tpValues=None):
        """except of giving:
            sQuery = "SELECT * FROM A WHERE id=5"
            you can also give
            sQuery = "SELECT * FROM A WHERE id=?"
            tpValues = (5,)
            """
        if not self.con:
            raise Exception(
                "You have to establish a connection to a database before you can execute sql queries.")
        if not l3.complete_statement(sQuery):
            raise Exception(
                "The sql query %s is no valide sql statement" % sQuery)
        try:
            if not tpValues:
                self.cur.execute(sQuery)
            else:
                self.cur.execute(sQuery, tpValues)
            return self.cur.fetchall()
        except l3.Error as e:
            print("An error occurred: ", e.args[0])
