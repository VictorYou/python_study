'''LSS client info methods
'''
import argparse
from termcolor import colored
import logging
import requests
import time
import json
import sys
import os
import random
from .dict_builder import DictionaryBuilder
import re
from .globals import *
from .utils import _print_out, _print_out_and_log, _format_string, _formulate_admin_server_access_str, load_json_content, _gen_unit_mock
from .lab_request import _check_lab_reservation_status
from .rest_client import *
import datetime

log = logging.getLogger(__name__)


def show_labs(service_url=None, lab_name=None, **kwargs):
    """   Shows labs in lab state service
     """
    log.debug("CMD line params: [{0}:'{1}'".format("labName", lab_name))

    message = ""
    where = ""
    if lab_name:
        where = "&where={\"lab_name\":\"%s\"}" % lab_name

    query = "%s/labs?%s" % (service_url, where)
    log.debug('show_labs query: %s' % (query))
    try:
        labs_data = get_labs(query, service_url)
        log.debug('show_labs(): labs_data = %s' % (labs_data))
    except Exception as e:
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out(message, kwargs['output_file'])

    data_dict = _create_data_dict_for_printing(labs_data)
    log.debug('show_labs(): data_dict = %s' % (data_dict ))

    _print_labs(lab_name, data_dict,
                kwargs['verbose'],
                kwargs['output_file'],
                kwargs['output_format'],
                kwargs['filtered_by'])


def show_snapshots(service_url=None,snapshot_in_print=None, **kwargs):
    """    shows states in lab pool
    """
    log.debug("CMD line params: [{0}:'{1}'".format("testi", snapshot_in_print))

    message = ""
    where = ""
    query = "%s/labs?%s" % (service_url, where)
    log.debug('show_snapshots query: %s' % (query))

    try:
        labs_data = get_labs(query, service_url)
        log.debug('show_snapshots(): labs_data = %s' % (labs_data))
    except Exception as e:
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out(message, kwargs['output_file'])
    snapshot_data_dict = _create_data_for_show_snapshots(labs_data,**kwargs)
    log.debug('show_snapshots(): labs_data = %s' % (snapshot_data_dict))
    print_dict = _resolve_print_content(snapshot_data_dict ,snapshot_in_print)
    log.debug('show_snapshots(): labs_data = %s' % (print_dict))

    _print_snapshots(print_dict, **kwargs)


def show_item(href=None, service_url=None, **kwargs):
    """   Shows 'lab|state|reservation' item as JSON for given href.
       - to get 'href' values, use 'show-labs' with '-v' (verbose) option
         from output it is possible to copy 'href' value for the 'show-item' input
    """
    log.debug('show_item(href=%s, service_url=%s, kwargs=%s)' % (href, service_url, kwargs))
    if service_url is None:
        raise Exception('service_url is None')

    message = ""
    embedded_str = "&embedded={\"states\":1,\"reservation\":1,\"previously_reverted_state\":1}&pretty"
    query = "%s/%s?%s" % (service_url, href, embedded_str)
    try:
        log.info(query)
        req = requests.get(query)
        log.debug(_gen_unit_mock(query, req.json()))
        req.raise_for_status()
        message = req.text
    except Exception as e:
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out(message, kwargs['output_file'])


def show_schema(schema_item=None, service_url=None, **kwargs):
    """   Shows 'lab|state|reservation|labrequests' schema as JSON.
    """
    log.debug('kwargs: %s' % (kwargs))
    log.info("CMD line params: {0}:'{1}'".format("item", schema_item))

    exit_code = 0
    message = ""
    query = "%s/schema?pretty" % (service_url)
    try:
        log.info(query)
        req = requests.get(query)
        log.debug(_gen_unit_mock(query, req.json()))
        req.raise_for_status()
        message = resolve_schema_text(req.text, schema_item)
        log.info("message : '{}'".format(message))
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])

    return exit_code


def resolve_schema_text(text, schema_item):
    NL = "NEWLINE"
    schema_text = str(text)
    if schema_item:
        if schema_item in SCHEMA_ITEM_MAP:
            tmp_text = schema_text.replace("\n", NL)
            log.info("TEMP: '{}'".format(tmp_text))
            find_match = r"" + NL + "    \"" + schema_item + "\":.*" + SCHEMA_ITEM_MAP[schema_item] + ""
            tmp_text = re.findall(find_match, tmp_text)
            log.info("SIZE: '{}' '{}'".format(len(tmp_text), find_match))
            if len(tmp_text) > 0:
                schema_text = tmp_text[0].replace(NL, "\n")
                schema_text = "    " + schema_text
    return schema_text


