#!/usr/bin/env python

""" Tampere OSS&CEM Datacenter API """

import operator
import datetime
import requests
import logging
log = logging.getLogger(__name__)
import socket
import time
import json
import re
import ilo

timeout_poweron = 240
timeout_poweron_vm = 120
timeout_poweroff = 240
timeout_poweroff_vm = 120
timeout_shutdown_vm = 600
timeout_deletevms = 240
timeout_deletesnapshots = 3600
timeout_lock = 20
dcapi_request_retry_count = 3
dcapi_request_retry_delay = 5
event_output_interval = 2
dcapi_url = "http://dcapi.netact.nsn-rdnet.net/rest/api/v2"

_proxyDict = {
    "http": None,
    "https": None,
    "ftp": None
}

def handle_request(reqtype, requrl, reqdata=None, reqheaders=None):
    for i in range(0, dcapi_request_retry_count):
        try:
            req = getattr(requests, reqtype)(requrl, data=reqdata, headers=reqheaders)
            break
        except requests.ConnectionError as e:
            log.error("Connection error: %s", e)
            if i + 1 == dcapi_request_retry_count:
                log.error("Request retry limit reached")
                return False
            time.sleep(dcapi_request_retry_delay)
            continue
    return req

def get_event_progress(eventid):
    req = requests.get("%s/labs/eventstatus/%d" % (dcapi_url, eventid), proxies=_proxyDict)
    eventjson = load_json_content(req.content)
    if 'status' in eventjson:
        if eventjson['status'] == 'done':
            print_event_info(eventid, eventjson)
            return 100
        if eventjson['status'] == 'failed':
            print_event_info(eventid, eventjson)
            return -1
    if 'progress' in eventjson:
        if type(eventjson['progress']) is unicode and eventjson['progress'].isdigit():
            print_event_info(eventid, eventjson)
            return int(eventjson['progress'])
    log.error("Error: Unknown event state")
    print_event_info(eventid, eventjson)
    return -1

def print_event_info(eventid, event):
    if 'errormsg' in event:
        log.error("API Error while getting event %d: %s", eventid, event['errormsg'])
    if 'eventID' in event and 'message' in event and 'progress' in event and 'status' in event and 'starttime' in event:
        if 'completetime' in event and event['completetime'].isdigit() and int(event['completetime']) > 0:
            if event['status'] == 'failed':
                log.error("%s: %s - %s%%: %s - %s in %d seconds", event['eventID'], event['message'], event['progress'], event['status'], datetime.datetime.fromtimestamp(int(event['completetime'])), int(event['completetime'])-int(event['starttime']))
            else:
                log.info("%s: %s - %s%%: %s - %s in %d seconds", event['eventID'], event['message'], event['progress'], event['status'], datetime.datetime.fromtimestamp(int(event['completetime'])), int(event['completetime'])-int(event['starttime']))
        else:
            log.info("%s: %s - %s%%: %s - %d seconds since %s", event['eventID'], event['message'], event['progress'], event['status'], time.time()-int(event['starttime']), datetime.datetime.fromtimestamp(int(event['starttime'])))

def print_errormsg(source, apijson):
    if 'errormsg' in apijson:
        log.error("API Error (%s): %s", source, apijson['errormsg'])
        return 1
    else:
        return 0

def wait_event(eventid, timeoutsecs):
    stime = time.time()
    while (time.time() - stime) < timeoutsecs:
        progress = get_event_progress(eventid)
        if progress < 0 or progress == 100:
            return progress
        time.sleep(event_output_interval)
    log.error("Event %d reached %d second timeout", eventid, timeoutsecs)
    return -1

def wait_events(eventlist, timeoutsecs):
    stime = time.time()
    if len(eventlist) == 0:
        return -1
    completed_events = []
    while True:
        done = 0
        for event in eventlist:
            if event in completed_events:
                done += 1
            else:
                progress = get_event_progress(event)
                if progress < 0 or progress == 100:
                    completed_events.append(event)
                    done += 1
        if done == len(eventlist):
            break
        if (time.time() - stime) > timeoutsecs:
            log.error("Events reached %d second timeout", timeoutsecs)
            return -1
        log.info("Events completed: %d/%d", done, len(eventlist))
        time.sleep(10)
    return len(eventlist)

def get_eventid(content):
    cjson = load_json_content(content)
    if 'eventID' in cjson:
        return int(cjson['eventID'])
    if print_errormsg('get_eventid', cjson) == 1:
        return -1
    log.error("Error: no eventID or errormsg in content: %s", content)
    return -1

