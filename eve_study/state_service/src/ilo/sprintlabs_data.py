#!/usr/bin/python

"""
Provides data for Sprintlabs used by Lab State Service

Currently only list of ESXi servers and their ILO console is configured

- data is a dict 'SPRINTLABS'
- every Spintlab definition contains 'ESXis' and 'dcstorage_auth'
    - 'ESXis' contains a list of tuples for ESXi servers
        - each tuple: (<ESXi IP or name>, <ILO server IP>, <ILO user>, <password for ILO user>)
    - 'dcstorage_auth' defines user of the DCSA (DC Storage API) and its password 

Please note:

In order to work properly the lab names must exacly be the same as the ones used by DCSA!
    - typically they have the form 'SprintLab'<NUMBER>
    - i.e. S and L letters in sprintlab name MUST be upper case and all other letters lower case
"""

SPRINTLABS = dict(
    # lab for testing
    SprintLab99999 = dict(
        ESXis = [
            ('10.91.132.63','10.9.222.51', 'ilouser', 'ilouser1'),
            ('10.91.132.64','10.9.222.51', 'ilouser', 'ilouser1'),
            ('10.91.132.65','10.9.222.51', 'ilouser', 'ilouser1'),
            ('10.91.132.66','10.9.222.51', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\fakelab99999sa' , password = 'passu'),
    ),
    SprintLab218 = dict(
        ESXis = [
            ('10.41.112.134','10.91.12.221', 'ilouser', 'ilouser1'),
            ('10.41.112.135','10.91.12.222', 'ilouser', 'ilouser1'),
            ('10.41.112.136','10.91.12.223', 'ilouser', 'ilouser1'),
            ('10.41.112.137','10.91.12.224', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab218sa' , password = 'LabAcc0unt'),
    ),
   SprintLab279 = dict(
        ESXis = [
            ('10.9.184.212','10.8.96.56', 'ilouser', 'ilouser1'),
            ('10.9.184.213','10.8.96.57', 'ilouser', 'ilouser1'),
            ('10.9.184.214','10.8.96.58', 'ilouser', 'ilouser1'),
            ('10.9.184.215','10.8.96.59', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab279sa' , password = 'LabAcc0unt'),
    ),
    SprintLab283 = dict(
        ESXis = [
            ('10.91.128.136','10.9.243.227', 'ilouser', 'ilouser1'),
            ('10.91.128.137','10.9.243.228', 'ilouser', 'ilouser1'),
            ('10.91.128.138','10.9.243.229', 'ilouser', 'ilouser1'),
            ('10.91.128.139','10.9.243.230', 'ilouser', 'ilouser1'),
            ('10.91.128.140','10.9.243.231', 'ilouser', 'ilouser1'),
            ('10.91.128.141','10.9.243.232', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab283sa' , password = 'LabAcc0unt'),
    ),
    # https://confluence.int.net.nokia.com/display/OSS5MG/Lab+status#Labstatus-VMwareStandard
    SprintLab334 = dict(
        ESXis = [
            ('10.92.91.113','10.41.114.38', 'ilouser', 'ilouser1'),
            ('10.92.91.114','10.41.114.39', 'ilouser', 'ilouser1'),
            ('10.92.91.115','10.41.114.40', 'ilouser', 'ilouser1'),
            ('10.92.91.116','10.41.114.41', 'ilouser', 'ilouser1'),
            ('10.92.91.117','10.41.114.42', 'ilouser', 'ilouser1'),
            ('10.92.91.118','10.41.114.43', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab334sa' , password = 'LabAcc0unt'),
    ),
    SprintLab358 = dict(
        ESXis = [
            ('10.91.76.56','10.91.13.8', 'ilouser', 'ilouser1'),
            ('10.91.76.57','10.91.13.9', 'ilouser', 'ilouser1'),
            ('10.91.76.58','10.91.13.10', 'ilouser', 'ilouser1'),
            ('10.91.76.59','10.91.13.11', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab358sa' , password = 'LabAcc0unt'),
    ),
    SprintLab367 = dict(
        ESXis = [
            ('10.91.78.1','10.91.14.8', 'ilouser', 'ilouser1'),
            ('10.91.78.2','10.91.14.9', 'ilouser', 'ilouser1'),
            ('10.91.78.3','10.91.14.16', 'ilouser', 'ilouser1'),
            ('10.91.78.4','10.91.14.17', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab367sa' , password = 'LabAcc0unt'),
    ),
    SprintLab371 = dict(
        ESXis = [
            ('10.91.79.1','10.91.14.24', 'ilouser', 'ilouser1'),
            ('10.91.79.2','10.91.14.25', 'ilouser', 'ilouser1'),
            ('10.91.79.3','10.91.14.26', 'ilouser', 'ilouser1'),
            ('10.91.79.4','10.91.14.27', 'ilouser', 'ilouser1'),
            ('10.91.79.5','10.91.14.28', 'ilouser', 'ilouser1'),
            ('10.91.79.6','10.91.14.29', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab371sa' , password = 'LabAcc0unt'),
    ),
    SprintLab391 = dict(
        ESXis = [
            ('10.92.232.87','10.8.96.127', 'ilouser', 'ilouser1'),
            ('10.92.232.88','10.8.96.128', 'ilouser', 'ilouser1'),
            ('10.92.232.89','10.8.96.129', 'ilouser', 'ilouser1'),
            ('10.92.232.90','10.8.96.130', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab391sa' , password = 'LabAcc0unt'),
    ),	
    SprintLab417 = dict(
        ESXis = [
            ('10.91.110.110','10.91.15.150', 'ilouser', 'ilouser1'),
            ('10.91.110.111','10.91.15.151', 'ilouser', 'ilouser1'),
            ('10.91.110.112','10.91.15.152', 'ilouser', 'ilouser1'),
            ('10.91.110.113','10.91.15.153', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab417sa' , password = 'LabAcc0unt'),
    ),
    SprintLab440 = dict(
        ESXis = [
            ('10.91.132.63','10.41.114.64', 'ilouser', 'ilouser1'),
            ('10.91.132.64','10.41.114.65', 'ilouser', 'ilouser1'),
            ('10.91.132.65','10.41.114.66', 'ilouser', 'ilouser1'),
            ('10.91.132.66','10.41.114.67', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab440sa' , password = 'LabAcc0unt'),
    ),
    SprintLab441 = dict(
        ESXis = [
            ('10.91.213.137','10.91.168.34', 'ilouser', 'ilouser1'),
            ('10.91.213.138','10.91.168.35', 'ilouser', 'ilouser1'),
            ('10.91.213.139','10.91.168.36', 'ilouser', 'ilouser1'),
            ('10.91.213.140','10.91.168.42', 'ilouser', 'ilouser1'),
            ('10.91.213.141','10.91.168.43', 'ilouser', 'ilouser1'),
            ('10.91.213.142','10.91.168.44', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab441sa' , password = 'LabAcc0unt'),
    ),
    SprintLab446 = dict(
        ESXis = [
            ('10.91.133.9','10.91.168.66', 'ilouser', 'ilouser1'),
            ('10.91.133.10','10.91.168.67', 'ilouser', 'ilouser1'),
            ('10.91.133.11','10.91.168.68', 'ilouser', 'ilouser1'),
            ('10.91.133.12','10.91.168.69', 'ilouser', 'ilouser1'),
            ('10.91.133.13','10.91.168.70', 'ilouser', 'ilouser1'),
            ('10.91.133.14','10.91.168.71', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab446sa' , password = 'LabAcc0unt'),
    ),
    SprintLab467 = dict(
        ESXis = [
            ('10.91.137.155','10.91.168.224', 'ilouser', 'ilouser1'),
            ('10.91.137.156','10.91.168.225', 'ilouser', 'ilouser1'),
            ('10.91.137.157','10.91.168.226', 'ilouser', 'ilouser1'),
            ('10.91.137.158','10.91.168.227', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab467sa' , password = 'LabAcc0unt'),
    ),
    SprintLab473 = dict(
        ESXis = [
            ('10.91.139.144','10.41.114.34', 'ilouser', 'ilouser1'),
            ('10.91.139.145','10.41.114.35', 'ilouser', 'ilouser1'),
            ('10.91.139.146','10.41.114.36', 'ilouser', 'ilouser1'),
            ('10.91.139.147','10.41.114.37', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab473sa' , password = 'LabAcc0unt'),
    ),
    SprintLab493 = dict(
        ESXis = [
            ('10.91.143.93','10.92.32.122', 'ilouser', 'ilouser1'),
            ('10.91.143.94','10.92.32.123', 'ilouser', 'ilouser1'),
            ('10.91.143.95','10.92.32.124', 'ilouser', 'ilouser1'),
            ('10.91.143.96','10.92.32.125', 'ilouser', 'ilouser1'),
            ('10.91.143.97','10.92.32.126', 'ilouser', 'ilouser1'),
            ('10.91.143.98','10.92.32.127', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab493sa' , password = 'LabAcc0unt'),
    ),
    SprintLab500 = dict(
        ESXis = [
            ('10.92.82.201','10.92.32.192', 'ilouser', 'ilouser1'),
            ('10.92.82.202','10.92.32.193', 'ilouser', 'ilouser1'),
            ('10.92.82.203','10.92.32.194', 'ilouser', 'ilouser1'),
            ('10.92.82.204','10.92.32.195', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab500sa' , password = 'LabAcc0unt'),
    ),
    SprintLab501 = dict(
        ESXis = [
            ('10.92.83.19','10.92.32.196', 'ilouser', 'ilouser1'),
            ('10.92.83.20','10.92.32.197', 'ilouser', 'ilouser1'),
            ('10.92.83.21','10.92.32.198', 'ilouser', 'ilouser1'),
            ('10.92.83.22','10.92.32.199', 'ilouser', 'ilouser1'),
        ],
        dcstorage_auth = dict( user = 'NSLE\\sprintlab501sa' , password = 'LabAcc0unt'),
    ),
) 
