'''module for parsing LSS client command line
'''
import sys
import os
import logging
import argparse
from .globals import *
from .lab_request import request_lab, release_lab, preserve_state, change_lab_reservation
from .testing_support import create_test_labs, create_test_snapshots
from .admin import admin_patch_item, admin_migrate_snapshots,admin_remove_snapshots, admin_add_lab,admin_remove_labs,admin_reserve_labs,admin_data_backup,admin_data_restore,show_admin_server_access_data
from .config_change import get_server_config_entry, set_server_config_entry, remove_server_config_entry
from .info import show_labs, show_item, show_schema, show_snapshots

''' default value for url of Lab State Service REST API '''
LAB_STATE_SERVICE_URL = "http://localhost:8000"

log = logging.getLogger(__name__)

def parse_command_line(argv=None):
    '''parsing command line for dispatching actions of LSS client '''
    my_username = os.getenv('USER')
    my_binary_name = sys.argv[0]
    admin_username = "admin"

    parser, subparsers = parse_common_params()
    _add_request_lab_parser(subparsers, my_binary_name, my_username, request_lab)
    _add_release_lab_parser(subparsers, my_binary_name, my_username, release_lab)
    _add_change_lab_reservation_parser(subparsers, my_binary_name, my_username, change_lab_reservation)
    _add_preserve_state_parser(subparsers, my_binary_name, my_username, preserve_state, check_wait_time)
    _add_show_labs_parser(subparsers, my_binary_name, my_username, show_labs)
    _add_show_snapshot_parser(subparsers, my_binary_name, my_username, show_snapshots)

    _add_show_item_parser(subparsers, my_binary_name, my_username, show_item)
    _add_show_schema_parser(subparsers, my_binary_name, my_username, show_schema)

    _add_config_change_parser(subparsers, my_binary_name, my_username, get_server_config_entry, set_server_config_entry, remove_server_config_entry)

    _add_admin_patch_item_parser(subparsers, my_binary_name, my_username, admin_username, admin_patch_item)
    _add_admin_migrate_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, admin_migrate_snapshots)
    _add_admin_remove_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, admin_remove_snapshots)
    _add_admin_add_lab_parser(subparsers, my_binary_name, my_username, admin_username, admin_add_lab)
    _add_admin_remove_labs_parser(subparsers, my_binary_name, my_username, admin_username, admin_remove_labs)
    _add_admin_reserve_labs_parser(subparsers, my_binary_name, my_username, admin_username, admin_reserve_labs)
    _add_admin_data_backup_parser(subparsers, my_binary_name, my_username, admin_username, admin_data_backup)
    _add_admin_data_restore_parser(subparsers, my_binary_name, my_username, admin_username, admin_data_restore)
    _add_show_admin_server_access_data(subparsers, my_binary_name, my_username, admin_username, show_admin_server_access_data)

    _add_create_test_labs_parser(subparsers, my_binary_name, my_username, create_test_labs)
    _add_create_test_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, create_test_snapshots)

    return parser.parse_args(argv)

def parse_common_params():
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--username",
                        dest="username",
                        required=True)

    parser.add_argument("-f", "--output-file",
                        dest="output_file",
                        default='STDOUT')

    parser.add_argument("-o", "--output-format",
                        dest="output_format",
                        choices=['JSON', 'CSV', 'ASCII', 'HTML'],
                        default='ASCII')

    parser.add_argument("-l", "--log-level",
                        dest="loglevel",
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
                        default='INFO')

    parser.add_argument('-url', '--service-url',
                        dest="service_url",
                        default=LAB_STATE_SERVICE_URL,
                        required=False)

    parser.add_argument('-dca-url', '--dcapi-service-url',
                        dest="dcapi_service_url",
                        default=STORAGE_API_URL,
                        required=False)

    parser.add_argument('-v', '--verbose',
                        dest="verbose",
                        action='store_true',
                        default=False,
                        required=False)

    parser.add_argument('-lf', '--log-file',
                        dest="log_file",
                        default=None,
                        required=False)

    return parser, parser.add_subparsers()

