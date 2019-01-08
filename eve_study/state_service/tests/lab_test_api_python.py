import os
import requests
import subprocess
import re
import random
import sys
import io

SPECIAL_ERROR_MESSAGE_REGX = {
    "variable not found": "(.* )*Variable (.* )*not found(.*)*",
    "exit code 0": "(.*)'0'",
    "state fail": "(.* )*'state_operation_failed' (.* )*'1'(\\n)?",

}

DELETE_PROXY_LIST = ["http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"]


def delete_os_env(value):
    try:
        del os.environ[value]
    except KeyError:
        pass


for proxy in DELETE_PROXY_LIST:
    delete_os_env(proxy)


class NOKError(Exception):
    """
    Error class for out putting intended NOK case errors
    """
    pass


class StateOperationFail(Exception):
    """
    Error class for raise state operation fail / random errors
    """
    pass


def _check_exit_code_matches(line, exit_code):
    
    try:
        if "ERROR:" in line or "ERROR" in line:
            if exit_code == 0:
                raise Exception("ERROR: error occured but return code is 0.")

        if "ERROR:" not in line and "ERROR" not in line and exit_code > 0:
            raise Exception("ERROR: No error seem to have occurred but exit code != 0")

    except ValueError:
        return
    except IndexError:
        return



def get_exit_code(message):
    pattern = ".*(?P<exit_code>[0-9])'?(\n)$"
    match = re.match(pattern,message)
    return match.group("exit_code")


def _database_data_puller(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def _keyword_finder(command_list, key):
    for i in range(len(command_list)):
        if  key == command_list[i]:
            return command_list[i + 1]
    return ""


def _command_executer(commands, wanted_return="", return_exit_code=False):
    # works on python 3.5. If universal_newlines = False, it works with 2.7

    p1 = subprocess.Popen(commands, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                          universal_newlines=True, stderr=subprocess.PIPE)
    all_lines, last_line = parse_subprosess_output(p1)
    exit_code = (p1.communicate()[0],p1.returncode)[1]
    print(exit_code)
    #_check_exit_code_matches(all_lines, exit_code)
    return_value = parse_wanted_returns(wanted_return, all_lines, last_line, exit_code, return_exit_code)
    return return_value


def parse_subprosess_output(p1):
    """
    Parses output created by subprocess class and returns output values
    :param p1: subprocess class
    :return: parsed output values
    """
    last_line = ""
    all_lines = []
    while True:
        line = p1.stdout.readline()
        if line == "":
            break
        if line != "\n":
            last_line = line
        slots = line.strip().split(" ")
        all_lines += slots

        print(line.strip("\n"))
    print("")
    return all_lines, last_line


def parse_wanted_returns(wanted_return, all_lines, last_line, exit_code, return_exit_code):
    """
    :param wanted_return: What user wants to return
    :param all_lines: All lines form subprocess output
    :param last_line: Last line from subprocess output
    :param exit_code: Exitcode of subprocess 
    :param return_exit_code: Boolean value about return or not to return exit code
    :return: 
    """
    return_value = ""
    if wanted_return == "all":
        while True:
            if "" in all_lines:
                all_lines.remove("")
            else:
                break
        return_value = all_lines

    elif wanted_return == "last":
        return_value = last_line

    if return_exit_code:
        return return_value, exit_code
    else:
        return return_value



def run_lab_reservation_from_container(query, url ,nok_case="no_nok_case"):
    """
    runs lab request command with given container name, query and url. Raises exception
    if reservation fails
    :return: Labname
    """
    args = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'request-lab', "-wait", "5", '--message', '"test"', '-q',
            query]
    if url != "":
        args[10] = url

    line = _command_executer(args, wanted_return="last")
    try:
        line = line.replace("  ", " ").split(" ")
        if "'state_operation_failed'" in line:
            raise StateOperationFail(
                "ERROR in 'request-lab' operation, reverting snapshot failed "
                "'state_operation_failed'. Exit code: '1'")
        elif nok_case in line:
            raise NOKError()
        elif "ERROR" in line:
            raise Exception("ERROR: " + " ".join(line[3:]))
        else:
            return line[1]
    except IndexError:
        raise Exception("ERROR: check container name. Exit code: '1'")


