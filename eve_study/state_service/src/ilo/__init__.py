'''module for powering ESXi servers in SprintLab on/off.

Background:
- DCAPI does not (yet) support the automatical retrieval of access data for physical ESXi servers used in Sprintlabs
- DCAP neither supports the shutdown or starting of physical ESXi servers

This module provides support for this missing DCAPI functionality. It is meant as temporary solution until such support
is added to DCAPI. The assumption is that ESXi servers are HPUX servers with management servers supporting HP ILO (=HP Integrated Lights-Out).

Since migrating lab (data) from DCAPI does not fetch any acess data for the ILO servers, such data is provided "hardcoded" in the module
'ilo.sprintlabs'. In case you use a SprintLab NOT listed there, this module has to be updated.
'''

import re

from ilo.ilo_connect import new_ssh_connection 
from ilo.ilo_power import power, power_on, power_off, power_lab_ilos_onoff
from ilo.sprintlabs_data import SPRINTLABS

__all__= [
    'new_ssh_connection',
    'power', 'power_on', 'power_off', 'power_lab_ilos_onoff',
    'SPRINTLABS', 
]