def _resolve_print_content(snapshot_data_dict, snapshot_in_print, **kwargs):
    log.debug('show_snapshot() data dict: \n"' + str(snapshot_in_print) + '"')
    print_dict = {}
    if snapshot_in_print:
        if snapshot_data_dict.get(snapshot_in_print):
            print_dict = {snapshot_in_print: snapshot_data_dict[snapshot_in_print]}
        else:
            for snapshot in snapshot_data_dict.keys():
                if re.search(snapshot_in_print, snapshot):
                    print_dict[snapshot] =  snapshot_data_dict[snapshot]
        if not print_dict:
            _print_out("No such snapshot as '{}'".format(snapshot_in_print), kwargs['output_file'])

    else:
        print_dict = snapshot_data_dict
    return print_dict


def resolve_status_from_response(response):
    status_ok = False
    message = ""
    if '_status' in response:
        status = response['_status']
        if status in "OK":
            status_ok = True
        else:
            if '_error' in response:
                message = "Code: '{}' ".format(response['_error'].get('code')) + response['_error'].get('message')
    log.info("resolve_status_from_response({}): status_ok: '{}', message: '{}'".format(response, status_ok, message))
    return status_ok, message


def _create_data_for_show_snapshots(labs,**kwargs):
    snapshot_dict = {}
    for response in labs:
        for lab_data in response['_items']:
            if lab_data.get("reservation"):
                lab_status = "reserved"
            else:
                lab_status = "free"
            if lab_data.get("states"):
                for state in lab_data["states"]:
                    snapshot_data={}
                    snapshot_data["lab_status"] = lab_status
                    snapshot_data["lab_name"] = lab_data.get("lab_name")
                    snapshot_data["lab_type"] = lab_data.get("lab_type")

                    snapshot_id = state.get("build").get("id")
                    if snapshot_id not in snapshot_dict:
                        snapshot_dict[snapshot_id] = [snapshot_data]
                    else:
                        snapshot_dict[snapshot_id].append(snapshot_data)

    return snapshot_dict


def _create_data_dict_for_printing(labs):

    """
       Printed data is collected into dictionary according to output format, which enables easy print out loop

            data_dict[status][lab_type][lab]['states'][snap_status]['_id']
            data_dict[status][lab_type][lab]['states'][snap_status]['_build']
            data_dict[status][lab_type][lab]['states'][snap_status]['_created']

STATE:queued_for_initialization
=================================
        vsprint -lab
        --------------
            FREE       vSprint5673
                        Snapshot build id:  netact/product/99.17.03.0.112            queued                 Mon, 27 Mar 2017 08:07:28 GMT

           FREE       vSprint1446
                        Snapshot build id:  netact/product/99.17.03.0.112            queued                 Mon, 27 Mar 2017 12:47:03 GMT
    """

    status_lab_dict = {}

    for response in labs:
        for lab_data in response['_items']:
            lab_name = str(lab_data['lab_name'])
            log.debug('_create_data_dict_for_printing(): lab_name = %s (%s)' % (lab_name, type(lab_name)))
            _reservation_entry = dict(
                lab_status = str(lab_data['status']),
                lab_type = str(lab_data.get('lab_type')),
                _id = lab_data['_id'],
            )
            reservation = 'RESERVED' if lab_data.get('reservation') else 'FREE'
            if reservation == 'RESERVED':
                _reservation_entry.update(dict(
                    reservation_color = AsciiColors.RESERVED,
                    reservation_user = lab_data['reservation'].get('username'),
                    reservation_message = lab_data['reservation'].get('message'),
                    reservation_id = lab_data['reservation'].get('_id'),
                ))
            else:
                _reservation_entry.update(dict(
                    reservation_color = AsciiColors.FREE,
                    reservation_user = None,
                    reservation_message = None,
                    reservation_id = None,
                ))
            if reservation not in status_lab_dict:
                status_lab_dict[reservation] = {}
            status_lab_dict[reservation][lab_name] = _reservation_entry
            log.debug('_create_data_dict_for_printing(): _reservation_entry=%s' % (_reservation_entry))

            if 'states' in lab_data:
                index = 1000
                for state in lab_data['states']:
                    if 'snapshot_status' in state:
                        snap_status = str(state['snapshot_status'])
                        build_id = str(state['build']['id'])
                        if 'states' not in status_lab_dict[reservation][lab_name]:
                            status_lab_dict[reservation][lab_name]['states'] = {}
                        if snap_status not in status_lab_dict[reservation][lab_name]['states']:
                            status_lab_dict[reservation][lab_name]['states'][snap_status] = {}
                        if build_id not in status_lab_dict[reservation][lab_name]['states'][snap_status]:
                            status_lab_dict[reservation][lab_name]['states'][snap_status][index] = {}
                            status_lab_dict[reservation][lab_name]['states'][snap_status][index][build_id] = {}

                        status_lab_dict[reservation][lab_name]['states'][snap_status][index][build_id].update(dict(
                            _id = state['_id'],
                            _created = state['_created'],
                            snapshot_id = state.get('snapshot_id'),
                            admin_server_access = _formulate_admin_server_access_str(state),
                        ))
                        index += 1

    return status_lab_dict