def test_if_lab_is_reserved_with_given_labname(lab_name, url, user="test-user"):
    """
    Checks that does the reserved lab have reserved status in database.

    :return: True if lab is reserved, False if not
    """
    lab_url = url + "/labs?pretty&where={\"lab_name\":\"" + lab_name + "\"}"
    try:
        lab_data = _database_data_puller(lab_url)
        print(lab_data)
        reservation_id = lab_data["_items"][0].get("reservation")
    except IndexError:
        return False
    if reservation_id is None:
        return False

    reservation_url = "{0}/reservations/{1}".format(url, reservation_id)
    reservation_data = _database_data_puller(reservation_url)
    if reservation_data["_id"] == reservation_id and user == reservation_data["username"]:
        return True, reservation_id
    return False


def release_lab(lab_name,  url="", nok_case="no_nok_case"):
    """
    Runs lab release command for reserved lab. If release is OK, returns nothing.
    If release is NOK raises exception
    :param lab_name: 
    :param  
    :param url: 
    :param nok_case: to get intended nok case error message
    :return: 
    """
    if lab_name == "<none>" or lab_name == "":
        raise Exception("Lab name empty")

    args = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'release-lab', '--lab-name', lab_name]
    if url != "":
        args[10] = url

    try:
        result = _command_executer(args, wanted_return="last").strip(" ")
        slots = result.split(" ")
        if slots[1] == "ERROR:":
            if "exist!" in slots:
                raise Exception("ERROR: Lab " + " ".join(slots[2:]))
            if nok_case == "release unreserved" and "not" in slots and "reserved!" in slots:
                raise NOKError()
            raise Exception("ERROR: " + " ".join(slots[2:]))
        return
    except IndexError:
        raise Exception("ERROR: Invalid container name '" +  "'. Exit code: '1'")


def create_test_data():
    """
    Runs create test labs command. Used for test suite setup
    :param  
    """
    _command_executer(
        ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'create-test-labs']
    )


def find_lab_query():
    """
    Finds all labs that are available for reservation and returns random lab query.
    Raises exception if no free lab s found. Used for test suite setup.
    :param  
    :return: random query from list of available queries
    """
    queries = []
    args = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'show-labs']
    data = _command_executer(args, wanted_return="all")
    print(data)

    for i in range(len(data)):
        result = re.match(".*FREE.*", data[i])
        if result and data[i + 3] == "READY" and data[i + 9] == "available":
            query_id = data[i + 8]
            queries.append(query_id)
    print(queries)

    try:
        return "{\"build.id\":\"" + str(queries[random.randint(0, len(queries) - 1)]) + "\"}"
    except ValueError:
        raise Exception("ERROR: No queries found")


def clear_test_data(web):
    """
    Clears database from all data. Used for test suite tear down.
    :param web: 
    :return: 
    """
    command_list = [['curl', '-X', 'delete', '-ig', web + ' /labs'],
                    ['curl', '-X', 'delete', '-ig', web + '/states'],
                    ['curl', '-X', 'delete', '-ig', web + '/reservations'],
                    ['curl', '-X', 'delete', '-ig', web + '/labrequests']]
    for commands in command_list:
        _command_executer(commands)


def preserve_lab_state(lab_name):
    """
    Runs preserve-state command and adds new information for the new state
    :return: 
    """
    args = [
        'python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'preserve-state',
        '-lab', lab_name, '-s', '\"build.id=\"test/123\"\"', '-a',
        '\"build_history=\"test_snapshot\"\"'
    ]
    try:
        message = _command_executer(args, wanted_return="last")
        print(message)
        return message
    except:
        raise Exception("ERROR: State reservation failed. Exit code: '1'")