def _add_request_lab_parser(subparsers, my_binary_name, my_username, request_lab_func):
    request_lab_help_txt = """
    e.g.
          python %s -u %s request-lab -q "{\\"build.id\\":\\"netact/product/99.17.03.0.303\\"}" -m "NA17_2 to NA17_5 upgrade test" --wait-time 10
          python %s -u %s request-lab -q "{\\"build.id\\":\\"netact/product/99.17.03.0.445\\"}" -m "NA17_2SP1 to NA17_5 upgrade test"
    """ % (my_binary_name, my_username, my_binary_name, my_username)

    parser_request_lab = subparsers.add_parser('request-lab',
                                               description=request_lab_func.__doc__ + request_lab_help_txt,
                                               formatter_class=argparse.RawTextHelpFormatter)

    required_named = parser_request_lab.add_argument_group('required arguments')
    required_named.add_argument('-q', '--state-search-query',
                                help="State search query with Mongo specific format. Both native Mongo queries and Python conditional expressions are supported. See 'python eve filtering' feature for more help. ",
                                dest="state_search_query",
                                required=True)
    required_named.add_argument('-m', '--message',
                                help="Free text for lab reservation message.",
                                dest="message",
                                required=True)
    parser_request_lab.add_argument('-lq', '--lab-search-query',
                                    help="Lab search query with Mongo specific format. Both native Mongo queries and Python conditional expressions are supported.\nSee 'python eve filtering' feature for more help. ",
                                    dest="lab_search_query",
                                    default=None,
                                    required=False)
    parser_request_lab.add_argument('-tag', '--reservation-tag',
                                    help='Tag for lab reservation: must be unique for all reservations. Allowed options are:\n\t${username}\n\t${state_search_query}\n\t${lab_search_query}\n\t${message}\n... or datetime.datime.strftime format placeholders like %%Y, %%m, %%d etc',
                                    dest="lab_reservation_tag",
                                    default='${username}-${state_search_query}-${lab_search_query}-%Y.%m.%d',
                                    required=False)
    parser_request_lab.add_argument('-wait', '--wait-time',
                                    help="Lab reservation waiting time, default '{}' seconds.".format(DEFAULT_LAB_RESERVATION_WAIT_TIME),
                                    dest="lab_reservation_wait_time",
                                    default=DEFAULT_LAB_RESERVATION_WAIT_TIME,
                                    required=False)
    parser_request_lab.add_argument('-rt', '--revert-time',
                                    help="Lab revert waiting time, default '{}' seconds.".format(DEFAULT_LAB_REVERT_WAIT_TIME),
                                    dest="lab_revert_wait_time",
                                    default=DEFAULT_LAB_REVERT_WAIT_TIME,
                                    required=False)
    parser_request_lab.add_argument('-dur', '--lab-reservation-duration',
                                    help="Lab reservation duration time",
                                    dest="lab_reservation_duration",
                                    default=DEFAULT_LAB_RESERVATION_DURATION_TIME,
                                    required=False)
    parser_request_lab.set_defaults(func = request_lab_func)
    if parser_request_lab._action_groups:
        parser_request_lab._action_groups.reverse()

def _add_release_lab_parser(subparsers, my_binary_name, my_username, release_lab_func):
    release_lab_help_txt = """
    e.g.
          python %s -u %s release-lab --lab-name SprintLab4702
    """ % (my_binary_name, my_username)

    parser_release_lab = subparsers.add_parser('release-lab',
                                               description=release_lab_func.__doc__ + release_lab_help_txt,
                                               formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_release_lab.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)
    parser_release_lab.add_argument('-f', '--force',
                                    help="force releasing of lab reservation",
                                    dest="force_release",
                                    action='store_true',
                                    default=False)

    parser_release_lab.set_defaults(func=release_lab_func)
    if parser_release_lab._action_groups:
        parser_release_lab._action_groups.reverse()

def _add_change_lab_reservation_parser(subparsers, my_binary_name, my_username, change_lab_reservation_func):
    change_lab_reservation_txt = """
    e.g.
          python %s -u %s change-lab-reservation -lab SprintLab4702 -dur [+|-]SECONDS
          python %s -u %s change-lab-reservation -lab SprintLab4702 -dur ABSOLUTE_DURATION_SECONDS

          python %s -u %s change-lab-reservation -lab SprintLab4702 --duration "2018-11-11T11:11" 
    """ % (
        my_binary_name, my_username, my_binary_name, my_username, my_binary_name, my_username,
        )

    parser_change_lab_reservation = subparsers.add_parser('change-lab-reservation',
                                               description=change_lab_reservation_func.__doc__ + change_lab_reservation_txt,
                                               formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_change_lab_reservation.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)
    parser_change_lab_reservation.add_argument('-dur',
                                dest="duration",
                                help='[+-]duration in seconds to extend/reduce, or date as YYYY-MM-DDTHH:MM',
                                required=True)

    parser_change_lab_reservation.set_defaults(func=change_lab_reservation_func)
    if parser_change_lab_reservation._action_groups:
        parser_change_lab_reservation._action_groups.reverse()

