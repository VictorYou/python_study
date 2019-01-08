#!/usr/bin/python

SSH_TIMEOUT = 60

import sys
import time
import logging
log = logging.getLogger(__name__)

def new_ssh_connection(host, user, passwd, fake_ssh_client = None):
    """ open ssh session to host using user/passwd """
    if fake_ssh_client is not None:
        # testing mode: mock SSHClient
        log.debug('provided ssh client: %s' % (fake_ssh_client))
        return fake_ssh_client
    import paramiko
    ##paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
    ssh = paramiko.SSHClient()
    log.info('SSH(%s): %s as %s/%s' % (ssh, host, user, passwd))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        log.info('Connecting to host: %s user: %s timeout: %u', host, user, SSH_TIMEOUT)
        ssh.connect(host, username=user, password=passwd, look_for_keys=False, timeout=SSH_TIMEOUT)
    except paramiko.ssh_exception.SSHException as ex:
        log.error("Error Opening SSH Connection to %s: %s" % (host, sys.exc_info()[0]))
        return None
    return ssh 

def ssh_exec_command(ssh_connection, cmd, number_of_retries=5):
    ''' wrapper around ssh_connection.exec_command() for
        retrying ssh command 

        param 'number_of_retries' determines how often the command should be 
            retried
    '''
    from paramiko.ssh_exception import SSHException
    for trial in range(max(number_of_retries + 1, 1)):
        try:
            log.debug('Executing SSH command: %s' % (cmd))
            (stdin, stdout, stderr) = ssh_connection.exec_command(cmd)
            log.debug('SSH command %s succeeded' % (cmd))
            return stdin, stdout, stderr
        except SSHException as ex:
            log.error("%s" % ((sys.exc_info()[0])))
            time.sleep(1)
    raise ex