def find_state_information_from_database(lab_name, web):
    """
    Checks is information given with preserve lab state command
    in database. Raises errors if data is not in database.


    :return: 
    """
    url = web + "/labs?where={\"lab_name\":\"" + lab_name + "\"}"
    lab_id = _database_data_puller(url)["_items"][0]["_id"]
    state_url = web + "/labs/" + lab_id + "?embedded={\"states\":1}"
    states = _database_data_puller(state_url)["states"]
    print(states)
    build_history_found = False
    state_id_found = False

    for state in states:
        if state["build"]["id"] == "test/123":
            state_id_found = True
        if "build_history" in state:
            if "test_snapshot" in state["build_history"]:
                build_history_found = True

    if not state_id_found:
        raise Exception("ERROR: Changed state ID not found. Exit code: '1'")
    if not build_history_found:
        raise Exception("ERROR: Appended state history information not found. Exit code: '1'")


def find_lab_name():
    """
    Finds all labs that are available for reservation and returns random lab name.
    Raises exception if no free lab is found.
    :param  
    :return: random lab name from list of available queries
    """
    labs = []
    args = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', 'show-labs']
    data = _command_executer(args, wanted_return="all")
    for i in range(len(data)):
        result = re.match(".*FREE.*", data[i])
        if result and data[i + 3] == "READY" and data[i + 9] == "available":
            lab_name = data[i + 1]
            labs.append(lab_name)
    print(data)
    print(labs)
    try:
        return str(labs[random.randint(0, len(labs) - 1)])
    except ValueError:
        raise Exception("ERROR: lab names not found. Exit code: '1'")


def release_lab_with_wrong_username(lab_name,  url=""):
    """
    Runs lab release command for reserved lab but with false username. If release is OK, returns nothing.
    If release is NOK raises an exception. Used for NOK test case.
    :param lab_name: 
    :param  
    :param url: 
    :return: 
    """
    if lab_name == "<none>" or lab_name == "":
        raise Exception("Lab name empty")

    args = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "wrong_username", '-url', 'http://localhost:8000', 'release-lab', '--lab-name', lab_name]
    if url != "":
        args[11] = url

    try:
        result = _command_executer(args, wanted_return="last").strip(" ")
        slots = result.split(" ")
        if "'test-user'!" in slots:
            raise NOKError
        if slots[1] == "ERROR:":
            if "exist!" in slots:
                raise Exception("ERROR: Lab " + " ".join(slots[2:]))
            raise Exception("ERROR: " + " ".join(slots[2:]))
        return
    except IndexError:
        raise Exception("ERROR: Invalid container name '" +  "'. Exit code: '1'")


def user_reserves_lab_py(query, url):
    """
    Python keyword for lab reservation E2E test

    """
    lab_name = run_lab_reservation_from_container(query, url)
    if lab_name == "<none>":
        raise Exception("ERROR: Intented lab was not free to reserve. Exit code: '1'")
    return lab_name


def lab_should_be_reserved_py(web_url, lab_name):
    """
    Python keyword to check lab reservation from databes in E2E test

    """
    if not test_if_lab_is_reserved_with_given_labname(lab_name, web_url):
        raise Exception("ERROR: Lab '" + lab_name + "' not found in reservation database. Exit code: '1'")


def lab_is_not_reserved_py(lab_name, url):
    """
    Python keyword to check lab release from database in E2E test

    """

    if test_if_lab_is_reserved_with_given_labname(lab_name, url):
        raise Exception("ERROR: Lab release failed for '" + lab_name + "'. Exit code: '1'")


def user_reserves_lab_whit_wrong_query_and_fails_py(url):
    """
    Python keyword for reserve lab with wrong query NOK case

    """

    try:
        message = run_lab_reservation_from_container("Wrong_Query", url, nok_case="'Wrong_Query'")
        print(message)
        if len(message.split(" ")) == 1:
            raise Exception("ERROR: Lab reservation succeed with wrong query, lab name: "
                            + message + " . Exit code: '1'")
        else:
            raise Exception(message)
    except NOKError:
        return


