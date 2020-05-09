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

  def download_file(self, prefix, file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(self.backend, username=self.backend_username, password=self.backend_password, look_for_keys=False, timeout=60)
    sftp_client = ssh.open_sftp()
    file_path = os.path.join(self.package_home, prefix, file)
    log.debug(f'{__file__}:{inspect.currentframe().f_lineno}: file_path: {file_path}')
    try:
      sftp_client.get(file_path, file)
    except IOError as e:
      log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")
      raise e
    finally:
      sftp_client.close()
        

def main(argv=None):
  pass

if __name__ == "__main__":
  sys.exit(main())
