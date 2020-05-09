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


class RisVersionCommitter(RisVersionInfo):
  def __init__(self, ris_id):
    super().__init__(ris_id)
    self._files_to_download = [self.ris_file]

  def get(self):
    self.download_files()
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    return [elem.attrib for elem in root if elem.tag == 'buildsource'][0]['lastCommiter']


class RisVersionDependencyVersion(RisVersionInfo):
  def __init__(self, ris_id):
    super().__init__(ris_id)
    self._files_to_download = [self.ris_file]

  def get(self):
    self.download_files()
    with open(self.ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    return True


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
    self.__dependency_version = []

  def get(self, date_after):
    latest_ris_version = RisComponentLatestVersion('netact/product').get(date_after)
    RisVersionDependencyVersion(latest_ris_version)
    return self

  def save(self):
    return self

  def cleanup(self):
    pass
#    os.system('rm *.xml')
        

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
