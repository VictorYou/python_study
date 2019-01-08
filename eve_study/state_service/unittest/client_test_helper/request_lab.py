'''

'''
# TODO re-factor unit tests and this helper too

REQUEST_LAB_WAIT_FOR_FREE_SUCCESS = dict(
keepalive = [
# R2 -- PATCH 'labrequests/5b6aa1f6794b4c00013c31de/keepalive'
{"_updated": "Wed, 08 Aug 2018 07:55:34 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de/keepalive/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "ccb45ed54900545e5b2d443fee559362c6a051c3"},

],
responses = [
# R0 -- POST 'labrequests' url: 'http://ss:8000/labrequests' request: '{"username": "tester1", "state_search_query": "{\"build.id\":\"test0020\"}", "message": "VALID"}'
{"_updated": "Wed, 08 Aug 2018 07:55:34 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "057cdf2685fa3441e4c85679962534165cd7d6d4"},

# R1 -- GET 'labrequests' request: 'http://ss:8000/labrequests/5b6aa1f6794b4c00013c31de
{"username": "tester1", "status": "pending", "_updated": "Wed, 08 Aug 2018 07:55:34 GMT", "expireAt": "Wed, 08 Aug 2018 07:56:34 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"test0020\"}", "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "message": "VALID", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "efe1f339a8701f261966f2bad7547a4178cbe986"},

### R2 -- PATCH 'labrequests/5b6aa1f6794b4c00013c31de/keepalive'
##{"_updated": "Wed, 08 Aug 2018 07:55:34 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de/keepalive/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "ccb45ed54900545e5b2d443fee559362c6a051c3"},

# R3: LOOP -- GET 'labrequests' request: 'http://ss:8000/labrequests/5b6aa1f6794b4c00013c31de
{"username": "tester1", "status": "no_lab_available", "_updated": "Wed, 08 Aug 2018 07:55:36 GMT", "expireAt": "Wed, 08 Aug 2018 07:56:34 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"test0020\"}", "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "message": "VALID", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "b01404152923e6d2f941bf1d7f731ee5161cedbe"},
 
{"username": "tester1", "status": "no_lab_available", "_updated": "Wed, 08 Aug 2018 07:55:36 GMT", "expireAt": "Wed, 08 Aug 2018 07:56:34 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"test0020\"}", "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "message": "VALID", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "b01404152923e6d2f941bf1d7f731ee5161cedbe"},
 
###           -- PATCH 'labrequests/5b6aa1f6794b4c00013c31de/keepalive'
##{"_updated": "Wed, 08 Aug 2018 07:55:36 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de/keepalive/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "eb6cb15c4e957e4fb1e633de5304de5aa73624d0"},

# R4 -- GET 'labrequests' request: 'http://ss:8000/labrequests/5b6aa1f6794b4c00013c31de
{"username": "tester1", "status": "ready", "_updated": "Wed, 08 Aug 2018 07:55:44 GMT", "expireAt": "Wed, 08 Aug 2018 07:56:43 GMT", "lab_reservation_time": "60", "lab": "5b6a9155794b4c00013c31cf", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"test0020\"}", "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "message": "VALID", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "96ac9e6e8b4cff34f7b8cc28b7eb05aa8740a904"},

# R5 -- GET 'labs' request: 'http://ss:8000/labs/5b6a9155794b4c00013c31cf
{"status": "queued_for_revert", "_updated": "Wed, 08 Aug 2018 07:55:44 GMT", "previously_reverted_state": "5b6a9155794b4c00013c31d0", "lab_type": "vosp", "states": ["5b6a9155794b4c00013c31d0", "5b6a9155794b4c00013c31d1", "5b6a9155794b4c00013c31d2"], "lab_name": "vOSP0020", "_links": {"self": {"href": "labs/5b6a9155794b4c00013c31cf", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "5b6aa200794b4c00013c31df", "_created": "Wed, 08 Aug 2018 06:44:37 GMT", "_id": "5b6a9155794b4c00013c31cf", "_etag": "582ab0514ca9fd5f7fedee5797598603a0e8bce3"},

###           -- PATCH 'labrequests/5b6aa1f6794b4c00013c31de/keepalive'
##{"_updated": "Wed, 08 Aug 2018 07:55:45 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de/keepalive/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "3c1e4bcb47d20f0599b17cf3a3326b510a385809"},

# R6: LOOP
{"status": "reverting_state", "_updated": "Wed, 08 Aug 2018 07:55:46 GMT", "previously_reverted_state": "5b6a9155794b4c00013c31d0", "lab_type": "vosp", "states": ["5b6a9155794b4c00013c31d0", "5b6a9155794b4c00013c31d1", "5b6a9155794b4c00013c31d2"], "lab_name": "vOSP0020", "_links": {"self": {"href": "labs/5b6a9155794b4c00013c31cf", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "5b6aa200794b4c00013c31df", "_created": "Wed, 08 Aug 2018 06:44:37 GMT", "_id": "5b6a9155794b4c00013c31cf", "_etag": "a4c2b18b25b8bb2dfd4d6c393deae1eb392ca03e"},

###           -- PATCH 'labrequests/5b6aa1f6794b4c00013c31de/keepalive'
##{"_updated": "Wed, 08 Aug 2018 07:55:47 GMT", "_links": {"self": {"href": "labrequests/5b6aa1f6794b4c00013c31de/keepalive/5b6aa1f6794b4c00013c31de", "title": "Labrequest"}}, "_created": "Wed, 08 Aug 2018 07:55:34 GMT", "_status": "OK", "_id": "5b6aa1f6794b4c00013c31de", "_etag": "65c47c7e4d425d6adb92683dcbfd0f1b34b1390f"},

# R7 -- GET 'labs' request: 'http://ss:8000/labs/5b6a9155794b4c00013c31cf
{"status": "ready", "_updated": "Wed, 08 Aug 2018 07:56:16 GMT", "previously_reverted_state": "5b6a9155794b4c00013c31d0", "lab_type": "vosp", "states": ["5b6a9155794b4c00013c31d0", "5b6a9155794b4c00013c31d1", "5b6a9155794b4c00013c31d2"], "lab_name": "vOSP0020", "_links": {"self": {"href": "labs/5b6a9155794b4c00013c31cf", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "5b6aa200794b4c00013c31df", "_created": "Wed, 08 Aug 2018 06:44:37 GMT", "_id": "5b6a9155794b4c00013c31cf", "_etag": "b1bff5b21c289f28761cd738645f3353c42fcc54"},

])
