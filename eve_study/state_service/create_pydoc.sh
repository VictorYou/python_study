#!/bin/sh

if [ "${1}" == 'rebuild' ]
then 
	source $(dirname $0)/start_virtualenv.rc rebuild
	shift
else
	source $(dirname $0)/start_virtualenv.rc
fi

export PYTHONPATH=../src:$PYTHONPATH
export PYDOC_RUN='yes'

set -x
[ -d pydoc ] || mkdir pydoc
cd pydoc || exit 255
set +x
rm -f *.html

modules="
client client.__main__ client.admin client.info client.lab_request client.config_change client.testing_support
client.command_line_parser client.rest_client client.utils client.globals client.dict_builder
server
api settings
dcapi dcstorage
ilo ilo.ilo_connect ilo.ilo_power ilo.sprintlabs_data
tasks celery_config
labrequest_tasks snapshot_tasks
"

if [ $# -gt 0 ]
then
	pydoc_opts=$@
else
	pydoc_opts='-w'
	do_index='yes'
fi

python -m pydoc $pydoc_opts $modules

if [ ! -z "$do_index" ]
then
cat<<EOF > index.html 
<DOCTYPE html>
<html>
<head><title>LSS pydoc information</title></head>
<body>
<table>
EOF

for entry in client server api dcapi dcstorage ilo tasks celery_config labrequest_tasks snapshot_tasks
do
	echo "<tr><td>${entry}</td><td><a href=\"${entry}.html\">${entry}</a></td></tr>" >> index.html
done

cat<<EOF >> index.html
</table>
</body>
</html>
EOF
fi
