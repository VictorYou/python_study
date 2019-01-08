#!/usr/bin/python

import ilo

import unittest
import mock
from StringIO import StringIO

import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class IloTests(unittest.TestCase):
    def setUp(self):
        self.POWER_STATE_TEMPLATE = 'status=0\nstatus_tag=COMMAND COMPLETED\nThu Jun  7 10:14:06 2018\n\n\n\npower: server power is currently: %s\n\n\n\n'
    
    @mock.patch('paramiko.SSHClient.connect')
    def test_ilo_connection(self, ssh_client_connect):
        host, user, password = 'goodfakehost', 'ilouser', 'ilouser1'
        conn = ilo.new_ssh_connection(host, user, password)
        log.debug('conn: %s' % (conn))
        self.assertTrue(ssh_client_connect.called)
        self.assertEqual(type(conn).__name__, 'SSHClient')
        self.assertEqual(type(conn).__module__, 'paramiko.client')
        ##log.debug('conn: %s' % conn)
        ##log.debug(dir(ssh_client_connect))
        log.debug('SSH_connect.method_calls: %s' % (ssh_client_connect.method_calls))
        log.debug('SSH_connect.mock_calls: %s' % (ssh_client_connect.mock_calls))
        log.debug(ssh_client_connect.call_args)
        ssh_client_connect.assert_any_call(host, username=user, password=password, look_for_keys=mock.ANY, timeout=mock.ANY)

    @mock.patch('paramiko.SSHClient.connect')
    def test_ilo_connection_failure(self, ssh_client_connect):
        host, user, password = '23.100.122.175', 'ilouser', 'asdasdsd'
        ssh_client_connect.side_effect = Exception()
        with self.assertRaises(Exception) as ex:
            conn = ilo.new_ssh_connection(host, user, password)
        self.assertTrue(ssh_client_connect.call_count, 1)
        log.debug('SSH_connect.mock_calls: %s' % (ssh_client_connect.mock_calls))
        ssh_client_connect.assert_any_call(host, username=user, password=password, look_for_keys=mock.ANY, timeout=mock.ANY)

    @mock.patch('paramiko.SSHClient.exec_command')
    def test_ssh_exec_command(self, ssh_client_exec_command):
        import paramiko
        ssh_client = paramiko.SSHClient()
        log.debug('ssh_client: %s' % (ssh_client))
        expected_out_str, expected_err_str = "x = y", "MESS"
        ssh_client_exec_command.return_value = None, StringIO(expected_out_str), StringIO(expected_err_str)
        (_in, out, err) = ilo.ilo_connect.ssh_exec_command(ssh_client, 'x')
        self.assertTrue(ssh_client_exec_command.called)
        log.debug('SSH_exec_command.mock_calls: %s' % (ssh_client_exec_command.mock_calls))
        ssh_client_exec_command.assert_any_call('x')
        out_str = out.readlines()
        err_str = err.readlines()
        log.debug('stdout: %s\tstderr: %s' % (out_str, err_str))
        self.assertEqual([expected_out_str], out_str)
        self.assertEqual([expected_err_str], err_str)

    @mock.patch('time.sleep')
    @mock.patch('paramiko.SSHClient.exec_command')
    def test_ssh_exec_command_fails_with_SSHException(self, ssh_client_exec_command, time_sleep):
        import paramiko
        ssh_client = paramiko.SSHClient()
        log.debug('ssh_client: %s' % (ssh_client))
        ssh_client_exec_command.side_effect = paramiko.ssh_exception.SSHException()
        with self.assertRaises(paramiko.ssh_exception.SSHException) as ex:
            ilo.ilo_connect.ssh_exec_command(ssh_client, 'some nice command that does not matter')
        log.debug('Mocked calls to time.sleep: %s', time_sleep.mock_calls)
        self.assertEqual(time_sleep.call_count, 6)

    @mock.patch('time.sleep')
    @mock.patch('paramiko.SSHClient.exec_command')
    def test_ssh_exec_command_fails_with_SSHException_after_11_retrials(self, ssh_client_exec_command, time_sleep):
        import paramiko
        ssh_client = paramiko.SSHClient()
        log.debug('ssh_client: %s' % (ssh_client))
        ssh_client_exec_command.side_effect = paramiko.ssh_exception.SSHException()
        with self.assertRaises(paramiko.ssh_exception.SSHException) as ex:
            ilo.ilo_connect.ssh_exec_command(ssh_client, 'some nice command that does not matter', 11)
        log.debug('Mocked calls to time.sleep: %s', time_sleep.mock_calls)
        self.assertEqual(time_sleep.call_count, 12)

    @mock.patch('time.sleep')
    @mock.patch('paramiko.SSHClient.exec_command')
    def test_ssh_exec_command_number_of_retrials_was_invalid(self, ssh_client_exec_command, time_sleep):
        import paramiko
        ssh_client = paramiko.SSHClient()
        log.debug('ssh_client: %s' % (ssh_client))
        ssh_client_exec_command.side_effect = paramiko.ssh_exception.SSHException()
        with self.assertRaises(paramiko.ssh_exception.SSHException) as ex:
            ilo.ilo_connect.ssh_exec_command(ssh_client, 'some nice command that does not matter', -1)
        log.debug('Mocked calls to time.sleep: %s', time_sleep.mock_calls)
        self.assertEqual(time_sleep.call_count, 1)

    @mock.patch('paramiko.SSHClient.exec_command')
    @mock.patch('paramiko.SSHClient')
    def test_power_on(self, ssh_client, ssh_client_exec_command):
        ilo_state_expected, ilo_retval = (True,'On')
        ssh_client_exec_command.return_value = None, StringIO(self.POWER_STATE_TEMPLATE % (ilo_retval)), None
        ilo_state = ilo.power(ssh_client)
        self.assertTrue(ssh_client_exec_command.called)
        log.debug('SSH_exec_command.mock_calls: %s' % (ssh_client_exec_command.mock_calls))
        log.debug('ILO State: %s\tExpected Outcome: %s Actual Outcome: %s' % (ilo_retval, ilo_state_expected, ilo_state))
        ssh_client_exec_command.assert_any_call('power')
        self.assertEqual(ilo_state_expected, ilo_state)

    @mock.patch('paramiko.SSHClient.exec_command')
    @mock.patch('paramiko.SSHClient')
    def test_power_off(self, ssh_client, ssh_client_exec_command):
        ilo_state_expected, ilo_retval = (False, 'Off')
        ssh_client_exec_command.return_value = None, StringIO(self.POWER_STATE_TEMPLATE % (ilo_retval)), None
        ilo_state = ilo.power(ssh_client)
        self.assertTrue(ssh_client_exec_command.called)
        log.debug('SSH_exec_command.mock_calls: %s' % (ssh_client_exec_command.mock_calls))
        log.debug('ILO State: %s\tExpected Outcome: %s Actual Outcome: %s' % (ilo_retval, ilo_state_expected, ilo_state))
        ssh_client_exec_command.assert_any_call('power')
        self.assertEqual(ilo_state_expected, ilo_state)

    @mock.patch('paramiko.SSHClient.exec_command')
    @mock.patch('paramiko.SSHClient')
    def test_power_on(self, ssh_client, ssh_client_exec_command):
        ssh_client_exec_command.return_value = None, StringIO('OK'), None
        retval = ilo.power_on(ssh_client)
        log.debug('SSH_exec_command.mock_calls: %s' % (ssh_client_exec_command.mock_calls))
        ssh_client_exec_command.assert_any_call('power on')

    @mock.patch('paramiko.SSHClient.exec_command')
    @mock.patch('paramiko.SSHClient')
    def test_power_off(self, ssh_client, ssh_client_exec_command):
        ssh_client_exec_command.return_value = None, StringIO('OK'), None
        retval = ilo.power_off(ssh_client)
        log.debug('SSH_exec_command.mock_calls: %s' % (ssh_client_exec_command.mock_calls))
        ssh_client_exec_command.assert_any_call('power off hard')

    @mock.patch('paramiko.SSHClient.connect')
    def test_ilo_power_onoff_one_ilo_server_does_not_work(self, ssh_client_connect):
        from paramiko.ssh_exception import SSHException
        ssh_client_connect.side_effect = [None, SSHException(), None]
        with self.assertRaises(SSHException) as sshex:
            ilo.power_lab_ilos_onoff([
                ('host001', 'ilo001', 'joy', '#"!?<'),
                ('host002', 'ilo002', 'joy', '#"!?<'),
                ('host003', 'ilo003', 'joy', '#"!?<'),
            ])
        log.debug("SSHException: error message is '%s'", sshex.exception.message)
        self.assertEqual('''Unable to connect to all ILO servers: connected: ['ilo001', 'ilo003'], failed: ['ilo002']''',
                         sshex.exception.message)
        log.debug('calls: %s', ssh_client_connect.mock_calls)
        self.assertEqual(ssh_client_connect.call_count, 3, 'there must be three login attempts')
        ssh_client_connect.assert_any_call('ilo001', username='joy', password='#"!?<', look_for_keys=mock.ANY, timeout=mock.ANY)
        ssh_client_connect.assert_any_call('ilo002', username='joy', password='#"!?<', look_for_keys=mock.ANY, timeout=mock.ANY)
        ssh_client_connect.assert_any_call('ilo003', username='joy', password='#"!?<', look_for_keys=mock.ANY, timeout=mock.ANY)

    def test_one_ilo_power_on(self):
        log.debug('ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = %s' % (ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS))
        ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = 1
        fakeSSHClient = FakeSSHClient('ilo01', 'u1', 'p1',
            [
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
                ('power on', (None,StringIO("\n"),None)),
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'On'),None)),
            ],
        ) 
        ilo.power_lab_ilos_onoff([
                (None, None, None, None, fakeSSHClient),
        ])
        self.assertEqual(fakeSSHClient.behavior, [])

    def test_one_ilo_power_off(self):
        log.debug('ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = %s' % (ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS))
        ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = 1
        fakeSSHClient = FakeSSHClient('ilo01', 'u1', 'p1',
            [
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'On'),None)),
                ('power off hard', (None,StringIO("\n"),None)),
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
            ],
        ) 
        ilo.power_lab_ilos_onoff([
                (None, None, None, None, fakeSSHClient),
        ],
        False)
        self.assertEqual(fakeSSHClient.behavior, [])

    @mock.patch('time.sleep')
    def test_one_ilo_power_on_several_checks(self, time_sleep):
        log.debug('ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = %s' % (ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS))
        ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = 3
        ilo.ilo_power.TIMEOUT_ILO_POWER_CHECKS = 1
        fakeSSHClient = FakeSSHClient('ilo01', 'u1', 'p1',
            [
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
                ('power on', (None,StringIO("\n"),None)),
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'On'),None)),
            ],
        ) 
        ilo.power_lab_ilos_onoff([
                (None, None, None, None, fakeSSHClient),
        ],
        True)
        self.assertEqual(fakeSSHClient.behavior, [])

    @mock.patch('time.sleep')
    def test_one_ilo_power_on_when_already_on(self, time_sleep):
        log.debug('ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = %s' % (ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS))
        ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = 5
        fakeSSHClient = FakeSSHClient('ilo01', 'u1', 'p1',
            [
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'On'),None)),
            ],
        ) 
        ilo.power_lab_ilos_onoff([
                (None, None, None, None, fakeSSHClient),
        ])
        self.assertEqual(fakeSSHClient.behavior, [])

    @mock.patch('time.sleep')
    def test_one_ilo_power_off_when_already_off(self, time_sleep):
        log.debug('ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = %s' % (ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS))
        ilo.ilo_power.NUMBER_OF_ILO_POWER_CHECKS = 5
        fakeSSHClient = FakeSSHClient('ilo01', 'u1', 'p1',
            [
                ('power', (None,StringIO(self.POWER_STATE_TEMPLATE % 'Off'),None)),
            ],
        ) 
        ilo.power_lab_ilos_onoff([
                (None, None, None, None, fakeSSHClient),
        ],
        False)
        self.assertEqual(fakeSSHClient.behavior, [])

class FakeSSHClient():
    def __init__(self, host, user, password, behavior = {}):
        self.conn_data = (host, user, password)
        self.id = reduce(lambda s,sum: s+'/'+sum, (host, user, password))
        log.info('FakeSSHClient: %s' % (self.id))
        self.behavior = behavior
        self.unexpected_behavior = []
        self.calls_count = {}
    def exec_command(self, *args, **kwargs):
        log.info('[%12.12s] command_exec(%s %s)' % (self.id, args, kwargs))
        log.debug('behavior: %s' % (self.behavior))
        try:
            command, retval = self.behavior.pop(0)
        except:
            # store unexpected behavior for check
            self.unexpected_behavior.insert(0, (args[0]))
            raise Exception("Unexpected command: %s" % (args[0]))
        log.debug('''Expected command: '%s' and retval: %s''' % (command, retval))
        # check match of behavior
        assert(command == args[0])
        return retval
        
