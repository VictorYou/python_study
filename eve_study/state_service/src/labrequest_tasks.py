'''Definition of Celery task for handling lab requests
'''
from tasks import app
from celery.utils.log import get_task_logger
import requests
import time
import datetime
import os
import logging

log = get_task_logger(__name__)
log.setLevel(logging.DEBUG)

STATE_REST_API_URL = "http://web:8000"
FINAL_LAB_STATES = ['ready', 'state_operation_failed']

if os.getenv('PYDOC_RUN') is None:
    @app.task(bind=True)
    def process_labrequests(self):
        log.info("**** Request {0}: process_labrequests starts ****".format(self.request.id))
        labrequests_sorted = _get_open_labrequests()
        log.debug('OPEN LAB REQUESTS: #: %u - %s' % (len(labrequests_sorted), labrequests_sorted))
        for labrequest in labrequests_sorted:
            try:
                LabrequestProcessor(labrequest).process_labrequest()
            except Exception as e:
                log.exception(e)
                log.error("Processing failed for labrequest {}. Check above traceback for details.".format(labrequest['_id']))
                try:
                    _update_labrequest(labrequest, status="error")
                except Exception as e:
                    log.exception(e)
                    log.error(
                        "Could not update labrequest {} status to \"error\". Check above traceback for details.".format(labrequest['_id']))
        log.info("**** Request {0}: process_labrequests ends ****".format(self.request.id))

