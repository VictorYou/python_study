#!/usr/bin/python

import re

from .ilo_connect import new_ssh_connection, ssh_exec_command
import time
import logging
log = logging.getLogger(__name__)

TIMEOUT_FOR_ILO_POWER_CHECK = 5
NUMBER_OF_ILO_POWER_CHECKS = 30

def power(ssh_connection):
    (stdin, stdout, stderr) = ssh_exec_command(ssh_connection, 'power')
    for x in stdout.readlines():
        m = re.match(r'power: server power is currently: (\S+)', x.rstrip())
        if m is not None:
            return not m.group(1) == 'Off'

def power_on(ssh_connection):
    (stdin, stdout, stderr) = ssh_exec_command(ssh_connection, 'power on')
    return stdout.readlines()

def power_off(ssh_connection):
    (stdin, stdout, stderr) = ssh_exec_command(ssh_connection, 'power off hard')
    return stdout.readlines()

def power_lab_ilos_onoff(lab_entry, power_on_wanted=True):
    '''
        Power all ILO servers in given (Sprint)lab on or off

        labentry is a list containing 'ESXis' entries.
        Each entry is a tulple describing a single ESXi host:
            (<esxi ip or name>, <ILO ip or name>, <ilo user>, <ilo password>)
    '''
    from paramiko.ssh_exception import SSHException
    ilo_servers = _connect_to_ilo_servers(lab_entry)
    log.info('ilo_servers: %s' % (ilo_servers))
    successful_ilo_servers = [en['ilo_ip'] 
        for en in filter(lambda en: en['ssh'] is not None, ilo_servers)]
    if len(successful_ilo_servers) < len(lab_entry):
        failed_ilo_servers = [en['ilo_ip'] 
            for en in filter(lambda en: en['ssh'] is None, ilo_servers)]
        msg = 'Unable to connect to all ILO servers: connected: %s, failed: %s' % \
            (successful_ilo_servers, failed_ilo_servers) 
        log.error(msg)
        raise SSHException(msg)
    log.debug('Starting to change power states to %s', ('ON' if power_on_wanted else 'OFF'))
    map(
        lambda ilo_entry: _switch_power_state(ilo_entry, power_on_wanted),
        ilo_servers)
    for i in range(NUMBER_OF_ILO_POWER_CHECKS):
        ilo_servers_still_to_handle = filter(
            lambda ilo_entry: _power_state_not_as_wanted(ilo_entry, power_on_wanted),
            ilo_servers) 
        log.info('[%u] ilo_servers: %s' % (i, ilo_servers))
        if ilo_servers_still_to_handle == []:
            break
        time.sleep(TIMEOUT_FOR_ILO_POWER_CHECK)


def _connect_to_ilo_servers(lab_entry):
    return [
        dict(ssh = new_ssh_connection(*en[1:]), ilo_ip=en[1],) 
        for en in lab_entry
    ]

def _power_state_not_as_wanted(ilo_entry, power_state_wanted):
    '''
        Checks whether power state of the ILO server described by 'ilo_entry'
        is according to the required state in 'power_state_wanted'. 

        If ilo_entry['power_state'] is unset (=None), it will be fetched from ILO server.
    '''
    if ilo_entry.get('power_state') is not None and ilo_entry['power_state'] == power_state_wanted:
        return True
    ilo_entry['power_state'] = power_state = power(ilo_entry['ssh'])
    return power_state != power_state_wanted

def _switch_power_state(ilo_entry, power_state_wanted, test_only=False):
    ilo_conn = ilo_entry['ssh']
    if _power_state_not_as_wanted(ilo_entry, power_state_wanted):
        if power_state_wanted:
            log.info('power_on(ilo_conn)')
            if not test_only: power_on(ilo_conn)
        else:
            log.info('power_off(ilo_conn)')
            if not test_only: power_off(ilo_conn)
    else:
        log.info('power is already ' + ('on' if power_state_wanted else 'off'))