def _add_preserve_state_parser(subparsers, my_binary_name, my_username, preserve_state_func, _check_wait_time):
    preserve_state_help_txt = """
    e.g.
          python %s -u %s show-schema

          python %s -u %s preserve-state -lab SprintLab4702 -s \"build.id=netact/product/99.17.03.0.335\" -wait 10
          python %s -u %s preserve-state -lab vSprint3934 -a \"nes='BSC-1'\" -a \"nes='MSC-1'\" -wait 100
          python %s -u %s preserve-state -lab CloudLab183 -s \"build.id=netact/product/99.17.03.0.335\" -a \"nes='BSC-1'\" -t
    """ % (my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username)

    parser_preserve_state = subparsers.add_parser('preserve-state',
                                                  description=preserve_state_func.__doc__ + preserve_state_help_txt,
                                                  formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_preserve_state.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)

    parser_preserve_state.add_argument('-wait', '--wait-time',
                                       help="Snapshot waiting time, default '{}' seconds.".format(DEFAULT_PRESERVE_STATE_WAIT_TIME),
                                       dest="snapshot_wait_time",
                                       type=_check_wait_time,
                                       default=DEFAULT_PRESERVE_STATE_WAIT_TIME,
                                       required=False)

    parser_preserve_state.add_argument('-d', '--delete-attribute',
                                       help="Deletes given 'state' attribute.",
                                       dest="delete_attribute_list",
                                       action='append',
                                       required=False)

    parser_preserve_state.add_argument('-a', '--append-to-list',
                                       help="Appends a new item to existing 'state' list-type attribute or creates a new list-type attribute.",
                                       dest="append_to_list_list",
                                       action='append',
                                       required=False)

    parser_preserve_state.add_argument('-s', '--set-attribute',
                                       help="Sets or updates existing 'state' attribute value.",
                                       dest="set_attribute_list",
                                       action='append',
                                       required=False)

    parser_preserve_state.add_argument('-t', '--trigger-and-exit',
                                       help="Triggers a snapshot operation and returns immediately.",
                                       dest="trigger_and_exit",
                                       action='store_true',
                                       default=False,
                                       required=False)
    parser_preserve_state.set_defaults(func=preserve_state_func)
    if parser_preserve_state._action_groups:
        parser_preserve_state._action_groups.reverse()

