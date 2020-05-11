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
from exceptions import MissingStatus, CommitDateTooOld
from filedownloader import FileDownloader
from functools import wraps
from log import log
from pytz import timezone
from ris_info import RisVersionInfo, RisComponentHistory


class RisVersionCommitter(RisVersionInfo):
  def __init__(self, ris_id):
    super().__init__(ris_id)
    self._files_to_download = [self.ris_file]

  def get(self):
    self.download_files()
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    result = [elem.attrib for elem in root if elem.tag == 'buildsource']
    if len(result) > 0 and 'lastCommiter' in result[0]:
      return result[0]['lastCommiter']
    else:
      return 'Unknown'


class RisVersionDependencyVersion(RisVersionInfo):
  def __init__(self, ris_id):
    super().__init__(ris_id)
    self._files_to_download = [self.ris_file]

  def get(self):
    self.download_files()
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    result = [os.path.join(x[0].attrib['group'], x[0].attrib['component'], x[0].attrib['version']) for x in root if x.tag == 'dependency']
    result.sort()
    return result


class RisComponentLatestVersion(RisComponentHistory):
  def get(self, date_after):
    ris_list = []
    self.download_file()
    versions = self.get_versions(date_after)
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: versions: {versions}")
    ris_version = os.path.join(self._ris_group_component, versions[0])
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: ris_version: {ris_version}")
    return ris_version


class LatestNetActProductDependency():
  def __init__(self):
    self.__dependency_versions = []

  def get(self, date_after):
    latest_ris_version = RisComponentLatestVersion('netact/product').get(date_after)
    ris_versions = RisVersionDependencyVersion(latest_ris_version).get()
    for ris_version in ris_versions:
      self.__dependency_versions.append((ris_version.split('/')[0], ris_version.split('/')[1], ris_version.split('/')[2], RisVersionCommitter(ris_version).get()))
    return self

  def save(self):
    headers = ['group', 'component', 'version', 'committer']
    with open('ris_group_components_all.txt', 'w') as f:
      f_csv = csv.writer(f)
      f_csv.writerow(headers)
      f_csv.writerows(self.__dependency_versions)
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

  LatestNetActProductDependency().get(args.date_after).save().cleanup()


if __name__ == "__main__":
  sys.exit(main())
