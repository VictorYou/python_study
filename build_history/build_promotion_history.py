import logging
import os
import paramiko
import re
import sys
import xml.etree.ElementTree as ET

from datetime import datetime
from log import log
from pytz import timezone

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
    file_path = os.path.join(self.package_home, prefix, self.version, file)
    sftp_client.get(file_path, file)
    sftp_client.close()


class RisVersionPromotionHistory():
  status_keys_list = [['component_upgrade_validated_with', 'release_upgrade_validated_with', 'scratch_install_validated_with'], ['ready_for_product']]
  timezone = timezone('Europe/Helsinki')

  def __init__(self, ris_id):
    self._ris_id = ris_id
    ris_info = ris_id.split('/')
    self.group, self.component, self.version = ris_info[0], ris_info[1], ris_info[2]
    self._ris_status_file = f'{self.group}-{self.component}-{self.version}-status.xml'
    self._ris_file = 'ris.xml'

  def download_files(self):
    prefix = os.path.join(self.group, self.component)
    for file in files:
      FileDownloader().download_file(prefix, file)

  def get_status_list(self):
    self.download_files()
    with open(self._ris_status_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    key_list = [item for sublist in self.status_keys_list for item in sublist]
    status_list = [{elem.attrib['key']: elem.attrib['creation']} for elem in root if elem.tag == 'item' and elem.attrib['key'] in key_list and re.match('netact/product/.*', elem.attrib['value'])]
    status_list_rfp = [{'ready_for_product': elem.attrib['creation']} for elem in root if elem.tag == 'item' and elem.attrib['key'] == 'ready_for_product']
    status_list += status_list_rfp
    status_list = sorted(status_list, key=lambda d: list(d.keys()))
    return status_list

  def get_status_list_timestamp(self):
    status_list = self.get_status_list()
    for status in status_list:
      key = list(status.keys())[0]
      date = status[key].split('+')[0]
      status[key] = self.timezone.localize(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")).timestamp()
    return status_list  

  def get_promotion_date_timestamp(self):
    status_list_timestamp = self.get_status_list_timestamp()
    latest_timestamps = []
    for keys in self.status_keys_list:
      timestamps = []
      for status in status_list_timestamp:
        key = list(status.keys())[0]
        if key in keys:
          timestamps.append(status[key])
      log.debug(f'timestamps: {timestamps}')
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
    return int(self.timezone.localize(datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S")).timestamp())
    
  def get_promotion_history(self):
    self.get_status_list()
    commit_date = self.get_commit_date_timestamp()
    promotion_date = self.get_promotion_date_timestamp()
    return {'ris_id': self._ris_id, 'promotion_date': promotion_date, 'promotion_time': promotion_date - commit_date }


class RisComponentPromotionHistory():
  def __init__(self, ris_group_component):
    self._ris_group_component = ris_group_component
    self._chronological = "chronological.xml"

  def download_file(self):
    FileDownloader().download_file(self._chronological)

  def get_versions(self):
    with open(self._chronological) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    versions = [item.attrib['name'] for item in root]
    versions.sort()
    return versions

  def get_promotion_history(self):
    promotion_history = []
    versions = self.get_versions()
    for version in versions:
      ris_id = os.path.join(self._ris_group_component, version)
      promotion_history.append(RisVersionPromotionHistory(ris_id).get_promotion_history)
    return promotion_history


class PromotionHistory():
  config_file = "ris_group_components.txt"

  def __init__(self):
    self.__ris_group_components, self.__history = [], []
    with open(self.config_file) as file:
      for line in file:
        self.__ris_group_components.append(line.strip())
    log.debug(f"ris_group_components: {self.__ris_group_components}")

  def get_promotion_history(self):
    for ris_group_component in self.__ris_group_components:
      self.__history.append(RisComponentPromotionHistory(ris_group_component).get_promotion_history())
    log.debug(f"self.__history: {self.__history}")
        

def main(argv=None):
  PromotionHistory().get_promotion_history()


if __name__ == "__main__":
  sys.exit(main())
