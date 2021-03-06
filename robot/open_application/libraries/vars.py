NDAP = 'https://10.131.73.217'
DASHBOARD_URL = NDAP + '/dashboard-view'
TVNF_DEPLOYMENT_NAME = 'TVNFVictor'
LIST__TVNF_DEPLOYMENT_OPTIONS = ['NetAct Fast Pass Test VNF', 'FastPass-TVNF-OpenStack', 'Release 19', '19.0.444']
LIST__TVNF_DEPLOYMENT_INFO = ['fastpass_tvnf_victor', '0', '10.55.76.110:32443', '{"ne_class":"MRBTS","ne_ip":"10.93.245.31","ne_instance":"801","ne_sw":"FL19","ne_type":"MRBTS","mrbts_address":"mrbts-801.netact.com","mrbts_distinguished_name":"PLMN-PLMN/MRBTS-801","ne3sws_agent_security_mode":"0","mrbts_em_address":"10.93.245.31","ne3sws_agent_https_connection_port":"8443","ip_version":"0","sdv_oss_was_dmgr_ip":"10.32.214.236","vm3dn":"clab3417node03.netact.nsn-rdnet.net","omc_password":"omc", "root_password":"arthur", "netact_host":"10.32.214.236","netact_lbwas":"clab3417lbwas.netact.nsn-rdnet.net","dn":"PLMN-PLMN/MRBTS-801","mr":"MRC-MRC/MR-BTSMED","mrc_instance":"MRC-MRC/MR-BTSMED","ne_subclass":"MRBTSA","ne_cell_instance":"1","db_schema":"NOKLTE"}']
LIST__PASSWORDS = ["nemuuser", "scli"]

WORKFLOW_CREATE = 'tvnf_create_modify_instantiate'
CREATE_PARAMETER_NAME_TVNF_NAME = 'xpath://workflow-parameter-renderer/div/div/div[6]/input[2]'
CREATE_PARAMETER_NAME_REPOSITORY = 'xpath://workflow-parameter-renderer/div/div/div[3]/input[2]'
PARAMETER_VALUE_REPOSITORY = 'FastPass-Testing'
WORKFLOW_ONBOARD = 'vnfd_onboard'
ONBOARD_PARAMETER_NAME_REPOSITORY = 'xpath://workflow-parameter-renderer/div/div/div[3]/input[2]'
