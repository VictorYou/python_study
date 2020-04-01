import os
import paramiko

class RisPromotionHistory():
  backend = '10.9.137.108'
  backend_username = 'n8'
  backend_password = '8n'
  package_home = '/opt/mpp/packages/'
  status_key_list= ['component_upgrade_validated_with', 'release_upgrade_validated_with', 'ready_for_product']
  def __init__(self, ris_id):
    ris_info = ris_id.split('/')
    self.group, self.component, self.version = ris_info[0], ris_info[1], ris_info[2]
    self._ris_status_file = f'{self.group}-{self.component}-{self.version}-status.xml'
    self.download_files(self._ris_status_file, 'ris.xml')
    pass
    
  def download_files(self, *files):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(self.backend, username=self.backend_username, password=self.backend_password, look_for_keys=False, timeout=60)
    sftp_client = ssh.open_sftp()
    for file in files:
      file_path = os.path.join(self.package_home, self.group, self.component, self.version, file)
      sftp_client.get(file_path, file)
    sftp_client.close()

  def get_status_list(self, status_file):
    pass

  def get_promotion_date(self):
    pass

  def get_commit_date(self):
    pass

  def promotion_time(self):
    pass