def user_reserves_reserved_lab_and_fails_py(web):
    """
    Python keyword for reserve already reserved lab NOK case

    """

    query = find_lab_query()
    run_lab_reservation_from_container(query, web)
    try:
        message = run_lab_reservation_from_container(query, web, nok_case="'no_lab_available'")
        if len(message.split(" ")) == 1:
            raise Exception("ERROR: Lab reservation succeed to lab already reserved, lab name: "
                            + message + ". Exit code: '1'")
        else:
            raise Exception(message)
    except NOKError:
        return


def user_releases_lab_reserved_for_another_user_and_fails(web):
    """
    Python keyword for release lab reserved for another user NOK case

    """
    query = find_lab_query()
    lab_name = run_lab_reservation_from_container(query, web)
    try:
        release_lab_with_wrong_username(lab_name,  web)
        raise Exception("ERROR: Lab release succeed with wrong username. Exit code: '1'")
    except NOKError:
        return


def user_releases_unreserved_lab_and_fails_py(url):
    """
    Python keyword for release unreserved lab NOK case

    """
    lab_name = find_lab_name()
    print(lab_name)
    try:
        release_lab(lab_name, url, nok_case="release unreserved")
        raise Exception("ERROR: Lab release succeed to unreserved lab. Exit code: '1'")
    except NOKError:
        return


def user_preserves_state_of_unreserved_lab_and_fails_py():
    """
    Python keyword for preserve state un unreserved lab NOK case    

    """

    lab_name = find_lab_name()
    message = preserve_lab_state(lab_name)
    exit_code = get_exit_code(message)
    if  exit_code == str(1) and "not currently reserved" in message:
        return
    else:
        raise Exception("ERROR: Snapshot taken from unreserved lab. Exit code: '1'")


def admin_creates_lab_py(labname="sprintlabtest1232"):
    commands = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "admin", '-url', 'http://localhost:8000', "admin-add-lab", "-lab", labname]
    return _command_executer(commands, wanted_return="all", return_exit_code= True)


def lab_should_be_in_database(url, lab_name="sprintlabtest1232"):
    lab_url = url + "/labs?pretty&where={\"lab_name\":\"" + lab_name + "\"}"
    lab_data =_database_data_puller(lab_url)
    try:
        found_lab_name_from_database = lab_data["_items"][0]["lab_name"]
    except IndexError:
        raise NOKError("ERROR: Lab " + lab_name + " not found in database, /labs?pretty&where={\"lab_name\":\"" + lab_name + "\"} failed to connect . Exit code: '1'")

    if found_lab_name_from_database == lab_name:
        return
    else:
        raise NOKError("ERROR: Lab " + lab_name + " not found in database, labname was not found in database. Exit code: '1'")


def admin_adds_lab_that_already_exists_and_fails_py():
    existing_lab = find_lab_name()
    print("found existing labb '" + existing_lab + "'")
    output, exitcode = admin_creates_lab_py(existing_lab)

    if "added into Lab State" in " ".join(output) and exitcode == 0:
        raise NOKError("ERROR: Existing lab added to Lab State Service. Exit code: '1'")
    else:
        return


def admin_removes_lab_py(lab_name="sprintlabtest1232"):
    commands = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "admin", '-url', 'http://localhost:8000', "admin-remove-labs", "-lab", lab_name, "-f"]
    _command_executer(commands)


def lab_should_not_be_in_database_py(web, lab_name="sprintlabtest1232"):
    try:
        lab_should_be_in_database(web, lab_name)
    except NOKError:
        print("Lab not found in database")
    else:
        raise Exception("ERROR: Lab found in database after it was deleted. Exit code '0'")


def user_removes_lab_and_fails_py():
    lab_name = find_lab_name()
    commands = ['python2', '../src/client.py', '-l', 'INFO', '--username',
            "test-user", '-url', 'http://localhost:8000', "admin-remove-labs", "-lab", lab_name, "-f"]
    output, exit_code = _command_executer(commands, return_exit_code=True)
    if "#ERROR: User" not in output and "not allowed" not in output and exit_code == 1:
        pass
    elif exit_code == 0:
        raise Exception("### ERROR: User was able to remove lab from LSS")
    else:
        raise Exception("### ERROR: Not intended error occured: \n  " + output)




if __name__ == "__main__":
    create_test_data()