def get_event(eventid):
    req = requests.get("%s/labs/eventstatus/%d" % (dcapi_url, eventid), proxies=_proxyDict)
    eventjson = load_json_content(req.content)
    if 'eventID' in eventjson:
        return eventjson
    return -1

def get_event_info(eventid):
    req = requests.get("%s/labs/eventstatus/%d" % (dcapi_url, eventid), proxies=_proxyDict)
    eventjson = load_json_content(req.content)
    if 'info' in eventjson:
        return eventjson['info']
    return -1

def get_lab_auth(lab):
    '''Retrieve authentication data from DCAPI

    :param lab  ID of lab for which authentication data is requested
    '''
    req = requests.get("%s/labs/getdata/%s/JSON" % (dcapi_url, lab), proxies=_proxyDict)
    labjson = load_json_content(req.content)
    log.debug("labjson: ***%s***" % (labjson))
    vcenter = labjson.get('vcenter')
    log.info("vcenter : {}".format(vcenter))
    if vcenter == 'vcenter.nsle.nsn-rdnet.net':
        user = 'nle\\vcbuser'
        password = 'vJexABF8'
        log.debug("u:{} p:{}".format(user, password))
        return { 'user': user, 'password': password }
    elif 'serviceaccount' in labjson and 'serviceaccountpassword' in labjson:
        return { 'user':labjson['serviceaccount'], 'password': labjson['serviceaccountpassword'] }
    else:
        errormsg = labjson.get('errormsg')
        if errormsg.startswith('Failed to find lab with name') and ilo.SPRINTLABS.get(lab) is not None:
            log.debug('ilo.SPRINTLABS.get(lab): ***%s***' % (ilo.SPRINTLABS.get(lab)))
            return ilo.SPRINTLABS.get(lab).get('dcstorage_auth')

    if print_errormsg('get_lab_auth', labjson) == 1:
        return -1
    return -1

