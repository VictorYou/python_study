import argparse
import csv
import inspect
import logging
import mysql.connector
import os
import paramiko
import re
import sys
import xml.etree.ElementTree as ET

sys.path.append("../common")

from datetime import datetime, timedelta
from dbconnector import DBConnector, LocalTimeZone
#from exceptions import MissingStatus, CommitDateTooOld
from functools import wraps
from log import log
from pytz import timezone


class DBConnectorJiraTicket(DBConnector):
  database = 'jira_ticket'


class DBConnectorJiraTicketJira(DBConnectorJiraTicket):
  table = 'jira_ticket'

  def create_table(self):
    command = f"create table {self.table} (id varchar(50) primary key, summary varchar(80), assignee varchar(20), reporter varchar(20), location varchar(20), creation_date int(10))"
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: command: {command}")
    self._cursor.execute(f"{command}")

class DBConnectorJiraTicketCount(DBConnectorJiraTicket):
  table = 'jira_count'

  def create_table(self):
    command = f"create table {self.table} (id varchar(50) primary key, location varchar(20), creation_date int(10), count int(10))"
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: command: {command}")
    self._cursor.execute(f"{command}")


class JiraTicket():
  config_file = "reporters_chengdu.txt"
  result_file = "result.csv"
  summary_len = 25

  def __init__(self):
    self._reporters_chengdu, self._tickets, self._created, self._counts = [], [], [], []
    with open(self.config_file) as file:
      for line in file:
        self._reporters_chengdu += line.strip().split(',')
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: reporters_chengdu: {self._reporters_chengdu}")

  def get(self, data_after):
    self.get_tickets()
    self.get_counts()
    return self

  def get_tickets(self):
    result = []
    with open(self.result_file) as f:
      f_csv = csv.DictReader(f)
      result += []
      for r in f_csv:
        ticket = {}
        for key in ['Issue key', 'Summary', 'Assignee', 'Reporter']:
          ticket[key] = r[key]
        ticket['Summary'] = re.sub('[\'\"]', '', ticket['Summary'])
        ticket['Summary'] = ticket['Summary'][:self.summary_len]
        month_year = re.match('\d+\.(\d+\.\d+)\s+.*', r['Created']).group(1)
        ticket['Created'] = LocalTimeZone.timezone.localize(datetime.strptime(month_year, "%m.%Y")).timestamp()
        self._created.append(ticket['Created'])
        if r['Reporter'] in self._reporters_chengdu:
          ticket['From'] = 'Chengdu'
        else:
          ticket['From'] = 'Others'
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: ticket: {ticket}")
        self._tickets.append(ticket)
    self._tickets = sorted(self._tickets, key=lambda k: k['Issue key'])
    self._created = list(set(self._created))
    self._created = sorted(self._created)

  def get_counts(self):
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: self._created: {self._created}")
    for created in self._created:
      for location in ['Chengdu', 'Others']:
        list = [d for d in self._tickets if d['Created'] == created and d['From'] == location]
        if len(list) > 0:
          self._counts.append({'location': location, 'creation_date': created, 'count': len(list)})
    self._counts = sorted(self._counts, key=lambda k: k['creation_date'])
        
  def save(self):
    self.save_jira()
    self.save_count()
    return self

  def save_jira(self):
    with DBConnectorJiraTicketJira() as d:
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: type(d): {type(d)}")
      for data in self._tickets:
        command = f"insert into {DBConnectorJiraTicketJira.table}(id, summary, assignee, reporter, location, creation_date) values('{data['Issue key']}', '{data['Summary']}', '{data['Assignee']}', '{data['Reporter']}', '{data['From']}', '{data['Created']}') on duplicate key update summary='{data['Summary']}', assignee='{data['Assignee']}', reporter='{data['Reporter']}', location='{data['From']}', creation_date={data['Created']}"
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: command: {command}")
        d.execute(command)
        d._cnx.commit()
    return self

  def save_count(self):
    with DBConnectorJiraTicketCount() as d:
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: type(d): {type(d)}")
      for data in self._counts:
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: data: {data}")
        command = f"insert into {DBConnectorJiraTicketCount.table}(id, location, creation_date, count) values('{data['location']}_{data['creation_date']}', '{data['location']}', {data['creation_date']}, {data['count']}) on duplicate key update location='{data['location']}', creation_date={data['creation_date']}, count={data['count']}"
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: command: {command}")
        d.execute(command)
        d._cnx.commit()
    return self

  def cleanup(self):
    pass
        

def main(argv=None):
  logging.getLogger("paramiko").setLevel(logging.WARNING)
  week_ago = LocalTimeZone.timezone.localize(datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%dT%H:%M:%S')

  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--date-after", dest="date_after", default=f'{week_ago}', help="date after, eg: 2020-04-18T00:33:58")
  args = parser.parse_args()
  log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: args: {args}")

  JiraTicket().get(args.date_after).save().cleanup()


if __name__ == "__main__":
  sys.exit(main())
