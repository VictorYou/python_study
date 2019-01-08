#!/bin/bash
function _start_test_server(){
    STATE_SERVICE_API_DISABLE_TASKS=yes STATE_SERVICE_MONGO_DBNAME=lss_unittest999999 STATE_SERVICE_MONGO_HOST=localhost python server.py -d --4324832948dsa
    ps -ef|grep 'python server.py -d --4324832948dsa'
    local pid
    pid=$(ps -ef|grep 'python server.py -d --4324832948dsa'|grep -v grep|awk '{print $2}')
    echo "Test server started with pid: ${pid}"
}

function _stop_test_server(){
    local pid
    pid=$(ps -ef|grep 'python server.py -d --4324832948dsa'|grep -v grep|awk '{print $2}')
    kill -TERM $pid && echo "Test server with pid: ${pid} stopped"
    ps -ef|grep 'python server.py'
}

function cleanup() {
    find $CURRDIR/src $CURRDIR/unittest $CURRDIR/tests -type f -name "*.py?" | xargs rm -f
    rm -f $CURRDIR/*/testfile_error*.txt $CURRDIR/testfile_error*.txt
}

source start_virtualenv.rc $@
mkdir -p "${WORKSPACE}"/artifacts

cd "${CURRDIR}"/src
unset http_proxy https_proxy no_proxy ftp_proxy
rm -R -f tmp*

packages_to_test=${packages_to_test-api_test client_test dict_builder_test snapshot_tasks_test labrequest_tasks_test ilo_test}
packages_to_cover="api,client,dict_builder,snapshot_tasks,labrequest_tasks,ilo"
_start_test_server

unittests_failed=0
cleanup
set -x
STATE_SERVICE_MONGO_HOST=localhost \
STATE_SERVICE_MONGO_DBNAME=lss_unittest3214329 \
PYTHONPATH="${PYTHONPATH}:${CURRDIR}/unittest:${CURRDIR}/.venv_${JOB_NAME}/lib/python2.7/site-packages/" \
nosetests --exe \
          --with-coverage \
          --cover-package="${packages_to_cover}" \
          --with-xunit \
          --xunit-file="${WORKSPACE}/artifacts/junit_results.xml" \
          --cover-erase \
          --cover-inclusive \
          --cover-html \
          --cover-html-dir "${WORKSPACE}/artifacts/cover" \
          --cover-xml \
          --cover-xml-file "${WORKSPACE}/artifacts/cover/cover.xml" \
          -v \
          ${packages_to_test} \
          || unittests_failed=1
_stop_test_server
cleanup

# if unittests were OK try creation of Pydoc
[ $unittests_failed -eq 0 ] && ${CURRDIR}/create_pydoc.sh
