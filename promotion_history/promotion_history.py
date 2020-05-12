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
from exceptions import MissingStatus, CommitDateTooOld, MissingBuildSource
from filedownloader import FileDownloader
from functools import wraps
from log import log
from pytz import timezone
from ris_info import RisVersionInfo, RisComponentHistory


class DBConnectorPromotionHistory(DBConnector):
  database = 'promotion_history'
  table = 'promotion'

  def create_table(self):
    self._cursor.execute(f"create table {self.table} (component varchar(50), version varchar(80) primary key, promotion_date int(10), commit_date int(10), promotion_time int(10))")


class RisVersionPromotionHistory(RisVersionInfo):
  def __init__(self, ris_id, keys_list, date_after, sftp_client):
    super().__init__(ris_id)
    self._sftp_client = sftp_client
    self._ris_status_file = f'{self.group}-{self.component}-{self.version}-status.xml'
    self._files_to_download = [self._ris_status_file, self.ris_file]
    self._status_keys_list = []
    self._date_after = LocalTimeZone.timezone.localize(datetime.strptime(date_after, "%Y-%m-%dT%H:%M:%S"))
    for keys in keys_list.split(':'):
      self._status_keys_list.append(keys.split(','))

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
        raise MissingStatus(f'{__file__}:{inspect.currentframe().f_lineno}: missing status: {keys}')
      log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: timestamps: {timestamps}')
      timestamps.sort()
      latest_timestamps.append(timestamps[0])
    latest_timestamps.sort()
    return latest_timestamps[-1]

  def get_commit_date(self):
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    result = [elem for elem in root if elem.tag == 'buildsource']
    if len(result) > 0 and 'lastCommitDate' in result[0].attrib:
      return result[0].attrib['lastCommitDate']
    else:
      raise MissingBuildSource

  def get_commit_date_timestamp(self):
    commit_date = self.get_commit_date().split('+')[0]
    date = LocalTimeZone.timezone.localize(datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S"))
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: date: {date}')
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: self._date_after: {self._date_after}')
    if date < self._date_after:
      raise CommitDateTooOld(f'{__file__}:{inspect.currentframe().f_lineno}: date: {date}')
    return int(date.timestamp())
    
  def get(self):
    self.get_status_list()
    commit_date = self.get_commit_date_timestamp()
    promotion_date = self.get_promotion_date_timestamp()
    promotion_time = (promotion_date - commit_date) / 3600
    return {'ris_id': self._ris_id, 'ris_component': self.component, 'promotion_date': promotion_date, 'promotion_time': promotion_time, 'commit_date': commit_date}


class RisComponentPromotionHistory(RisComponentHistory):
  def __init__(self, ris_group_component):
    self._promotion_history = []
    super().__init__(ris_group_component)

  def get(self, keys_list, date_after):
    with FileDownloader() as sftp_client:
      self.download_file(sftp_client)
      versions = self.get_versions(date_after)
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: versions: {versions}")
      for version in versions:
        ris_id = os.path.join(self._ris_group_component, version)
        try:
          self._promotion_history.append(RisVersionPromotionHistory(ris_id, keys_list, date_after, sftp_client).get())
        except Exception as e:
          log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")
  
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: promotion_history: {self._promotion_history}")
    return self

  def save(self):
    with DBConnectorPromotionHistory() as d:
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: type(d): {type(d)}")
      for data in self._promotion_history :
        command = f"insert into {DBConnectorPromotionHistory.table}(component, version, promotion_date, commit_date, promotion_time) values('{data['ris_component']}', '{data['ris_id']}', {data['promotion_date']}, {data['commit_date']}, {data['promotion_time']}) on duplicate key update promotion_date={data['promotion_date']}, commit_date={data['commit_date']}, promotion_time={data['promotion_time']}"
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: command: {command}")
        d.execute(command)
        d._cnx.commit()
    return self

  def cleanup(self):
    os.system('rm *.xml')


class PromotionHistory():
  config_file_headers = ['group', 'component', 'version', 'committer']

  def __init__(self, config_file):
    self.__ris_group_components, self.__history = [], []
    with open(config_file) as file:
      f_csv = csv.DictReader(file)
      for r in f_csv:
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: group: {r['group']}")
        self.__ris_group_components.append(os.path.join(r['group'], r['component']))
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: ris_group_components: {self.__ris_group_components}")

  def get_save(self, keys_list, date_after):
    for ris_group_component in self.__ris_group_components:
      RisComponentPromotionHistory(ris_group_component).get(keys_list, date_after).save().cleanup()
    return self


def main(argv=None):
  logging.getLogger("paramiko").setLevel(logging.WARNING)
  week_ago = LocalTimeZone.timezone.localize(datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%dT%H:%M:%S')

  parser = argparse.ArgumentParser()
  parser.add_argument("-k", "--promotion-keys", dest="keys_list", default='component_upgrade_validated_with,release_upgrade_validated_with:ready_for_product', help="keys list, eg: 'component_upgrade_validated_with,release_upgrade_validated_with:ready_for_product")
  parser.add_argument("-d", "--date-after", dest="date_after", default=f'{week_ago}', help="date after, eg: 2020-04-01T00:33:58")
  parser.add_argument("-f", "--config-file", dest="config_file", default='ris_group_components_all.csv', help="ris group components file, eg: ris_group_components_all.csv")
  args = parser.parse_args()
  log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: args: {args}")

  PromotionHistory(args.config_file).get_save(args.keys_list, args.date_after)


if __name__ == "__main__":
  sys.exit(main())
