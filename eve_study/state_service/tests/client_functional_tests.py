__author__ = 'ahvenjar'

import argparse
import unittest
import commands
import client
import sys
import logging
from StringIO import StringIO
import inspect
import re
import random

log = logging.getLogger(__name__)
log_level = logging.DEBUG
logging.basicConfig(level=log_level)

username = "functional_tester"
password = "testing"
url = "http://localhost:8000"

client.lab_pool_url = url
result_data = ""


class ClientFunctionalTests(unittest.TestCase):
    SERVICE_URL = url

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.held, sys.stderr = sys.stderr, StringIO()
        pass

    def _trace_test_name(self, func_name, argv):
        log.debug('*'*80)
        log.debug("TEST: {}({})".
                  format(str(func_name), str(argv)))
        log.debug('*'*80)

    def _resolve_docker_env(self):
        cmd = "docker ps | grep stateservice_labrequest_worker | cut -d' ' -f1"
        it = None
        stdout_value = commands.getoutput(cmd)
        if stdout_value:
            it = stdout_value
        return it

    def _exiting(self, text):
        log.error(text)
        sys.exit(1)

    def _command_line_operation_check(self, test_name, argv,
                                      except_name, except_msg,
                                      stdout_data=None,
                                      stdout_not_match_data=None, outfile=None):
        global result_data
        self._trace_test_name(test_name, argv)
        log.debug("Expected results  [{}:{}:{}]".
                  format(except_name, except_msg, stdout_data))
        try:
            it = self._resolve_docker_env()
            if it is None:
                self._exiting(" ### ERROR: Cannnot resolve working docker env!!")
            binary = "docker exec -it {} python /src/client.py -url {} ".format(it, self.SERVICE_URL)
            cmd = "{} {}".format(binary, argv)
            log.info("CMD: '{}'".format(cmd))
            stdout_value = commands.getoutput(cmd)
        except except_name as e:
            log.debug("EXCEPTION: [e.type:{},e.message:{}]".
                      format(type(e), e.message))
            self.assertEqual(except_msg, e.message)
            raise
        finally:
            self._assert_stdout_value(stdout_value, stdout_data,
                                      stdout_not_match_data, outfile)
            result_data = stdout_value

    def _assert_stdout_value(self, stdout_value, stdout_data, stdout_not_match_data, outfile=None):
        source = ""
        if outfile:
            stdout_value = self._read_data_from_file(outfile)
            source = " from file {}".format(outfile)
        log.debug("STDOUT {}:\n\n{}".format(source, str(stdout_value)))
        if stdout_data:
            self.assertRegexpMatches(stdout_value, stdout_data)
        if stdout_not_match_data:
            self.assertNotRegexpMatches(stdout_value, stdout_not_match_data)

    def _read_data_from_file(self, outfile):
        content = ""
        with open(outfile, 'r') as content_file:
            content = content_file.read()
            log.info(" *** Reading data from file '{}'".format(outfile))
            log.info("      content: '{}'".format(content))
        return content

    def _get_data_from_results(self, search_str):
        global result_data
        data_field = re.findall(search_str, result_data)
        if data_field:
            data_field = data_field[0]
        else:
            data_field = None
        log.info("_get_data_from_results(): '{}'".format(data_field))
        return data_field

    def test_parse_command_line_no_params(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "", SystemExit, 2,
                                           "too few arguments")

    def test_client_create_test_labs(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} create-test-labs".format(username),
                                           SystemExit, 0,
                                           "netact/product/99.17.03.0.123")

    def test_client_show_labs_all(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} show-labs".format(username),
                                           SystemExit, 0,
                                           "Snapshot build id:  netact/product/99.17.03.0.123")

    def test_client_show_lab_by_name(self, lab_name='SprintLab1234', expected_str='SprintLab1234'):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} show-labs -lab {}".format(username, lab_name),
                                           SystemExit, 0,
                                           expected_str)

    def test_client_show_labs_free(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} show-labs --filtered_by FREE".format(username),
                                           SystemExit, 0,
                                           "Snapshot build id:  netact/product/99.17.03.0.123")

    def test_client_release_lab(self, lab_name='SprintLab1234', expected_str='SprintLab1234'):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} release-lab -lab {}".format(username, lab_name),
                                           SystemExit, 0,
                                           expected_str)

    def test_client_preserve_state(self, lab_name='SprintLab1234', expected_str='SprintLab1234'):
        rand_int = str(random.randint(0, 9999999))
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} preserve-state -lab {} --set-attribute \"build.id=netact/product/99.17.03.0.{}\"".format(username, lab_name, rand_int),
                                           SystemExit, 0,
                                           expected_str)

    def test_client_request_and_release_lab(self):
        self.test_client_create_test_labs()
        self.test_client_show_labs_free()
        available_snapshot = self._get_data_from_results(
            'Snapshot build id:  ([^ ]*).*available.*')
        self._command_line_operation_check(inspect.stack()[0][3],
                                           "-u {} ".format(username) +
                                           "request-lab -q \"{\\\"build.id\\\":\\\"" + str(available_snapshot)
                                           + "\\\"}\" -m \"module test\" --wait-time 4",
                                           SystemExit, 0,
                                           "LAB: ")
        reserved_lab = self._get_data_from_results('LAB: ([^ ]*)')
        self.test_client_show_lab_by_name(reserved_lab, "RESERVED.*{}".format(reserved_lab))
        self.test_client_preserve_state(reserved_lab, ".*{}".format(reserved_lab))
        self.test_client_release_lab(reserved_lab, "Released lab:.*{}".format(reserved_lab))
        self.test_client_show_lab_by_name(reserved_lab, "FREE.*{}".format(reserved_lab))


if __name__ == '__main__':
    usage_text = """
    Usage:

          python client_functional_tests.py -h
          python client_functional_tests.py --service-url "http://10.157.67.191:8000" ClientFunctionalTests.test_client_request_and_release_lab

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--service-url', dest="service_url")
    parser.add_argument('unittest_args', nargs='*')
    if len(sys.argv) == 1:
        parser.print_help()
        print usage_text
        sys.exit(1)

    args = parser.parse_args()
    ClientFunctionalTests.SERVICE_URL = args.service_url

    sys.argv[1:] = args.unittest_args
    unittest.main()
