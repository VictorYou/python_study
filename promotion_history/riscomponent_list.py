import argparse
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
from exceptions import MissingStatus, CommitDateTooOld
from filedownloader import FileDownloader
from functools import wraps
from log import log
from pytz import timezone
from ris_info import RisVersionInfo, RisComponentHistory


class RisVersionDependency(RisVersionInfo):
  def __init__(self, ris_id):
    super().__init__(ris_id)
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
        raise MissingStatus(f'lineno: {inspect.currentframe().f_lineno}, missing status: {keys}')
      log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: timestamps: {timestamps}')
      timestamps.sort()
      latest_timestamps.append(timestamps[0])
    latest_timestamps.sort()
    return latest_timestamps[-1]

  def get_commit_date(self):
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    return [elem.attrib for elem in root if elem.tag == 'buildsource'][0]['lastCommitDate']

  def get_commit_date_timestamp(self):
    commit_date = self.get_commit_date().split('+')[0]
    date = LocalTimeZone.timezone.localize(datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S"))
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: date: {date}')
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: self._date_after: {self._date_after}')
    if date < self._date_after:
      raise CommitDateTooOld(f'lineno: {inspect.currentframe().f_lineno}, date: {date}')
    return int(date.timestamp())
    
  def get(self):
    self.get_status_list()
    commit_date = self.get_commit_date_timestamp()
    promotion_date = self.get_promotion_date_timestamp()
    promotion_time = (promotion_date - commit_date) / 3600
    return {'ris_id': self._ris_id, 'ris_component': self.component, 'promotion_date': promotion_date, 'promotion_time': promotion_time, 'commit_date': commit_date}


class RisComponentLatestVersion(RisComponentHistory):
  def get(self, date_after):
    ris_list = []
    self.download_file()
    versions = self.get_versions(date_after)
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: versions: {versions}")
    ris_version = os.path.join(self._ris_group_component, versions[0])
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: ris_version: {ris_version}")
    return []
#    return RisVersionDependency(ris_version)


class LatestNetActProduct():
  def __init__(self):
    self.__dependency = []

  def get(self, date_after):
    self.__dependency = RisComponentLatestVersion('netact/product').get(date_after)
    return self

  def save(self):
    return self

  def cleanup(self):
    os.system('rm *.xml')
        

def main(argv=None):
  logging.getLogger("paramiko").setLevel(logging.WARNING)
  week_ago = LocalTimeZone.timezone.localize(datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%dT%H:%M:%S')

  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--date-after", dest="date_after", default=f'{week_ago}', help="date after, eg: 2020-04-01T00:33:58")
  args = parser.parse_args()
  log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: args: {args}")

  LatestNetActProduct().get(args.date_after).save().cleanup()


if __name__ == "__main__":
  sys.exit(main())