def _formulate_show_snapshot_ascii(data_dict,**kwargs):
    if not data_dict:
        print "No labs in database"
        return

    header_row = "    {:40s}{:20s}"
    info_row = "                   {:25s}{:20s}{:10s}"
    data_string = ""
    for snapshot in data_dict:
        snap_status = colored("UNAVAILABLE","red")
        for i in range(len(data_dict[snapshot])):
            snap = data_dict[snapshot][i]
            if snap.get("lab_status") == "free":
                snap_status = colored("AVAILABLE","green")
        data_string += header_row.format(snapshot, snap_status) + "\n"
        if kwargs["labs_shown"]:
            for i in range(len(data_dict[snapshot])):
                snap = data_dict[snapshot][i]
                data_string += info_row.format(snap.get("lab_name"),snap.get("lab_status"),snap.get("lab_type")) + "\n"
            data_string += "\n"
    return data_string


def _print_snapshots(print_dict, **kwargs):
    output_format =  kwargs['output_format']
    print_target = kwargs['output_file']
    data = ""
    if output_format == 'ASCII':
        data = _formulate_show_snapshot_ascii(print_dict,**kwargs)
    elif output_format == 'JSON':
        data = json.dumps(print_dict, indent=4)
    elif output_format == 'HTML':
        data = _format_show_snapshot_html(print_dict)
    _print_out(data, print_target)



def _print_labs(lab_name, data_dict, verbose, print_target, output_format, filtered_by):
    ''' print lab data which is in JSON format in data_dict '''
    log.debug('_print_labs(lab_name=%s, data_dict=%s, verbose=%s, print_target=%s, output_format=%s, filtered_by=%s)' %
                (lab_name, data_dict, verbose, print_target, output_format, filtered_by))
    data = ""
    if output_format == 'ASCII':
        data = _formulate_ascii(data_dict, verbose, filtered_by)
    elif output_format == 'JSON':
        data = json.dumps(data_dict, indent=4)
    elif output_format == "HTML":
        labs_html_dict = _create_show_labs_html_dict(data_dict)
        data = _format_show_labs_html(labs_html_dict)
    if lab_name:
        if not data:
            data = "  ### LAB: '{}' does not exist!".format(lab_name)
    log.debug("_print_labs(): {}\n_print_labs(): --------  log ends here -------------".format(data))
    _print_out(data, print_target)