def _add_show_labs_parser(subparsers, my_binary_name, my_username, show_labs_func):
    show_labs_help_txt = """
    e.g.
          python %s -u %s show-labs
          python %s -u %s show-labs -lab SprintLab4702
          python %s -u %s show-labs -fb FREE
    """ % (my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username)

    parser_show_labs = subparsers.add_parser('show-labs',
                                             description=show_labs_func.__doc__ + show_labs_help_txt,
                                             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_show_labs.add_argument('-lab', '--lab-name',
                                  help="Filter for listing only given lab.",
                                  dest="lab_name",
                                  required=False)

    parser_show_labs.add_argument('-fb', '--filtered-by',
                                  help="Filter for listing selected labs.",
                                  dest="filtered_by",
                                  choices=['FREE', 'RESERVED'],
                                  default="",
                                  required=False)

    parser_show_labs.set_defaults(func=show_labs_func)

def _add_show_snapshot_parser(subparsers, my_binary_name, my_username, show_snapshot_func):
    show_labs_help_txt = """
    e.g.
          python %s -u %s show-snapshots
          python %s -u %s show-snapshots -labs
          python %s -u %s show-snapshots -snap 99.* -labs
          python %s -u %s show-snapshots -snap netact/product/99.17.03.0.522 
    """ % (my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username)

    parser_show_snapshots = subparsers.add_parser('show-snapshots',
                                             description=show_snapshot_func.__doc__ + show_labs_help_txt,
                                             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_show_snapshots.add_argument('-labs', '--show_labs',
                                                      dest="labs_shown",
                                                      help="Show lab names in snapshots",
                                                      required=False,
                                                      action='store_true')

    parser_show_snapshots.add_argument('-snap', '--snapshot-name',
                                  help="Filter for listing only given snapshot.",
                                  dest="snapshot_name",
                                  required=False)


    parser_show_snapshots.set_defaults(func=show_snapshot_func)


def _add_show_item_parser(subparsers, my_binary_name, my_username, show_item_func):
    show_item_help_txt = """
    e.g.
          python client.py -u root -v show-labs

          python %s -u %s show-item labs/5915b32632f2a00001c6ef5c
          python %s -u %s show-item states/5915b32632f2a00001c3432
          python %s -u %s show-item reservations/5923432632f2a00001c3432
    """ % (my_binary_name, my_username,
           my_binary_name, my_username,
           my_binary_name, my_username)

    parser_show_item = subparsers.add_parser('show-item',
                                             description=show_item_func.__doc__ + show_item_help_txt,
                                             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_show_item.add_argument('href', help='href string')

    parser_show_item.set_defaults(func=show_item_func)

def _add_show_schema_parser(subparsers, my_binary_name, my_username, show_schema_func):
    show_schema_help_txt = """
    e.g.
          python %s -u %s show-schema
          python %s -u %s show-schema -i labs
    """ % (my_binary_name, my_username, my_binary_name, my_username)

    parser_show_schema = subparsers.add_parser('show-schema',
                                               description=show_schema_func.__doc__ + show_schema_help_txt,
                                               formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_show_schema.add_argument('-i', '--schema_item',
                                    choices=['labs', 'states', 'reservations', 'labrequests'],
                                    default="",
                                    required=False)

    parser_show_schema.set_defaults(func=show_schema_func)

def _add_admin_patch_item_parser(subparsers, my_binary_name, my_username, admin_username, admin_patch_item_func):
    admin_patch_item_help_txt = """
    e.g.
          python client.py -u root -v show-labs

          python %s -u %s admin-patch-item labs/5915b32632f2a00001c6ef5c "status=initializing"
          python %s -u %s admin-patch-item states/5915b32632f2a00001c3432 "build.id=netact17.8_p7,snapshot_id=SprintLab283-23483597803"
          python %s -u %s admin-patch-item reservations/5923432632f2a00001c3432 "message=This is test reservation"

          python %s -u %s admin-patch-item labs/5915b32632f2a00001c6ef5c "{'status': 'ready'}"
          python %s -u %s admin-patch-item states/5915b32632f2a00001c3432 "{'build.id': 'netact17.8_p7' , 'snapshot_id': 'SprintLab283-23483597803'}"
          python %s -u %s admin-patch-item states/5923432632f2a00001c3432 "{'build_history': ['testbuild1' , 'testbuild4'], 'integrated_nes': ['bsc-1', 'mrbts-2']}"


    """ % (my_binary_name, admin_username, my_binary_name, admin_username,
           my_binary_name, admin_username, my_binary_name, admin_username,
           my_binary_name, admin_username, my_binary_name, admin_username)

    parser_admin_patch_item = subparsers.add_parser('admin-patch-item',
                                                    description=admin_patch_item_func.__doc__ + admin_patch_item_help_txt,
                                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_admin_patch_item.add_argument('href', help='href string')
    parser_admin_patch_item.add_argument('param_list',
                                         help='parameters: csv list of parameter=value or JSON string')

    parser_admin_patch_item.set_defaults(func=admin_patch_item_func)

def _add_admin_migrate_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, admin_migrate_snapshots_func):
    admin_migrate_snapshots_help_txt = """
    e.g.
          python %s -u %s admin-migrate-snapshots -labs sprintlab245
          python %s -u %s admin-migrate-snapshots -labs sprintlab245,vsp0061
          python %s -u %s admin-migrate-snapshots -labs sprintlab245,vsp0061 -user admin -pw adminpw
          python %s -u %s admin-migrate-snapshots -labs sprintlab245,vsp0061 -port 29
    """ % (my_binary_name, admin_username, my_binary_name, admin_username,
           my_binary_name, admin_username, my_binary_name, admin_username)

    parser_admin_migrate_snapshots = subparsers.add_parser('admin-migrate-snapshots',
                                                           description=admin_migrate_snapshots_func.__doc__ +
                                                           admin_migrate_snapshots_help_txt,
                                                           formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_admin_migrate_snapshots.add_argument_group('required arguments')
    required_named.add_argument('-labs', '--lab-names',
                                help="csv list of 'lab_name' values",
                                type=_csv_list, action='store',
                                dest="lab_names",
                                required=True)

    parser_admin_migrate_snapshots.add_argument('-user', '--admin_server_username',
                                                dest='admin_server_username',
                                                help='username for admin server access, default: \'' +
                                                ADMIN_SERVER_ACCESS_USERNAME_DEFAULT + '\'',
                                                default=ADMIN_SERVER_ACCESS_USERNAME_DEFAULT,
                                                required=False)

    parser_admin_migrate_snapshots.add_argument('-pw', '--admin_server_password',
                                                dest='admin_server_password',
                                                help='password for admin server access, default: \'' +
                                                ADMIN_SERVER_ACCESS_PASSWORD_DEFAULT + '\'',
                                                default=ADMIN_SERVER_ACCESS_PASSWORD_DEFAULT,
                                                required=False)

    parser_admin_migrate_snapshots.add_argument('-host', '--admin_server_host',
                                                dest='admin_server_host',
                                                help='host for admin server access, default: \'' +
                                                ADMIN_SERVER_ACCESS_HOST_HELP_DEFAULT,
                                                default="",
                                                required=False)

    parser_admin_migrate_snapshots.add_argument('-port', '--admin_server_port',
                                                dest='admin_server_port',
                                                help='port for admin server access, default: \'' +
                                                str(ADMIN_SERVER_ACCESS_PORT_DEFAULT) + '\'',
                                                default=ADMIN_SERVER_ACCESS_PORT_DEFAULT,
                                                required=False)

    parser_admin_migrate_snapshots.set_defaults(func=admin_migrate_snapshots_func)
    if parser_admin_migrate_snapshots._action_groups:
        parser_admin_migrate_snapshots._action_groups.reverse()

def _add_admin_remove_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, admin_remove_snapshots_func):
    admin_remove_snapshots_help_txt = """
    e.g.
          python %s -u %s -v show-labs

          python %s -u %s admin-remove-snapshots -lab sprintlab245 -snaps "SprintLab245-1477398696,SprintLab245-8577986646"
          python %s -u %s admin-remove-snapshots -lab sprintlab245 -snaps "SprintLab245-1477398696" -f
    """ % (my_binary_name, admin_username, my_binary_name, admin_username, my_binary_name, admin_username)

    parser_admin_remove_snapshots = subparsers.add_parser('admin-remove-snapshots',
                                                          description=admin_remove_snapshots_func.__doc__ +
                                                          admin_remove_snapshots_help_txt,
                                                          formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_admin_remove_snapshots.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)

    required_named.add_argument('-snaps', '--snapshot_ids',
                                help="csv list of values",
                                type=_csv_list, action='store',
                                dest="snapshot_ids",
                                default=None,
                                required=True)

    parser_admin_remove_snapshots.add_argument('-f', '--force',
                                               help="force removal of snapshot(s)",
                                               dest="force_removal_flag",
                                               action='store_true',
                                               default=False)

    parser_admin_remove_snapshots.set_defaults(func=admin_remove_snapshots_func)
    if parser_admin_remove_snapshots._action_groups:
        parser_admin_remove_snapshots._action_groups.reverse()

def _add_admin_add_lab_parser(subparsers, my_binary_name, my_username, admin_username, admin_add_lab_func):
    admin__add_lab_help_txt = """
    e.g.
          python %s -u %s admin-add-lab -lab sprintlab245
          python %s -u %s admin-add-lab -lab sprintlab245 -type sprint
          python %s -u %s admin-add-lab -lab sprintlab245 -type sprint -status initializing
    """ % (my_binary_name, admin_username, my_binary_name, admin_username, my_binary_name, admin_username)

    parser_admin__add_lab = subparsers.add_parser('admin-add-lab',
                                                 description=admin_add_lab_func.__doc__ +
                                                 admin__add_lab_help_txt,
                                                 formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_admin__add_lab.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)

    parser_admin__add_lab.add_argument('-type', '--lab-type',
                                      dest="lab_type",
                                      action='store',
                                      choices=ALLOWED_LAB_TYPES,
                                      default=None,
                                      required=False)

    parser_admin__add_lab.add_argument('-status', '--lab-status',
                                      dest="lab_status",
                                      action='store',
                                      choices=ALLOWED_ADD_LAB_STATUSES,
                                      default="ready",
                                      required=False)

    parser_admin__add_lab.set_defaults(func=admin_add_lab_func)
    if parser_admin__add_lab._action_groups:
        parser_admin__add_lab._action_groups.reverse()

def _add_admin_remove_labs_parser(subparsers, my_binary_name, my_username, admin_username, admin_remove_labs_func):
    admin_remove_labs_help_txt = """
    e.g.
          python %s -u %s admin-remove-labs -labs sprintlab245
          python %s -u %s admin-remove-labs -labs sprintlab245,vsp0061
          python %s -u %s admin-remove-labs -labs sprintlab245,vsp0061 -f
    """ % (my_binary_name, admin_username, my_binary_name,
           admin_username, my_binary_name, admin_username)

    parser_admin_remove_labs = subparsers.add_parser('admin-remove-labs',
                                                     description=admin_remove_labs_func.__doc__ +
                                                     admin_remove_labs_help_txt,
                                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_admin_remove_labs.add_argument_group('required arguments')
    required_named.add_argument('-labs', '--lab-names',
                                help="csv list of 'lab_name' values",
                                type=_csv_list, action='store',
                                dest="lab_names",
                                required=True)

    parser_admin_remove_labs.add_argument('-f', '--force',
                                          help="force removal of lab(s)",
                                          dest="force_removal_flag",
                                          action='store_true',
                                          default=False)

    parser_admin_remove_labs.set_defaults(func=admin_remove_labs_func)
    if parser_admin_remove_labs._action_groups:
        parser_admin_remove_labs._action_groups.reverse()

def _add_admin_reserve_labs_parser(subparsers, my_binary_name, my_username, admin_username, admin_reserve_labs_func):
    admin_reserve_labs_help_txt = """
    e.g.
          python %s -u %s admin-reserve-labs -labs sprintlab245
          python %s -u %s admin-reserve-labs -labs sprintlab245,vsp0061 -m "Reserved for maintenance work"
          python %s -u %s admin-reserve-labs -labs sprintlab245,vsp0061 -f
    """ % (my_binary_name, admin_username, my_binary_name, admin_username, my_binary_name, admin_username)

    parser_admin_reserve_labs = subparsers.add_parser('admin-reserve-labs',
                                                      description=admin_reserve_labs_func.__doc__ +
                                                      admin_reserve_labs_help_txt,
                                                      formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_admin_reserve_labs.add_argument_group('required arguments')
    required_named.add_argument('-labs', '--lab-names',
                                help="csv list of 'lab_name' values",
                                type=_csv_list, action='store',
                                dest="lab_names",
                                required=True)

    parser_admin_reserve_labs.add_argument('-m', '--message',
                                           help="additional info message, default is 'Lab reserved for maintanance work'",
                                           dest="user_message",
                                           default=ADMIN_RESERVE_LAB_MESSAGE)

    parser_admin_reserve_labs.add_argument('-f', '--force',
                                           help="force reservation for 'admin' by removing existing reservation",
                                           dest="force_reservation_flag",
                                           action='store_true',
                                           default=False)

    parser_admin_reserve_labs.set_defaults(func=admin_reserve_labs_func)
    if parser_admin_reserve_labs._action_groups:
        parser_admin_reserve_labs._action_groups.reverse()

def _add_admin_data_backup_parser(subparsers, my_binary_name, my_username, admin_username, admin_data_backup_func):
    admin_data_backup_help_txt = """
    e.g.
          python %s -u %s admin-data-backup
    """ % (my_binary_name, my_username)

    parser_admin_data_backup = subparsers.add_parser('admin-data-backup',
                                                     description=admin_data_backup_func.__doc__ +
                                                     admin_data_backup_help_txt,
                                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_admin_data_backup.add_argument('-lab', '--lab-name',
                                          dest="lab_name",
                                          required=True)

    parser_admin_data_backup.set_defaults(func=admin_data_backup_func)

def _add_admin_data_restore_parser(subparsers, my_binary_name, my_username, admin_username, admin_data_restore_func):
    admin_data_restore_help_txt = """
    e.g.
          python %s -u %s admin-data-restore
    """ % (my_binary_name, my_username)

    parser_admin_data_restore = subparsers.add_parser('admin-data-restore',
                                                      description=admin_data_restore_func.__doc__ +
                                                      admin_data_restore_help_txt,
                                                      formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_admin_data_restore.add_argument('-lab', '--lab-name',
                                           dest="lab_name",
                                           required=True)

    parser_admin_data_restore.set_defaults(func=admin_data_restore_func)

def _add_show_admin_server_access_data(subparsers, my_binary_name, my_username, admin_username, show_admin_server_access_data_func):
    show_admin_server_access_data_help_txt = """
    e.g.
          python %s -u %s show-admin-server-access-data -l vosp0013 -snap netact/product/99.17.03.0.166
    """ % (my_binary_name, my_username)

    parser_show_admin_server_access_data = subparsers.add_parser('show-admin-server-access-data',
                                                                 description=show_admin_server_access_data_func.__doc__ +
                                                                 show_admin_server_access_data_help_txt,
                                                                 formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_show_admin_server_access_data.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=False)

    parser_show_admin_server_access_data.add_argument('-snap', '--snapshot_id',
                                                      dest="snapshot_id",
                                                      required=False)

    parser_show_admin_server_access_data.set_defaults(func=show_admin_server_access_data_func)

    if parser_show_admin_server_access_data._action_groups:
        parser_show_admin_server_access_data._action_groups.reverse()

def _add_create_test_labs_parser(subparsers, my_binary_name, my_username, create_test_labs_func):
    create_test_labs_help_txt = """
    e.g.
          python %s -u %s create-test-labs
    """ % (my_binary_name, my_username)

    parser_create_test_labs = subparsers.add_parser('create-test-labs',
                                                    description=create_test_labs_func.__doc__ + create_test_labs_help_txt,
                                                    formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_create_test_labs.set_defaults(func=create_test_labs_func)

def _add_create_test_snapshots_parser(subparsers, my_binary_name, my_username, admin_username, create_test_snapshots_func):
    create_test_snapshots_help_txt = """
    e.g.
          python %s -u %s create-test-snapshots -lab CloudLab2345
          python %s -u %s create-test-snapshots -lab CloudLab2345 -c 1
          python %s -u %s create-test-snapshots --lab_name CloudLab2345 --count 9
    """ % (my_binary_name, admin_username, my_binary_name,  admin_username, my_binary_name,  admin_username)

    parser_create_test_snapshots = subparsers.add_parser('create-test-snapshots',
                                                         description=create_test_snapshots_func.__doc__ + create_test_snapshots_help_txt,
                                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    required_named = parser_create_test_snapshots.add_argument_group('required arguments')
    required_named.add_argument('-lab', '--lab-name',
                                dest="lab_name",
                                required=True)

    parser_create_test_snapshots.add_argument('-c', '--count',
                                              type=int,
                                              dest='count',
                                              help='count of snapshots, default is 3',
                                              default=3,
                                              required=False)

    parser_create_test_snapshots.set_defaults(func=create_test_snapshots_func)
    if parser_create_test_snapshots._action_groups:
        parser_create_test_snapshots._action_groups.reverse()

def _add_config_change_parser(subparsers, my_binary_name, my_username, get_server_config_entry, set_server_config_entry, remove_server_config_entry):
    config_change_help = '''
    e.g.
          python %s -u %s config [-get <name>|-set <name> <value>|-del <name>]
    ''' % (my_binary_name, my_username)
    config_change_parser = subparsers.add_parser('config',
                                                 description = config_change_help,
                                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    config_change_subparsers = config_change_parser.add_subparsers()
    for op, nargs, func in [
            ('get',1, get_server_config_entry),
            ('set',2, set_server_config_entry),
            ('del',1, remove_server_config_entry)]:
        '''
        config_op.add_argument('-'+op, nargs=nargs,
                            action='store', 
                            help='<config op name>' + (' <value>' if nargs > 1 else ''))
        '''
        op_parser = config_change_subparsers.add_parser(op, description = config_change_help, formatter_class=argparse.RawDescriptionHelpFormatter)
        op_parser.add_argument('name', action='store', help='name of config attribute')
        if nargs == 2:
            op_parser.add_argument('value', action='store', help='value for config attribute')
        op_parser.set_defaults(func=func)
    
def _csv_list(string):
    return string.split(',')

def check_wait_time(string):
    value = int(string)
    if value <= 0:
        msg = " '--wait-time' value '{}' out of range, must be >0 !".format(value)
        raise argparse.ArgumentTypeError(msg)
    return value

