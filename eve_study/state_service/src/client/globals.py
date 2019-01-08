'''global definitions used by several modules under module 'client'
'''

STORAGE_API_URL = "http://10.91.228.255/rest/api/v2"

_SHOW_SCHEMA_ITEMS = ['labs', 'states', 'reservations', 'labrequests']

SCHEMA_ITEM_MAP = {
    _SHOW_SCHEMA_ITEMS[0]: '"' + _SHOW_SCHEMA_ITEMS[1] + '"',
    _SHOW_SCHEMA_ITEMS[1]: '"' + _SHOW_SCHEMA_ITEMS[3] + '"',
    _SHOW_SCHEMA_ITEMS[3]: '"' + _SHOW_SCHEMA_ITEMS[2] + '"',
    _SHOW_SCHEMA_ITEMS[2]: '}'
}

DEFAULT_LAB_RESERVATION_WAIT_TIME = 0
DEFAULT_LAB_RESERVATION_DURATION_TIME = 12 * 3600
DEFAULT_LAB_REVERT_WAIT_TIME = 8 * 3600
DEFAULT_PRESERVE_STATE_WAIT_TIME = 60
ALLOWED_LAB_TYPES = ['sprint', 'vsprint', 'cloud', 'vosp', 'other']
ALLOWED_ADD_LAB_STATUSES = ['ready', 'initializing']
SNAPSHOT_FORMAT = "%-70.70s  %-30.30s   %s \n"
CONFIRM_QUESTION_PREFIX = "Are You sure you want to "
CONFIRM_QUESTION_FOR_REMOVE_SNAPSHOTS = CONFIRM_QUESTION_PREFIX + "remove snapshots from Lab State Service and DC Storage? ([Y/n])\n"
CONFIRM_QUESTION_FOR_REMOVE_LABS = CONFIRM_QUESTION_PREFIX + "remove lab(s) from Lab State Service? ([Y/n])\n"
CONFIRM_QUESTION_OPERATION_CANCELLED = "Operation cancelled!"
CONFIRM_QUESTION_RIGHT_ANSWER = "Y"
RESERVE_LAB_FOR_DELETION_MESSAGE = "Lab is reserved for the deletion operation."
RESERVE_LAB_FOR_SNAPSHOT_DELETION_MESSAGE = "Lab is reserved for the 'snapshot' deletion operation."
ERROR_TXT = " ### ERROR: "
ERROR_TXT_NOT_ANY_LABS = ERROR_TXT + "Labs do not exist in Lab State Service!"
ERROR_TXT_LAB_DOES_NOT_EXIST = ERROR_TXT + "Lab '{}' does not exist in Lab State Service!"
ERROR_TXT_SNAPSHOT_WITH_BUILD_ID_DOES_NOT_EXIST_IN_LAB = ERROR_TXT + "Snapshot with build id '{}' does not exist in lab!"
ERROR_TXT_SNAPSHOT_DOES_NOT_EXIST_IN_LAB = ERROR_TXT + "Snapshot does not exist in lab!"
ADMIN_RESERVE_LAB_MESSAGE = "Lab reserved for maintanance work."
REMOVED_TXT = "REMOVED"
RESERVED_TXT = "RESERVED"
ADMIN_SERVER_ACCESS_PARAMETER_NAME = "admin_server_access"
ADMIN_SERVER_ACCESS_USERNAME_DEFAULT = "root"
ADMIN_SERVER_ACCESS_PASSWORD_DEFAULT = "nasroot"
ADMIN_SERVER_ACCESS_PORT_DEFAULT = 22
ADMIN_SERVER_ACCESS_PROTOCOL_DEFAULT = "ssh"
ADMIN_SERVER_ACCESS_HOST_DEFAULT_FORM = "{}vm1{}"
ADMIN_SERVER_ACCESS_HOST_NETWORK_DEFAULT = ".netact.nsn-rdnet.net"
ADMIN_SERVER_ACCESS_HOST_HELP_DEFAULT = ADMIN_SERVER_ACCESS_HOST_DEFAULT_FORM.format("<lab_name>", ADMIN_SERVER_ACCESS_HOST_NETWORK_DEFAULT)
LAB_NAME_KEY = "labName"
BUILD_ID_KEY = "buildId"
ADMIN_SERVER_ACESS_KEY = "admin_server_access"


class AsciiColors:
    OKGREEN = '\033[92m'
    FREE = '\033[1;90m'
    BG_FREE = '\033[101m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESERVED = '\033[1;91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REMOVED = '\033[30m'
    OKBLACK = '\033[30m'


