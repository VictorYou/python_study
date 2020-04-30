import argparse
import inspect
import logging
import mysql.connector
import os
import paramiko
import re
import sys
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from functools import wraps
from log import log
from pytz import timezone


class MissingStatus(Exception):
  pass


class CommitDateTooOld(Exception):
  pass


class LocalTimeZone():
  timezone = timezone('Europe/Helsinki')

class DBConnector():
  user = 'root'
  password = 'Yh123$%^'
  host='10.55.76.34'
  port=31884
  database='promotion_history'

  def __init__(self):
    try:
      self._cnx = mysql.connector.connect(user=self.user, host=self.host, password=self.password, port=self.port, database=self.database)
      self._cursor = self._cnx.cursor()
    except mysql.connector.Error as err:
      log.debug(f"lineno: {inspect.currentframe().f_lineno}, exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")

  def __enter__(self):
    return self._cursor

  def __exit__(self, exc_ty, exc_val, tb):
    self._cursor.close()
    self._cnx.close()
    

class FileDownloader():
  backend = '10.9.137.108'
  backend_username = 'n8'
  backend_password = '8n'
  package_home = '/opt/mpp/packages/'

  def download_file(self, prefix, file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(self.backend, username=self.backend_username, password=self.backend_password, look_for_keys=False, timeout=60)
    sftp_client = ssh.open_sftp()
    file_path = os.path.join(self.package_home, prefix, file)
    log.debug(f'lineno: {inspect.currentframe().f_lineno}, file_path: {file_path}')
    try:
      sftp_client.get(file_path, file)
    except IOError as e:
      log.debug(f"lineno: {inspect.currentframe().f_lineno}, exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")
      raise e
    finally:
      sftp_client.close()


class RisVersionPromotionHistory():
  def __init__(self, ris_id, keys_list, date_after):
    self._ris_id = ris_id
    ris_info = ris_id.split('/')
    self.group, self.component, self.version = ris_info[0], ris_info[1], ris_info[2]
    self._ris_status_file = f'{self.group}-{self.component}-{self.version}-status.xml'
    self._ris_file = 'ris.xml'
    self._status_keys_list = []
    self._date_after = LocalTimeZone.timezone.localize(datetime.strptime(date_after, "%Y-%m-%dT%H:%M:%S"))
    for keys in keys_list.split(':'):
      self._status_keys_list.append(keys.split(','))

  def download_files(self):
    prefix = os.path.join(self._ris_id)
    for file in [self._ris_status_file, 'ris.xml']:
      FileDownloader().download_file(prefix, file)

  def get_status_list(self):
    self.download_files()
    with open(self._ris_status_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    key_list = [item for sublist in self._status_keys_list for item in sublist]
    status_list = [ {elem.attrib['key']: elem.attrib['creation']} for elem in root if elem.tag == 'item' and elem.attrib['key'] in key_list and elem.attrib['value'] != 'stable_build' ]
    status_list = sorted(status_list, key=lambda d: list(d.keys()))
    return status_list

  def get_status_list_timestamp(self):
    status_list = self.get_status_list()
    for status in status_list:
      key = list(status.keys())[0]
      date = status[key].split('+')[0]
      status[key] = LocalTimeZone.timezone.localize(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")).timestamp()
    return status_list  

  def get_promotion_date_timestamp(self):
    status_list_timestamp = self.get_status_list_timestamp()
    latest_timestamps = []
    for keys in self._status_keys_list:
      timestamps = []
      for status in status_list_timestamp:
        key = list(status.keys())[0]
        if key in keys:
          timestamps.append(status[key])
      if len(timestamps) == 0:
        raise MissingStatus(f'lineno: {inspect.currentframe().f_lineno}, missing status: {keys}')
      log.debug(f'lineno: {inspect.currentframe().f_lineno}, timestamps: {timestamps}')
      timestamps.sort()
      latest_timestamps.append(timestamps[0])
    latest_timestamps.sort()
    return latest_timestamps[-1]

  def get_commit_date(self):
    with open(self._ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    return [elem.attrib for elem in root if elem.tag == 'buildsource'][0]['lastCommitDate']

  def get_commit_date_timestamp(self):
    commit_date = self.get_commit_date().split('+')[0]
    date = LocalTimeZone.timezone.localize(datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S"))
    log.debug(f'lineno: {inspect.currentframe().f_lineno}, date: {date}')
    log.debug(f'lineno: {inspect.currentframe().f_lineno}, self._date_after: {self._date_after}')
    if date < self._date_after:
      raise CommitDateTooOld(f'lineno: {inspect.currentframe().f_lineno}, date: {date}')
    return int(date.timestamp())
    
  def get(self):
    self.get_status_list()
    commit_date = self.get_commit_date_timestamp()
    promotion_date = self.get_promotion_date_timestamp()
    promotion_time = (promotion_date - commit_date) / 3600
    return {'ris_id': self._ris_id, 'ris_component': self.component, 'promotion_date': promotion_date, 'promotion_time': promotion_time, 'commit_date': commit_date}


class RisComponentPromotionHistory():
  def __init__(self, ris_group_component):
    self._ris_group_component = ris_group_component
    self._chronological = "chronological.xml"

  def download_file(self):
    FileDownloader().download_file(self._ris_group_component, self._chronological)

  def get_versions(self, date_after):
    date_after = LocalTimeZone.timezone.localize(datetime.strptime(date_after, "%Y-%m-%dT%H:%M:%S"))
    with open(self._chronological) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    versions = [ item.attrib['name'] for item in root if LocalTimeZone.timezone.localize(datetime.strptime(item.attrib['time'].split('+')[0], "%Y-%m-%dT%H:%M:%S")) > date_after ]
    versions.sort()
    return versions

  def get(self, keys_list, date_after):
    promotion_history = []
    self.download_file()
    versions = self.get_versions(date_after)
    for version in versions:
      ris_id = os.path.join(self._ris_group_component, version)
      try:
        promotion_history.append(RisVersionPromotionHistory(ris_id, keys_list, date_after).get())
      except Exception as e:
        log.debug(f"lineno: {inspect.currentframe().f_lineno}, exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")

    log.debug(f"lineno: {inspect.currentframe().f_lineno}, promotion_history: {promotion_history}")
    return promotion_history


class PromotionHistory():
  config_file = "ris_group_components.txt"
  table = 'promotion'

  def __init__(self):
    self.__ris_group_components, self.__history = [], []
    with open(self.config_file) as file:
      for line in file:
        self.__ris_group_components.append(line.strip())
    log.debug(f"lineno: {inspect.currentframe().f_lineno}, ris_group_components: {self.__ris_group_components}")

  def get(self, keys_list, date_after):
    for ris_group_component in self.__ris_group_components:
      self.__history += RisComponentPromotionHistory(ris_group_component).get(keys_list, date_after)
    log.debug(f"lineno: {inspect.currentframe().f_lineno}, self.__history: {self.__history}")
    return self

  def save(self):
    with DBConnector() as d:
      log.debug(f"lineno: {inspect.currentframe().f_lineno}, type(d): {type(d)}")
      for data in self.__history:
        command = f"insert into {self.table}(component, version, promotion_date, commit_date, promotion_time) values('{data['ris_component']}', '{data['ris_id']}', {data['promotion_date']}, {data['commit_date']}, {data['promotion_time']}) on duplicate key update promotion_date={data['promotion_date']}, commit_date={data['commit_date']}, promotion_time={data['promotion_time']}"
        log.debug(f"lineno: {inspect.currentframe().f_lineno}, command: {command}")
        d.execute(command)
        d._cnx.commit()
    return self

  def cleanup(self):
    os.system('rm *.xml')
        

def main(argv=None):
  logging.getLogger("paramiko").setLevel(logging.WARNING)
  week_ago = LocalTimeZone.timezone.localize(datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%dT%H:%M:%S')

  parser = argparse.ArgumentParser()
  parser.add_argument("-k", "--promotion-keys", dest="keys_list", default='component_upgrade_validated_with,release_upgrade_validated_with:ready_for_product', help="keys list, eg: 'component_upgrade_validated_with,release_upgrade_validated_with:ready_for_product")
  parser.add_argument("-d", "--date-after", dest="date_after", default=f'{week_ago}', help="date after, eg: 2020-04-18T00:33:58")
  args = parser.parse_args()
  log.debug(f"lineno: {inspect.currentframe().f_lineno}, args: {args}")

  PromotionHistory().get(args.keys_list, args.date_after).save().cleanup()


if __name__ == "__main__":
  sys.exit(main())
