"""module settings s used by eve (http://python-eve.org/)

Please see http://eve.readthedocs.io/en/latest/config.html for full
documentation about configuring eve.

"""

import os

# - datetime: Defaults to the RFC1123 (ex RFC 822) standard a, %d %b %Y %H:%M:%S GMT ("Tue, 02 Apr 2013 10:29:13 GMT").
DOMAIN = dict(
suts = {
  'schema': {
    'suts': {
      'items': 'list'
    }
  }
},
reservations = {
    'mongo_indexes': {'res_expire_at': ([('expireAt', 1)], {"expireAfterSeconds": 0})},
    'schema': {
        'lab': {
            'unique': True,
            'required': True,
            'empty': False,
            'type': 'objectid',
            'data_relation': {
                'resource': 'labs',
                'field': '_id',
                'embeddable': True
            }
        },
        'expireAt': {
            'type': 'datetime'
        },
        'duration': {
            ##'type': 'integer' # -N works, but +N not
            'type': 'string', 'regex': '^[+-]?\d+$',
        },
        'username': {
            'type': 'string',
            'required': True
        },
        'message': {
            'type': 'string'
        },
        'tag': {
            'type': 'string'
        },
        'labrequest_id': {
            'type': 'string'
        },
    }
},
labs = {
    'schema': {
        'lab_name': {
            'type': 'string',
            'required': True,
            'unique': True,
            'empty': False
        },
        # lab_type is bit dangerous because it hides lot of characteristics of a lab behind the type.
        # It would be better to be able to describe these attributes instead of a type.
        # However, I'm not able to and nor would our users at the moment.
        # In addition, these types are tightly coupled with DCINFRA offering.
        #
        # My thinking is we need to explore possibility of searching by labs based on DCAPI labinfo.
        'lab_type': {
            'type': 'string',
            'allowed': ['sprint',
                        'vsprint',
                        'vosp',
                        'cloud',
                        'other']
        },
        'states':
            {'type': 'list',
             'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'states',
                    'field': '_id',
                    'embeddable': True
                    }
                }
             },
        'reservation': {
            'type': 'objectid',
            'unique': True,
            'nullable': True,
            'data_relation': {
                'resource': 'reservations',
                'field': '_id',
                'embeddable': True
            }
        },
        'status': {
            'type': 'string',
            'allowed': ['reverting_state',
                        'preserving_state',
                        'state_operation_failed',
                        'queued_for_initialization',
                        'queued_for_revert',
                        'initializing',
                        'ready'],
            'default': 'queued_for_initialization'
        },
        'previously_reverted_state': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'states',
                    'field': '_id',
                    'embeddable': True
                }
        }
    },
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'lab_name'
    },
},
states = {
    'schema': {
        'build': {
            'type': 'dict',
            'required': True,
            'schema': {
                'id': {'type': 'string',
                       'required': True
                       },
                'nick_name': {'type': 'string'}
            },
        },
        'build_history': {'type': 'list'},
        'integrated_nes': {'type': 'list'},
        'snapshot_status': {'type': 'string',
                            'allowed': ['queued',
                                        'creating',
                                        'available',
                                        'failed'],
                            'default': 'queued'
                            },
        'snapshot_id': {'type': 'string',
                        'dependencies': ['snapshot_status']
                        },
        'admin_server_access': {
            'type': 'dict',
            'schema': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'host': {'type': 'string'},
                'port': {'type': 'integer'},
                'protocol': {'type': 'string'},
            },
        },
        'lab': {'type': 'objectid',
                'required': True,
                'data_relation': {
                    'resource': 'labs',
                    'field': '_id',
                    'embeddable': True
                    }
                }
    }
},
labrequests = {
    'mongo_indexes': {'lreq_expire_at': ([('expireAt', 1)], {"expireAfterSeconds": 0})},
    'schema': {
        'state_search_query': {
            'type': 'string',
            'required': True
        },
        'username': {
            'type': 'string',
            'required': True
        },
        'lab_search_query': {
            'type': 'string'
        },
        'group': {
            'type': 'string'
        },
        'lab_reservation_time': {
            'type': 'string',
            'default': '60'
        },
        'tag': {
            'type': 'string'
        },
        'message': {
            'type': 'string'
        },
        'lab': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'labs',
                'field': '_id',
                'embeddable': True
            }
        },
        'status': {
            'type': 'string',
            'allowed': ['pending',
                        'no_matching_state',
                        'no_matching_lab',
                        'no_lab_available',
                        'error',
                        'ready'],
            'default': 'pending'
        },
        'expireAt': {
            'type': 'datetime',
            'readonly': True
        }
    }
},
config = {
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
            'unique': True,
        },
        'value': {
            'type': 'string',
            'required': False
        },
    },
    'id_field': 'name',
    'item_url': 'regex("[\w]+")',
    'item_lookup_field': 'name',
},
)

MONGO_HOST = 'mongo' if not os.getenv('STATE_SERVICE_MONGO_HOST') else os.getenv('STATE_SERVICE_MONGO_HOST')
MONGO_PORT = 27017 if not os.getenv('STATE_SERVICE_MONGO_PORT') else os.getenv('STATE_SERVICE_MONGO_PORT')
MONGO_DBNAME = 'apitest' if not os.getenv('STATE_SERVICE_MONGO_DBNAME') else os.getenv('STATE_SERVICE_MONGO_DBNAME')
#MONGO_USERNAME = '<your username>'
#MONGO_PASSWORD = '<your password>'
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
CACHE_CONTROL = ''
CACHE_EXPIRES = 0
INFO = "_info"
SWAGGER_INFO = {
    'title': 'State service API',
    'version': '0.1',
    'description': 'an API description',
    'termsOfService': 'my terms of service',
    'contact': {
        'name': 'NetAct R&D Tre'
    }
}
STATE_SERVICE_SWAGGER_UI_URI = "http://localhost:8080" if not os.getenv('STATE_SERVICE_SWAGGER_UI_URI') else os.getenv('STATE_SERVICE_SWAGGER_UI_URI')
X_DOMAINS = [STATE_SERVICE_SWAGGER_UI_URI,
             'http://editor.swagger.io',
             'http://petstore.swagger.io']
X_HEADERS = ['Content-Type', 'If-Match']  # Needed for the "Try it out" buttons
ENABLE_HOOK_DESCRIPTION = True  # swagger documentation for hooks
# TRANSPARENT_SCHEMA_RULES = True  # needed for swagger resource descriptions
XML = False  # disable XML response rendering
PRESERVE_CONTEXT_ON_EXCEPTION = False
SCHEMA_ENDPOINT = "schema"
if os.getenv('STATE_SERVICE_ENABLE_OPLOG'):
    OPLOG = True
    OPLOG_ENDPOINT = "oplog"
MONGO_QUERY_BLACKLIST = ['$where']
