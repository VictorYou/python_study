import csv
import sys

class JiraTicket():
  jql = 'https://srvjira.int.net.nokia.com/issues/?jql=project%20%3D%20OSSSUP%20AND%20created%20%3E%3D%20-52w'
  def __init__(self):
    pass

class TicketReader():
  def __init__(self, result_file):
    self.file = result_file

  def reporter(self):
    reporters = []
    with open(self.file) as f:
      f_csv = csv.DictReader(f)
      for r in f_csv:
        reporters.append(r['Reporter'])
    reporters = list(set(reporters))
    reporters.sort()
    return ','.join(reporters)  

def main(argv=None):
  print(TicketReader('result.csv').reporter())


if __name__ == "__main__":
  sys.exit(main())
