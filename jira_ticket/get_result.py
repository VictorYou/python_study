import argparse
import csv
import http.cookiejar
import inspect
import logging
import os
import re
import ssl
import sys
import urllib

sys.path.append("../common")

from log import log
from datetime import datetime, timedelta
from dbconnector import DBConnector, LocalTimeZone
from urllib.request import HTTPCookieProcessor, build_opener


class JiraResult():
  result_file = 'result.csv'

  def __init__(self):
    cj = http.cookiejar.CookieJar()
    self._opener = build_opener(HTTPCookieProcessor(cj))
    self._opener.addheaders = [('User-agent','Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3'), ('Referer', "/")]
    ssl._create_default_https_context = ssl._create_unverified_context
    data = urllib.parse.urlencode({"os_username": 'viyou',"os_password": 'Yh#%&(!Ss'})
    res = self._opener.open("https://srvjira.int.net.nokia.com/login.jsp", data.encode('ascii', 'ignore'))
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: res: {res.read()}")

  def get(self, begin_date, end_date):
    url = f"https://srvjira.int.net.nokia.com/sr/jira.issueviews:searchrequest-csv-current-fields/temp/SearchRequest.csv?jqlQuery=project+%3D+OSSSUP+AND+created+%3E%3D+{begin_date}+AND+created+%3C%3D+{end_date}+ORDER+BY+key+DESC"
    log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: url: {url}")
    self._response = self._opener.open(url)
    return self
    
  def save(self):
    with open(self.result_file, 'wb') as f:
      f.write(self._response.read())


def main(argv=None):
  week_ago = LocalTimeZone.timezone.localize(datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d')

  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--date-after", dest="date_after", default=f'{week_ago}', help="date after, eg: 2020-04-01")
  args = parser.parse_args()
  date_after = args.date_after
  today = datetime.now().strftime('%Y-%m-%d')
  log.debug(f"{__file__}:{inspect.currentframe().f_lineno}: args: {args}")
  JiraResult().get(args.date_after, today).save()


if __name__ == "__main__":
  sys.exit(main())
