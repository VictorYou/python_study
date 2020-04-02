import logging
import os
import paramiko
import re
import xml.etree.ElementTree as ET

from datetime import datetime
from log import log

class RisPromotionHistory():
  backend = '10.9.137.108'
  backend_username = 'n8'
  backend_password = '8n'
  package_home = '/opt/mpp/packages/'
  status_keys_list = [['component_upgrade_validated_with', 'release_upgrade_validated_with', 'scratch_install_validated_with'], ['ready_for_product']]

  def __init__(self, ris_id):
    ris_info = ris_id.split('/')
    self.group, self.component, self.version = ris_info[0], ris_info[1], ris_info[2]
    self._ris_status_file = f'{self.group}-{self.component}-{self.version}-status.xml'
    self._ris_file = 'ris.xml'

  def download_files(self):
    files = [self._ris_status_file, 'ris.xml']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(self.backend, username=self.backend_username, password=self.backend_password, look_for_keys=False, timeout=60)
    sftp_client = ssh.open_sftp()
    for file in files:
      file_path = os.path.join(self.package_home, self.group, self.component, self.version, file)
      sftp_client.get(file_path, file)
    sftp_client.close()

  def get_status_list(self):
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
      status[key] = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").timestamp()
    return status_list  

  def get_promotion_date_timestamp(self):
    status_list_timestamp = self.get_status_list_timestamp()
    log.debug(f'status_list_timestamp: {status_list_timestamp}')
    latest_timestamp = 0
    for keys in self.status_keys_list:
      timestamps = []
      for status in status_list_timestamp:
        key = list(status.keys())[0]
        if key in keys:
          timestamps.append(status[key])
      log.debug(f'timestamps: {timestamps}')
      timestamps.sort()
      timestamp = timestamps[-1]
      if timestamp > latest_timestamp:
        latest_timestamp = timestamp
    return latest_timestamp

  def get_commit_date(self):
    with open(self._ris_file) as file:
      tree = ET.parse(file)
    root = tree.getroot()
    return [elem.attrib for elem in root if elem.tag == 'buildsource'][0]['lastCommitDate']

  def get_commit_date_timestamp(self):
    commit_date = self.get_commit_date().split('+')[0]
    return int(datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%S").timestamp())
    

  def promotion_time(self):
    pass