class LabrequestProcessor(object):
    def __init__(self, labrequest):
        self.labrequest = labrequest
        self.potential_state_ids = None

    def process_labrequest(self):
        if not self._ensure_there_is_no_reservation_with_same_tag():
            log.warning('tag already used')
            return
        reservation = self._reserve_matching_lab()
        if reservation:
            my_lab_id = reservation['lab']
            status = None
            try:
                state = self._get_correct_state(my_lab_id)
                log.info('process_labrequest: state of %s is %s' % (my_lab_id, state))
                status = "ready"
                _update_labrequest(self.labrequest, lab=my_lab_id, status=status)
                _trigger_revert(state)
            except Exception as e:
                log.error(e)
                status = "error"
                raise
            finally:
                _update_labrequest(self.labrequest, lab=my_lab_id, status=status)

    def _get_correct_state(self, my_lab):
        where = '{{"lab": "{0}"}}'.format(my_lab)
        my_lab_states = _get_all_resource_items('states', where=where)
        my_lab_state_ids = [a['_id'] for a in my_lab_states]
        states = set(self.potential_state_ids).intersection(set(my_lab_state_ids))
        state = states.pop()
        return state

    def _reserve_matching_lab(self):
        ''' reserve lab matching the query criteria of this request '''
        lab_ids = self._find_matching_labs()
        log.debug('FOUND matching lab ids: %s', lab_ids)
        for lab_id in lab_ids:
            log.debug('''calling _reserve_lab_if_available(_get_item('labs', lab_id=%s))''' % (lab_id))
            reservation = self._reserve_lab_if_available(_get_item('labs', lab_id))
            if reservation:
                log.debug('_reserve_matching_lab(): %s', reservation)
                return reservation
        if lab_ids:
            _update_labrequest(self.labrequest, status="no_lab_available")

    def _find_matching_labs(self):
        '''
            checks for query and lab query criteria. 
            If no lab matches the criteria the labrequest state will be set to either 'no_matching_state' or 'no_matching_lab'.
            Otherwise, if all matching labs are reserved labrequest state will be 'no_free_lab'.
            Return value will be list of free labs matching both search criteria.
        '''
        matching_states = _get_all_resource_items('states', where=self.labrequest['state_search_query'])
        log.debug('matching_states: %s' % (matching_states))
        if matching_states == []:
            log.warning("No state in any lab matches the search criteria")
            _update_labrequest(self.labrequest, status="no_matching_state")
            return []
        matching_lab_states = [(state['_id'], state['lab'], state.get("snapshot_status") == "available") 
            for state in matching_states]
        log.debug('matching_lab_states: %s' % (matching_lab_states))

        matching_lab_states = self._filter_with_lab_query(matching_lab_states)
        # diff b/w not matching query and unavailable lab
        error_status = "no_matching_state" if matching_lab_states == [] else "no_lab_available"
        available_lab_states = filter(lambda (state_id, lab_id, avail) : avail == True, matching_lab_states)
        log.debug('available_lab_states: %s' % (available_lab_states))
        if not available_lab_states:
            log.info("No matching/available state: status=%s" % (error_status))
            _update_labrequest(self.labrequest, status=error_status)
            return []
        self.potential_state_ids = [state_id for (state_id, lab_id, avail) in available_lab_states]
        log.debug('potential_state_ids: %s' % (self.potential_state_ids))
        return [lab_id for (state_id, lab_id, avail) in available_lab_states]

    def _filter_with_lab_query(self, lab_states):
        filtered_lab_states = lab_states
        if self.labrequest.get('lab_search_query'):
            matching_lab_ids = [lab['_id'] for lab in _get_all_resource_items('labs', where=self.labrequest.get('lab_search_query'))]
            filtered_lab_states = filter(lambda (state_id, lab_id, avail) : lab_id in matching_lab_ids, lab_states)
            log.debug('filtered_lab_states; %s' % (filtered_lab_states))
            if len(filtered_lab_states) == 0:
                _update_labrequest(self.labrequest, status="no_matching_lab")
        return filtered_lab_states

    def _reserve_lab_if_available(self, lab):
        ''' reserve this lab if it is available '''
        lab_data = lab
        log.debug('_reserve_lab_if_available(): lab_data: %s', lab_data)
        reservation_id, reservation = self._get_valid_labreservation(lab_data)
        log.debug('_reserve_lab_if_available(): existing reservation_id: %s reservation: %s', reservation_id, reservation)
        lab_status = lab_data.get('status')
        if not reservation_id:
            if lab_status in FINAL_LAB_STATES:
                log.debug('_reserve_lab_if_available(): reserving lab w/ id=%s' % (lab_data.get('_id', 'ID not set')))
                return self._create_lab_reservation(lab_id=lab_data['_id'])
            log.debug('No lab reservation, neither lab status is in final state')
        elif self.labrequest.get('_id') == reservation.get('labrequest_id'):
            # if reservation was done from this requests, return the exiting reservation
            #  this is a WA for race conditions
            log.warning('Reservation found that contains the same tag (%s) as this reservation request ID', reservation['labrequest_id']) 
            return reservation

    def _ensure_there_is_no_reservation_with_same_tag(self):
        items = _get_all_resource_items('reservations', where='{"tag":"%s"}' % self.labrequest.get('tag'))
        if len(items) > 0:
            log.debug('self: %s: reservation items w/ same tag: %s', self, items)
            _update_labrequest(self.labrequest, lab=items[0].get('lab'), status='ready')
            return False
        return True

    def _get_valid_labreservation(self, lab_data):
        ''' checks whether valid reservation exists for lab_data '''
        reservation_id = lab_data.get('reservation')
        if not reservation_id:
            return None, None
        try:
            reservation = _get_item('reservations', reservation_id)
        except requests.exceptions.HTTPError as ex:
            log.warning('Lab reservation entry exists, but no valid lab reservation: %s ERROR: %s', reservation_id, ex)
            return None, None
        if reservation:
            log.debug('Valid lab reservation found: %s', reservation)
            return reservation_id, reservation
        return None, None
 
    def _create_lab_reservation(self, lab_id):
        ''' create new lab reservation object for lab_id '''
        data = {"lab": lab_id,
                "username": self.labrequest['username'],
                "message": self.labrequest['message'],
                'labrequest_id': str(self.labrequest.get('_id', '')),
                }
        self._set_lab_reservation_duration(data)
        self._set_lab_reservation_tag(data)

        # labrequest.reservation_time -> expireAt somehow
        log.debug('_create_lab_reservation(): self.labrequest: %s' % (self.labrequest))
        response = _post_resource('reservations', data)
        new_reservation = _get_item('reservations', response['_id'])
        return new_reservation

    def _set_lab_reservation_duration(self, reservation_data):
        duration = self.labrequest['lab_reservation_time']
        if duration:
            reservation_data['duration'] = duration
            seconds = int(duration)
            reservation_data["expireAt"] = datetime.datetime.strftime(
                    (datetime.datetime.utcnow() + datetime.timedelta(seconds = seconds)), 
                    '%a, %d %b %Y %H:%M:%S GMT'
                )
        else:
            log.debug('no duration provided for lab reservation')

    def _set_lab_reservation_tag(self, reservation_data):
        tag = self.labrequest.get('tag')
        if tag is not None:
            reservation_data['tag'] = tag
        else:
            log.debug('no tag provided for lab reservation')

