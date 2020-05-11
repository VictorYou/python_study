import inspect
import logging
import os
import paramiko
import sys

from log import log

class FileDownloader():
  backend = '10.9.137.108'
  backend_username = 'n8'
  backend_password = '8n'
  package_home = '/opt/mpp/packages/'

  def __init__(self):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(self.backend, username=self.backend_username, password=self.backend_password, look_for_keys=False, timeout=60)
    self._sftp_client = ssh.open_sftp()

  def __enter__(self):
    return self._sftp_client

  def __exit__(self, exc_ty, exc_val, tb):
    self._sftp_client.close()


def main(argv=None):
  pass

if __name__ == "__main__":
  sys.exit(main())
