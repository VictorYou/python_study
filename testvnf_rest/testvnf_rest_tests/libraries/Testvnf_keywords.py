#!/bin/env python

#from robot.libraries.BuiltIn import BuiltIn
#import resource
import os

#ROBOT = BuiltIn()


def robot_var(variable):
  return ROBOT.get_variable_value("${%s}" % variable)

class Testvnf_keywords:
  """ Robot Keywords for resource.py

  """

#  ROBOT_LIBRARY_SCOPE = "GLOBAL"

  def testvnf_startup(self):
    testvnf_home = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    db = os.path.join(testvnf_home, 'db.sqlite3')
    print('db file: {}'.format(db))
    os.system('rm -rf {}'.format(db))
    manage_py = os.path.join(testvnf_home, 'manage.py')
    command = 'python3' + ' ' + manage_py + ' ' + 'migrate'
    print("command: {}".format(command))
    os.system(command)
    command = 'python3' + ' ' + manage_py + ' ' + 'runserver' + ' ' +  '0:8000&'
    print("command: {}".format(command))
    os.system(command)
    os.system('sleep 2')


  def testvnf_teardown(self):
    pid = os.popen("ps -ef | grep manage.py | grep -v grep | awk '{print $2}' | sort -n | tail -1").read().strip()
    command = 'kill -9 ' + pid
    print "command: {}".format(command)
    os.system(command)
