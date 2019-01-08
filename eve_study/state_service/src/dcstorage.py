'''Client for Tampere OSS&CEM API for handling Storage snapshots
'''

import requests
from requests import exceptions
import os
import urlparse
import logging
import json
import time

log = logging.getLogger(__name__)


class _Config(object):
    def __init__(self):
        """Reads configuration values from environment variables. Set as follows
        export DCASA_URL="http://<API PROVIDER>/rest/api/v2"
        export DCSA_USERNAME="user"
        export DCSA_PASSWORD="password"
        """
        self.api_url = os.environ.get('DCSA_URL')
        self.username = os.environ.get('DCSA_USERNAME')
        self.password = os.environ.get('DCSA_PASSWORD')


class _Client(object):
    """Generic HTTP client"""

    def __init__(self, api_url=None, username=None, password=None, timeout=20):
        self._config = _Config()
        if api_url:
            self._api_url = api_url
        else:
            self._api_url = self._config.api_url
        if username:
            self._username = username
        else:
            self._username = self._config.username
        if password:
            self._password = password
        else:
            self._password = self._config.password
        self._timeout = timeout
        assert self._api_url, "api_url missing"
        assert self._username, "username missing"
        assert self._password, "password missing"

    def request(self, url, method, params=None, data=None, extra_fields=None, authenticate=True, raise_for_status=True, timeout=None):
        """This method makes HTTP requests (GET, DELETE, POST, PUT). All data exchanges between this client and the
        server instance are encoded in JSON notation.

        returns content decoded into python objects.
        """
        if not timeout:
            timeout = self._timeout
        supported_methods = ['GET', 'PUT', 'POST', 'DELETE']
        if method not in supported_methods:
                raise ValueError("Unsupported HTTP method [{0}]".format(method))
        if hasattr(self, '_api_url'):
            log.debug("_api_url: " + self._api_url)
            log.debug("url: " + url.strip('/'))
            url = urlparse.urljoin(self._api_url + '/', url.strip('/'))
        log.info("url: {0} - method: {1}".format(url, method))
        fields = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            }
        if authenticate:
            fields.update({"Authorization": "{0}:{1}".format(self._username, self._password)})
        if extra_fields:
            fields.update(extra_fields)
        rsp = None
        rsp_data = None
        try:
            request = getattr(requests, method.lower())
            if data:
                rsp = request(url, params=params, data=json.dumps(data), headers=fields, timeout=timeout, verify=False)
            else:
                rsp = request(url, params=params, headers=fields, timeout=timeout, verify=False)
            if raise_for_status:
                rsp.raise_for_status()
            content_type = rsp.headers['content-type']
            log.debug("content_type: {}".format(content_type))
            if content_type != 'application/json':
                raise requests.exceptions.HTTPError("Content-Type \"{0}\" not accepted".format(content_type))
            rsp_data = rsp.json()
        except requests.exceptions.Timeout:
            log.error("HTTP request timeout")
            raise
        except requests.exceptions.HTTPError:
            log.error("HTTP request failed\n"
                      "Error response status code: {0}\n"
                      "Error response message: {1}".format(rsp.status_code, rsp.text))
            raise
        except ValueError as e:
            log.exception(e)
            raise exceptions.ContentDecodingError("Didn't receive json data\nData:{}".format(rsp.text))
        return rsp_data