def _formulate_ascii(data_dict, verbose, filtered_by):
    data = ""
    debug_data = ""
    lab_form = "   %-25.25s %-25.25s  %-10.10s  %s       %s  %s\n"
    state_form = "\t\tSnapshot build id:  %-80.80s %-20.20s   %s  %s\n"
    dic = data_dict
    for reservation in dic:
        debug_data += "\n{}\n\t".format(reservation)
        if _match_reservation_filter(filtered_by, reservation) is False:
            continue
        data += "\n"
        for lab in dic[reservation]:
            debug_data += "{},".format(lab)
            _id = dic[reservation][lab]['_id']
            lab_status = dic[reservation][lab]['lab_status']
            lab_type = dic[reservation][lab]['lab_type']
            reservation_color = dic[reservation][lab].get('reservation_color')
            reservation_user = dic[reservation][lab].get('reservation_user')
            reservation_message = dic[reservation][lab].get('reservation_message')
            reservation_id = dic[reservation][lab].get('reservation_id')
            reservation_data = "'{}'     '{}'".format(reservation_user, reservation_message)
            if reservation_user is None and reservation_message is None:
                reservation_data = ""
            lab_id = ""
            reservate_id = ""
            if verbose:
                reservate_id = reservation_id
                lab_id = "(Lab_id: labs/{} , Reservation_id: reservations/{})".format(_id, reservate_id)
            data += "\n"
            data += lab_form % ("{}{}{}{}".
                                format(str(reservation_color), reservation, str(AsciiColors.ENDC), str(AsciiColors.BOLD)),
                                lab, lab_type, lab_status.upper(), reservation_data,
                                "{}{}".format(lab_id, str(AsciiColors.ENDC)))

            if 'states' in dic[reservation][lab]:
                for snap_status in dic[reservation][lab]['states']:
                    for index in dic[reservation][lab]['states'][snap_status]:
                        for build_id in dic[reservation][lab]['states'][snap_status][index]:
                            _id = dic[reservation][lab]['states'][snap_status][index][build_id]['_id']
                            created = dic[reservation][lab]['states'][snap_status][index][build_id]['_created']
                            snapshot_id = dic[reservation][lab]['states'][snap_status][index][build_id]['snapshot_id']
                            admin_server_access = dic[reservation][lab]['states'][snap_status][index][build_id]['admin_server_access']
                            snap_id_txt = ""
                            if verbose:
                                snap_id_txt = "(Snapshot_href: states/{} , snapshot_id: '{}', admin_server_access: {})".format(_id,
                                                                                                                       snapshot_id,
                                                                                                                       admin_server_access)
                            data += state_form % (build_id, snap_status, created, snap_id_txt)
    log.debug(debug_data)
    return data


def _match_reservation_filter(filtered_by, reservation):
    match = False
    if filtered_by is '' or filtered_by in reservation:
        match = True
    return match





def _format_show_labs_html(lab_data_json):
    time_now = "Generated: " + str(datetime.datetime.now().replace( microsecond=0))
    LAB_TABLE = '<table style="width:50%"> <tr style ="background-color: #caccd1"> <th valign="top" >Lab name</th> <th valign="top" >Snapshots</th> <th valign="top" >Reservation tatus</th> <th valign="top" >Reservation user</th><th valign="top" >Lab status</th></tr> {}</table>'
    SNAPSHOT_TABLE = '<td style="text-align:left" valign="top" >{}</td>'
    SNAPSHOT_TABLE_CELL = '<p>{}</p>'
    PAGE_INIT = '<!DOCTYPE html> <html> <head> <title>Show labs</title> <p>'+ str(time_now) +'</p><link href="style.css" rel="stylesheet"> <script src="script.js" type="text/javascript"></script> <style type="text/css"> td,th {{text-align: left;padding: 15px}} tr:nth-child(even) {{background-color: #e3e5e8;}} tr:nth-child(odd) {{background-color: #f2f4f9;}} </style> </head> <body> <div class="header"> <h2>SHOW LABS</h2> </div> <div id="body">{} </div> </body> </html>'
    ROW_IN_SNAPSHOT_TABLE = '<tr valign="top">{}</tr>'
    SINGLE_ITEM_CELL = '<td>{}</td>'

    lab_status_rows = []


    for i in range(len(lab_data_json)):

        snapshot_table = ''
        if lab_data_json[i].get("snapshots"):
            for snap in lab_data_json[i]["snapshots"]:
                snapshot_table += SNAPSHOT_TABLE_CELL.format(snap)
        else:
            snapshot_table += SNAPSHOT_TABLE_CELL.format("None")
        row_in_lab_table_data = SINGLE_ITEM_CELL.format(lab_data_json[i]["lab_name"]) + \
                                SNAPSHOT_TABLE.format(snapshot_table) + \
                                SINGLE_ITEM_CELL.format(lab_data_json[i]["reservation_status"]) + \
                                SINGLE_ITEM_CELL.format(lab_data_json[i]["reservation_user"]) + \
                                SINGLE_ITEM_CELL.format(lab_data_json[i]["lab_status"])

        lab_status_rows.append(ROW_IN_SNAPSHOT_TABLE.format(row_in_lab_table_data))


    lab_table = LAB_TABLE.format("".join(lab_status_rows))
    return PAGE_INIT.format(lab_table)


