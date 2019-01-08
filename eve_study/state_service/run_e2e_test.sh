#!/bin/bash
declare -r CURRDIR="$( cd $(dirname $0) ; pwd)"
test -n "${JOB_NAME}" || export JOB_NAME=$(whoami)
test -n "${WORKSPACE}" || export WORKSPACE="$(dirname ${CURRDIR})"
mkdir -p "${WORKSPACE}"/artifacts
virtualenv --python=python3 "${CURRDIR}/.venv_e2e_test_${JOB_NAME}" ||exit 1
source "${CURRDIR}/.venv_e2e_test_${JOB_NAME}/bin/activate" ||exit 1
cd "${CURRDIR}"/tests
pip install -r test_requirements.txt ||exit 1
unset http_proxy
unset HTTP_PROXY
robot lab_test_robot.robot
