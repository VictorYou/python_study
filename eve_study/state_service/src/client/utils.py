'''misc utils for LSS client
'''
import re
import json
import datetime
from string import Template
import logging as log
from .globals import *

def count_seconds(in_string):
    ''' counting seconds from input given as value + time unit
        such as minute, hour or seconds 
        value string can contain sign + or -

        :param in_string    value in form <numeric><unit>

    '''
    log.debug('count_seconds(in_string=%s)', in_string)
    if type(in_string) != str:
        return in_string
    _m = re.match(r'^\s*([+-]?)\s*([\d.]+)\s*(|s|sec|seconds?|m|min|minutes?|h|hours?)\s*$', in_string)
    if _m is not None:
        (sign, value, unit) = _m.groups()
        log.debug('count_seconds: sign=%s value=%s unit=%s', sign, value, unit)
        sign = -1 if sign == '-' else 1
        multi = 1
        for multi, entries in (
            (1, 's sec second seconds'),
            (60, 'm min minute minutes'),
            (3600, 'h hour hours'),
        ):
            if unit in entries.split():
                return int(multi * float(value) * sign)
        return int(value) * sign

def create_tag_string(template, variables={}, timestamp=datetime.datetime.utcnow()):
    '''create and return tag string that may contain date and/or time fields, or fields from provided dict

    param: template     template string e.g. '${username}-%Y.%m.%d'
    param: variables    dict containing variable definitions
    param: timestamp    timestamp of type datetime.datetime
    '''
    log.debug('create_tag_string(template=%s, variables=%s, timestamp=%s)', template, variables, timestamp)
    template = datetime.datetime.strftime(timestamp, template)
    return Template(template).substitute(variables)

def _print_out_and_log(exit_code, data, print_target, print_exit_code=True):
    message = data
    if print_exit_code:
        message = data + " Exit code: '{}'".format(exit_code)
    if exit_code is 0:
        log.info(message)
    else:
        log.error(message)
    log.info("_print_out_and_log(): --------  log ends here -------------")
    _print_out(message, print_target)


def _print_out(data, print_target):
    if print_target == 'STDOUT':
        print data
    else:
        with open(print_target, 'w') as f:
            f.write(data + "\n".format())

def _format_string(string, col, bold=False, underline=False):
    ERROR_STATUSES = ['ERROR', 'ERR', 'FAIL', 'FAILED']
    formatted_str = ""
    bold_char = ""
    underline_char = ""
    if 'OK' in col:
        col = AsciiColors.OKBLACK
    elif col in ERROR_STATUSES:
        col = AsciiColors.FAIL
    if bold:
        bold_char = str(AsciiColors.BOLD)
    if underline:
        underline_char = str(AsciiColors.UNDERLINE)
    formatted_str = bold_char + underline_char + str(col) + string + str(AsciiColors.ENDC)
    return formatted_str

def _formulate_admin_server_access_str(state, output_format="ASCII", build_id=None, lab_name=None):
    data_string = ""
    header_string = ""
    json_data_dict = {}
    newline = ""

    if build_id:
        data_string += "{}: '{}', ".format(BUILD_ID_KEY, build_id)
        json_data_dict[BUILD_ID_KEY] = build_id

    if ADMIN_SERVER_ACESS_KEY in state:
        for key, value in sorted(state[ADMIN_SERVER_ACESS_KEY].iteritems()):
            data_string += "{}: '{}', ".format(key, value)

    if output_format in "ASCII":
        data_string = re.sub(r', $', '', data_string)
        data_string = "[{}]".format(data_string) + newline
    elif output_format in "JSON":
        if state:
            if state.get(ADMIN_SERVER_ACESS_KEY):
                json_data_dict.update(state.get(ADMIN_SERVER_ACESS_KEY))
        data_string = json.dumps(json_data_dict) + newline
    elif output_format in "CSV":
        header_string, data_string = _resolve_csv_data(lab_name, build_id, state)
    return (data_string, header_string)

def _resolve_csv_data(lab_name, build_id, state):
    header_str = ""
    data_str = ""
    keys = [LAB_NAME_KEY, BUILD_ID_KEY, "host", "password", "port", "protocol", "username"]

    for k in keys:
        header_str += "{},".format(k)

        if k in LAB_NAME_KEY:
            data_str += "{},".format(lab_name)
        elif k in BUILD_ID_KEY:
            data_str += "{},".format(build_id)
        else:
            if ADMIN_SERVER_ACESS_KEY in state:
                value = state[ADMIN_SERVER_ACESS_KEY].get(k)
                data_str += "{},".format(value)
            else:
                data_str += ","

    header_str = re.sub(r',$', '', header_str)

    data_str = re.sub(r',None', ',', data_str)
    data_str = re.sub(r',$', '', data_str)
    data_str = re.sub(r',\n', '\n', data_str)

    return (header_str, data_str)

def load_json_content(content):
    try:
        result = json.loads(content)
    except:
        result = json.loads('{"errormsg": "%s"}' % content.strip())
    return result

def _gen_unit_mock(query, data):
    mock_format = """
    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*%s.*')
    def mock_api_(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps(%s)
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }
    """
    mock_code = mock_format % (query, data)
    return mock_code

