import inspect
import mysql.connector
import os
import sys

from log import log
from pytz import timezone


class LocalTimeZone():
  timezone = timezone('Europe/Helsinki')


class DBConnector():
  user = 'root'
  password = 'Yh123$%^'
  host='10.55.76.34'
  port=31884

  def __init__(self):
    try:
      self.check_database()
      self._cnx = mysql.connector.connect(user=self.user, host=self.host, password=self.password, port=self.port, database=self._database)
      self._cursor = self._cnx.cursor()
      if not self._table in self.tables():
        self.create_table()
    except mysql.connector.Error as err:
      log.debug(f"lineno: {inspect.currentframe().f_lineno}, exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")

  def check_database(self):
    dbs = []

    cnx = mysql.connector.connect(user=self.user, host=self.host, password=self.password, port=self.port)
    cursor = cnx.cursor()
    cursor.execute("show databases")
    for (db) in cursor:
      dbs.append(db[0])
    if not self._database in dbs:
      cursor.execute(f"create database {self._database}")
    cursor.close()
    cnx.close()

  def tables(self):
    tables = []
    self._cursor.execute("show tables")
    for (table) in self._cursor:
      tables.append(db[0])
    return tables 

  def __enter__(self):
    return self._cursor

  def __exit__(self, exc_ty, exc_val, tb):
    self._cursor.close()
    self._cnx.close()
    

def main(argv=None):
  pass


if __name__ == "__main__":
  sys.exit(main())