def _format_show_snapshot_html(snapshot_data_json):
    time_now = "Generated: " + str(datetime.datetime.now().replace( microsecond=0))
    SNAP_TABLE = '<table class="fixed" > <col /><col /><col width="600px" /><tr style ="background-color: #caccd1"> <th valign="top" >Snapshots</th> <th valign="top" >Status</th> <th valign="top" >Labs</th> </tr>{}</table>'
    TABLE = '<table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" />{}</table>'
    PAGE_INIT = '<!DOCTYPE html> <html> <head> <title>Show snapshots</title> <p>'+ time_now +'</p><link href="style.css" rel="stylesheet"> <script src="script.js" type="text/javascript"></script> <style type="text/css"> td, th {{text-align: left;padding: 15px}} tr:nth-child(even) {{background-color: #e3e5e8;}} tr:nth-child(odd) {{background-color: #f2f4f9;}} </style> </head> <body> <div class="header"> <h2>SHOW SNAPSHOTS</h2> </div> <div id="body">{} </div> </body> </html>'
    ROW_WITHOUT_BACKGROUND = '<tr style="background: none" valign="top">{}</tr>'
    ROW_IN_TABLE = '<tr valign="top">{}</tr>'
    SINGLE_ITEM_CELL = '<td>{}</td>'
    snapshot_table_rows = []
    for snapshot in snapshot_data_json:
        snap_status = "UNAVAILABLE"
        lab_table = ""
        for i in range(len(snapshot_data_json[snapshot])):
            snap_data = snapshot_data_json[snapshot][i]
            if snap_data.get("lab_status") == "free":
                snap_status = "AVAILABLE"

            lab_name_cell = SINGLE_ITEM_CELL.format(snap_data["lab_name"])
            lab_type_cell = SINGLE_ITEM_CELL.format(snap_data["lab_type"])
            lab_status_cell = SINGLE_ITEM_CELL.format(snap_data["lab_status"])
            lab_table += ROW_WITHOUT_BACKGROUND.format(lab_name_cell + lab_status_cell + lab_type_cell)

        row_in_snapshot_table = ROW_IN_TABLE.format(
                                                    SINGLE_ITEM_CELL.format(snapshot) +\
                                                    SINGLE_ITEM_CELL.format(snap_status) +\
                                                    SINGLE_ITEM_CELL.format(TABLE.format(lab_table))
                                                    )

        snapshot_table_rows.append(row_in_snapshot_table)
    snapshot_table = SNAP_TABLE.format("".join(snapshot_table_rows))

    return PAGE_INIT.format(snapshot_table)



def _create_show_labs_html_dict(data_json):
    print_data = []
    for lab_reservation_status in data_json:
        for lab_name in data_json[lab_reservation_status]:
            lab_name_data = data_json[lab_reservation_status]
            if lab_name_data[lab_name].get("states"):
                for snapshot_state in lab_name_data[lab_name]["states"]:
                    snapshot_state_data = lab_name_data[lab_name].get("states")
                    lab_status = lab_name_data[lab_name].get('lab_status')
                    reservation_user = lab_name_data[lab_name].get('reservation_user')
                    snapshot_id_list = []

                    for snapshot in snapshot_state_data[snapshot_state]:
                        snapshot_dict = snapshot_state_data[snapshot_state]

                        for snapshot_id in snapshot_dict[snapshot]:
                            snapshot_id_list.append(snapshot_id)

                    lab_data_json = {"lab_name": lab_name,
                                          "snapshots": snapshot_id_list,
                                          "reservation_status": lab_reservation_status,
                                          'reservation_user': reservation_user,
                                          "lab_status": lab_status}
                    print_data.append(lab_data_json)
            else:
                lab_data_json = {"lab_name": lab_name,
                                 "snapshots": None,
                                 "reservation_status": lab_reservation_status,
                                 'reservation_user': None,
                                 "lab_status": None}
                print_data.append(lab_data_json)
    return print_data