def get_lab_clusterid(lab):
    '''Retrieve cluster ID of lab from DCAPI

    :param lab  ID of lab for which authentication data is requested
    '''
    req = requests.get("%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    labjson = load_json_content(req.content)
    if 'clusterID' in labjson:
        if type(labjson['clusterID']) is unicode:
            return int(labjson['clusterID'])
        else:
            log.error("Error: invalid clusterID for lab \"%s\"", lab)
    else:
        log.error("Error: clusterID for lab \"%s\" missing", lab)
    return -1

def get_lab_config_type(lab):
    req = requests.get("%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    labjson = load_json_content(req.content)
    if 'config' in labjson:
        if type(labjson['config']) is unicode:
            return labjson['config']
        else:
            log.error("Error: invalid config for lab \"%s\"", lab)
    else:
        log.error("Error: config for lab \"%s\" missing", lab)
    return -1

def get_lab_viis_node(lab):
    req = requests.get("%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    labjson = load_json_content(req.content)
    viis_node = None
    if 'errormsg' not in labjson:
        for node in labjson['nodes']:
            if node["role"] == "ViiS":
                viis_node = node.get('name')
                return viis_node
    else:
        log.warning("Error: get_lab_viis_node({}): '{}'".format(lab, labjson))
    return -1

def api_lab_action(reqtype, lab, action, timeout):
    '''Execute request in DCAPI

    :param reqtype  type of HTTP request such as GET, POST, etc.
    :param lab  ID of lab for which authentication data is requested
    :param action   tag of action, will be part of final REST URL
    :param timeout  timeout in seconds for DCAPI action
    '''
    log.info("Target: %s - %s Action: %s", lab, reqtype.upper(), action)
    authtarget = re.sub(r'node.*', '', lab.split('/')[0])
    lab = _special_handling_for_handling_single_node(lab)
    log.info('lab: %s authtarget: %s' % (lab, authtarget))
    auth = get_lab_auth(authtarget)
    if type(auth) is int:
        return -1
    reqheaders = {}
    reqheaders['Authorization'] = "%s:%s" % (auth['user'], auth['password'])
    log.info('Authorization: %s/%s' % (auth['user'], auth['password']))

    if reqtype not in ["get", "put", "post", "delete"]:
        log.error("Error: invalid request type \"%s\"", reqtype)
        return -1

    req = handle_request(reqtype, "%s/labs/%s/%s" % (dcapi_url, action, lab), reqdata=None, reqheaders=reqheaders)
    if type(req) is bool:
        return -1
    if reqtype == "get":
        return req.content

    eventid = get_eventid(req.content)
    if eventid == -1:
        return -1
    if timeout == -1:
        return eventid
    ret = wait_event(eventid, timeout)
    return ret

def _special_handling_for_handling_single_node(lab):
    return lab if re.match(r'.*node\d+$', lab) is None else lab.upper()

def revert_lab_snapshot(lab):
    return api_lab_action('put', lab, "snapshot", timeout_deletesnapshots)

def power_on_lab(lab):
    if _power_onoff_sprintlab(lab, True) is not None:
        return True
    return api_lab_action('put', lab, "poweron", timeout_poweron)

def power_on_vm(labvm):
    return api_lab_action('put', labvm, "poweron/vm", timeout_poweron_vm)

def power_off_lab(lab):
    if _power_onoff_sprintlab(lab, False) is not None:
        return True
    return api_lab_action('put', lab, "poweroff", timeout_poweroff)

def _power_onoff_sprintlab(lab, power_on=True):
    ''' start/shut down the ILO servers if lab is sprintlab '''
    sprintlab = ilo.SPRINTLABS.get(lab)
    log.debug("Sprintlab entry? %s" % (sprintlab))
    if sprintlab is not None:
        ilo.power_lab_ilos_onoff(sprintlab['ESXis'], power_on)
        return True

def power_off_vm(labvm):
    return api_lab_action('put', labvm, "poweroff/vm", timeout_poweroff_vm)

def shutdown_vm(labvm):
    return api_lab_action('put', labvm, "shutdown/vm", timeout_shutdown_vm)

def start_shutdown_vm(labvm):
    return api_lab_action('put', labvm, "shutdown/vm", -1)

def is_lab_locked(lab):
    req = handle_request("get", "%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    if type(req) is bool:
        return -1
    labjson = load_json_content(req.content)
    if 'blocked' in labjson:
        if type(labjson['blocked']) is unicode:
            return int(labjson['blocked'])
        else:
            log.error("Error: invalid block for lab \"%s\"", lab)
    else:
        log.error("Error: block for lab \"%s\" missing", lab)
    return -1

def lock_lab(lab):
    lock = is_lab_locked(lab)
    if lock != 0:
        return -1
    return api_lab_action('put', lab, "apilock", timeout_lock)

def unlock_lab(lab):
    lock = is_lab_locked(lab)
    if lock != 1:
        return -1
    return api_lab_action('put', lab, "apiunlock", timeout_lock)

def get_lab_powerstate(lab):
    reply = api_lab_action('get', lab, "powerstate", -1)
    if type(reply) is not str:
        return -1
    labjson = load_json_content(reply)
    if print_errormsg('get_lab_powerstate', labjson) == 1:
        return -1
    statelist = {}
    on_count = 0
    off_count = 0
    for node in labjson:
        if node['powerState'] == 'poweredOn':
            statelist[node['name']] = 1
            on_count += 1
        else:
            statelist[node['name']] = 0
            off_count += 1
    statelist['on'] = on_count
    statelist['off'] = off_count
    statelist['total'] = on_count + off_count
    return statelist

def delete_lab_snapshots(lab):
    log.info("Deleting lab \"%s\" snapshots", lab)
    return api_lab_action('delete', lab, "snapshot", timeout_deletesnapshots)

def load_json_content(content):
    try:
        result = json.loads(content)
    except:
        result = json.loads('{"errormsg": "%s"}' % content.strip())
    return result

def get_lab_info(lab):
    req = handle_request("get", "%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    if type(req) is bool:
        return
    labjson = load_json_content(req.content)
    return labjson

def show_lab_info(lab):
    req = handle_request("get", "%s/labs/getdata/%s/JSON" % (dcapi_url, lab))
    if type(req) is bool:
        return
    labjson = load_json_content(req.content)
    print json.dumps(labjson, sort_keys=True, indent=4, separators=(',', ': '))

def show_event(eventid):
    req = handle_request("get", "%s/labs/eventstatus/%d" % (dcapi_url, eventid))
    if type(req) is bool:
        return
    eventjson = load_json_content(req.content)
    print json.dumps(eventjson, sort_keys=True, indent=4, separators=(',', ': '))

def start_node_shutdown(lab, nodelist):
    eventlist = []
    for node in nodelist:
        labnode = "%snode%s" % (lab.lower(), node)
        eventid = start_shutdown_vm(labnode)
        if eventid != -1:
            eventlist.append(eventid)
        else:
            log.error("Error: starting shutdown of %s failed", labnode)
    return eventlist

def set_event_output_interval(interval):
    global event_output_interval
    event_output_interval = interval