class DCSAClient(object):

    def __init__(self, api_url=None, username=None, password=None, timeout=20):

        """Client for DCSA API: https://confluence.int.net.nokia.com/display/OSSOPLSVL/DCSAStorageSnapshot

        :param api_url: <http://<API PROVIDER>/rest/api/v2>
        :param password:
        :param username:
        :param timeout: int
        * Seconds to wait for http connection.\n
        * Seconds to wait between bytes when receiving data.\n
        * A tuple can be used to specify values separately.\n

        If params are omitted, reads configuration values from environment variables. Set as follows\n
        export DCASA_URL="http://<API PROVIDER>/rest/api/v2"\n
        export DCSA_USERNAME="user"\n
        export DCSA_PASSWORD="password"\n

        """
        self._client = _Client(api_url=api_url, password=password, username=username, timeout=timeout)
        self._events = []

    @property
    def events(self):
        return self._events

    def get_snapshot_status(self, lab):
        """Get snapshot related information for a lab.
        :param lab: e.g. 'CLAB1234'
        :return: {'snapshots': [{}, {}, ...], 'maxsnapshots': int}
        """
        method = "GET"
        path = "storage/snapshot/{}".format(lab)
        rsp = self._client.request(path, method)
        return rsp

    def get_event(self, event_id):
        """Get details for an event.
        :param event_id: e.g 1234
        :return: {}
        """
        method = 'GET'
        path = "storage/eventstatus/{0}".format(event_id)
        rsp = self._client.request(path, method)
        return rsp

    def get_ongoing_events(self, lab):
        """Get ongoing snapshot events for a lab.
        :param lab: e.g. 'CLAB1234'
        :return: [{}, {}, ... ]
        """
        method = "GET"
        path = "storage/ongoingevents/{0}".format(lab)
        rsp = self._client.request(path, method)
        return rsp

    def get_all_events(self, lab, limit=None):
        """Get all snapshot events for a lab.
        :param lab: e.g. 'CLAB1234'
        :param limit: get N amount of latest events
        :return: [{}, {}, ... ]
        """
        method = "GET"
        if limit:
            path = "storage/allevents/{0}/{1}".format(lab, str(limit))
        else:
            path = "storage/allevents/{0}".format(lab)
        rsp = self._client.request(path, method)
        return rsp

    def take_snapshot(self, lab):
        """Take storage snapshot. Lab can be powered on but snapshot maybe inconsistent.
        :param lab: e.g. 'CLAB1234'
        :return: {'eventID': int}
        """
        method = "POST"
        path = "storage/snapshot/{0}".format(lab)
        rsp = self._client.request(path, method)
        self._events.append(rsp.get('eventID'))
        return rsp

    def revert_to_snapshot(self, snapshot_name, online=True):
        """Revert storage snapshot. Lab must be powered off. If lab is not powered off, an event is successfully created but server will not perform snapshot revert -> event fails.
        :param snapshot_name: e.g. 'CLAB1234-1448007564'
        :param online: Must be true for cloudlabs and vSprints
        :return: {'eventID': int}
        """
        method = "PUT"
        if online:
            path = "storage/snapshot/{0}/online".format(snapshot_name)
        else:
            path = "storage/snapshot/{0}".format(snapshot_name)
        rsp = self._client.request(path, method)
        lab, snapshot_id = snapshot_name.split('-')
        self._events.append(rsp.get('eventID'))
        return rsp

    def delete_snapshot(self, snapshot_name):
        """Delete storage snapshot. Lab power state doesn't matter.
        :param snapshot_name: e.g. 'CLAB1234-1448007564'
        :return: {'eventID': int}
        """
        method = "DELETE"
        path = "storage/snapshot/{0}".format(snapshot_name)
        rsp = self._client.request(path, method)
        self._events.append(rsp.get('eventID'))
        return rsp

    def lock(self, lab):
        """Prevent any storage snapshot operations in lab.
        :param lab: e.g 'CLAB1234'
        :return: {'eventID': int}
        """
        method = "PUT"
        path = "storage/apilock/{0}".format(lab)
        rsp = self._client.request(path, method)
        self._events.append(rsp.get('eventID'))
        return rsp

    def unlock(self, lab):
        """Allow storage snapshot operations in lab.
        :param lab: e.g 'CLAB1234'
        :return: {'eventID': int}
        """
        method = "PUT"
        path = "storage/apiunlock/{0}".format(lab)
        rsp = self._client.request(path, method)
        self._events.append(rsp.get('eventID'))
        return rsp


class WaitEvents():

    def __init__(self, client, timeout=180, event_polling_interval=5, raise_for_failed_events=True):
        """Context manager to wait events.
        usage:
            >>> client = DCSAClient()
            >>> with WaitEvents(client):
            ...   client.take_snapshot('CLAB123')

        :type client: DCSAClient
        :param timeout: <seconds to wait before giving up>
        :param event_polling_interval: <seconds to wait between checking event status>
        :param raise_for_failed_events: True|False

        :raises: TimeOut, RuntimeError
        """
        self.client = client
        self._timeout = timeout
        self._event_polling_interval = event_polling_interval
        self._raise_for_failed_events = raise_for_failed_events

    def __enter__(self):
        return self.client

    def __exit__(self, type, value, traceback):
        events = self.client.events
        try:
            self._wait_until_timeout(events)
        except exceptions.Timeout as e:
            ongoing_events = [str(a) for a in events if self.client.get_event(a)['status'] == "ongoing"]
            raise exceptions.Timeout("{}\nUnfinished events:\n{}".format(e, ", ".join(ongoing_events)))
        failed_events = [str(a) for a in events if self.client.get_event(a)['status'] == "failed"]
        done_events = [str(a) for a in events if self.client.get_event(a)['status'] == "done"]
        log.info("Failed events: {0}/{2}\nSuccessful events: {1}/{2}".format(len(failed_events), len(done_events), len(events)))
        if len(failed_events) > 0 and self._raise_for_failed_events:
            raise RuntimeError("Snapshot event(s) failed! Failed events: {}".format(", ".join(failed_events)))

    def _wait_until_timeout(self, events):
        stime = time.time()
        while (time.time() - stime) <= self._timeout:
            ongoing_events = [a for a in events if self.client.get_event(a).get('status') == "ongoing"]
            if len(ongoing_events) > 0:
                log.info("Waiting for {0}/{1} events to complete ... ".format(len(ongoing_events), len(events)))
                time.sleep(self._event_polling_interval)
            else:
                return
        raise exceptions.Timeout("Storage snapshot event(s) not finished in time ({} seconds)".format(self._timeout))