def _update_labrequest(labrequest, lab=None, status=None, max_retries=20):
    # TODO : add status_message for more info about status
    log.debug('_update_labrequest(labrequest=%s, lab=%s, status=%s, max_retries=%u)' % (labrequest, lab, status, max_retries))
    patch_data = {}
    if lab:
        patch_data.update({'lab': lab})
    if status:
        patch_data.update({'status': status})
    retries = 1
    while retries <= max_retries:
        try:
            log.info("Updating labrequest with %s [%u/%u]" % (patch_data, retries, max_retries))
            _patch_item('labrequests', labrequest['_id'], patch_data, labrequest['_etag'])
            break
        except requests.HTTPError as e:
            if "PRECONDITION FAILED" in e.message:
                log.warning("Retrying {0}/{1} due to {2}".format(retries, max_retries, e.message))
                time.sleep(0.01)
            else:
                raise
        retries += 1
        labrequest = _get_item('labrequests', labrequest['_id'])


def _trigger_revert(state_id):
    url = STATE_REST_API_URL + "/states/{}/revert".format(state_id)
    log.info("Trigger revert for {}".format(state_id))
    response = requests.patch(url)
    log.info("PATCH states/{0}/revert response: {1}".format(state_id, response.text))
    log.debug('_trigger_revert(state_id=%s) response for patch: %s' % (state_id, response))
    response.raise_for_status()
    return response


def _get_open_labrequests():
    """Returns open labrequest in order, oldest first.

    *open: 'status' != 'ready' && 'status' != 'failed'
    """
    oldest_first = "_created"
    status_open = '{"$and":[{"status":{"$ne":"ready"}},{"status":{"$ne":"failed"}}]}'
    return _get_all_resource_items('labrequests', sort=oldest_first, where=status_open)


def _get_all_resource_items(resource, all_pages=True, **url_params):
    resource_data = _get_resource(resource, **url_params)
    if all_pages and '_links' in resource_data:
        items = _get_pages(resource_data['_links'], resource_data['_items'])
    else:
        items = resource_data['_items']
    return items


def _get_pages(links, items):
    if 'next' in links:
        page_href = links['next']['href']
        page = _get_href(page_href)
        page_items = page['_items']
        items += page_items
        _get_pages(page['_links'], items)
    return items


def _get_href(href, **params):
    get_url = STATE_REST_API_URL + "/{0}".format(href)
    response = requests.get(get_url, params=params)
    log.info("GET {0} response: {1}".format(href, response.text))
    response.raise_for_status()
    return response.json()


def _get_resource(resource, **params):
    get_url = STATE_REST_API_URL + "/{0}/".format(resource)
    response = requests.get(get_url, params=params)
    log.info("GET {0} response: {1}".format(resource, response.text))
    response.raise_for_status()
    return response.json()


def _get_item(resource, _id, **params):
    get_url = STATE_REST_API_URL + "/{0}/{1}".format(resource, _id)
    response = requests.get(get_url, params=params)
    log.info("GET {0} response: {1}".format(resource, response.text))
    response.raise_for_status()
    return response.json()


def _patch_item(resource, _id, data, etag, **params):
    url = STATE_REST_API_URL + "/{0}/{1}".format(resource, _id)
    headers = {'If-Match': etag}
    response = requests.patch(url, json=data, headers=headers, params=params)
    log.info("PATCH {0} response: {1}".format(resource, response.text))
    response.raise_for_status()
    return response.json()


def _post_resource(resource, data, **params):
    log.debug('_post_resource')
    url = STATE_REST_API_URL + "/{0}".format(resource)
    response = requests.post(url, json=data, params=params)
    log.info("POST {0} response: {1}".format(resource, response.text))
    response.raise_for_status()
    return response.json()
