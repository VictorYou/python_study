import argparse
import inspect
import logging
import os
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


class RisVersionInfo():
  ris_file = 'ris.xml'
  package_home = '/opt/mpp/packages/'

  def __init__(self, ris_id):
    self._ris_id = ris_id
    ris_info = ris_id.split('/')
    self.group, self.component, self.version = ris_info[0], ris_info[1], ris_info[2]

  def download_files(self):
    prefix = os.path.join(self._ris_id)
    for file in self._files_to_download:
      try:
        file_path = os.path.join(self.package_home, prefix, file)
        log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: file_path: {file_path}')
        self._sftp_client.get(file_path, file)
      except IOError as e:
        log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")
        raise e


class RisComponentHistory():
  package_home = '/opt/mpp/packages/'

  def __init__(self, ris_group_component):
    self._ris_group_component = ris_group_component
    self._chronological = "chronological.xml"

  def download_file(self, sftp_client):
    file_path = os.path.join(self.package_home, self._ris_group_component, self._chronological)
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: file_path: {file_path}')
    try:
      sftp_client.get(file_path, self._chronological)
    except IOError as e:
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")
      raise e

  def get_versions(self, date_after):
    date_after = LocalTimeZone.timezone.localize(datetime.strptime(date_after, "%Y-%m-%dT%H:%M:%S"))
    with open(self._chronological) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    versions = [ item.attrib['name'] for item in root if LocalTimeZone.timezone.localize(datetime.strptime(item.attrib['time'].split('+')[0], "%Y-%m-%dT%H:%M:%S")) > date_after ]
    versions.sort()
    return versions


def main(argv=None):
  pass


if __name__ == "__main__":
  sys.exit(main())
