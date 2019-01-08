'''helper module for handling Python dicts and lists
'''
import shlex
from functools import reduce
import operator
import logging
log = logging.getLogger(__name__)


def _get_from_dict(data_dict, map_list):
    log.debug('_get_from_dict(data_dict=%s, map_list=%s)' % (data_dict, map_list))
    return reduce(operator.getitem, map_list, data_dict)


def _set_in_dict(data_dict, map_list, value):
    log.debug('_set_in_dict(data_dict=%s, map_list=%s)' % (data_dict, map_list))
    _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def _append_in_dict(data_dict, map_list, value):
    orig_value = _get_from_dict(data_dict, map_list[:-1])[map_list[-1]]
    if not orig_value:
        _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = [value]
    elif type(orig_value) is list:
        orig_value.append(value)
        _get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = orig_value
    else:
        raise TypeError("Value \"{}\" is not list".format(orig_value))


def _delete_in_dict(data_dict, map_list):
    del _get_from_dict(data_dict, map_list[:-1])[map_list[-1]]


def _get_maplist(map_string):
    return dict(token.split('=', 1) for token in shlex.split(map_string))


def _ensure_empty_paths(data_dict, map_list):
    """Adds new dictionary leaves to data_dict based on map_list."""
    value = None
    try:
        value = _get_from_dict(data_dict, map_list)
    except KeyError:
        pass
    except TypeError:
        pass
    new_paths = reduce(lambda x, y: {y: x}, reversed(map_list + [value]))
    log.debug("new_paths: {}".format(new_paths))
    log.debug("original_paths: {}".format(data_dict))
    _dict_merge(data_dict, new_paths)
    log.debug("updated: {}".format(data_dict))


def _dict_merge(a, b, path=None):
    """Merges b into a."""
    path = path if path is not None else []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif a[key] is None:
                a[key] = b[key]  # allow overwriting None values
            else:
                raise RuntimeError("Conflict at {0} (orig: \"{1}\" new: \"{2})\"".format('.'.join(path + [str(key)]), a[key], b[key]))
        else:
            a[key] = b[key]
    return a


class DictionaryBuilder(object):

    def __init__(self,
                 inherit=None,
                 add=None,
                 delete=None,
                 append=None,
                 exclude_meta=False):
        """Build a dictionary based on an existing dictionary by declaring the delta.

        :param inherit: Dictionary to build changes on. {"attr": {"attr": "value"}}
        :param add: Attributes to be added/modified. ["attr.attr=value", ...]
        :param delete: Attributes to be deleted. ["attr.attr", ...]
        :param append: Items to be appended to a list attribute. ["attr.attr=value", ...]
        """
        if exclude_meta:
            self._object = {k: v for k, v in inherit.items() if not k.startswith("_")}
        else:
            self._object = inherit
        self._to_be_added_list = add
        self._to_be_deleted_list = delete
        self._to_be_appended_list = append
        self._delete()
        self._add()
        self._append()

    @property
    def data(self):
        """Modified dictionary"""
        return self._object

    def __getitem__(self, item):
        return self._object[item]

    def _add(self):
        if self._to_be_added_list:
            for attribute_map in self._to_be_added_list:
                map_data = _get_maplist(attribute_map)
                for k, v in map_data.items():
                    map_list = k.split(".")
                    _ensure_empty_paths(self._object, map_list)
                    _set_in_dict(self._object, map_list, v)

    def _delete(self):
        if self._to_be_deleted_list:
            for d in self._to_be_deleted_list:
                map_list = d.split(".")
                try:
                    _delete_in_dict(self._object, map_list)
                except KeyError:  # don't fail when delete is called for key that does not exist
                    pass

    def _append(self):
        if self._to_be_appended_list:
            for a in self._to_be_appended_list:
                map_data = _get_maplist(a)
                for k, v in map_data.items():
                    map_list = k.split(".")
                    _ensure_empty_paths(self._object, map_list)
                    _append_in_dict(self._object, map_list, v)
