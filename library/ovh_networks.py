#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    import ovh
except ImportError:
    print "failed=True msg='ovh required for this module'"
    sys.exit(1)

vlan_id=0
# Try to automate this in case the supplied credentials are not valid
def get_credentials():
    """This function is used to obtain an authentication token.
    It should only be called once."""
    client = ovh.Client()
    access_rules = [
        {'method': 'GET', 'path': '/cloud/*'},
        {'method': 'PUT', 'path': '/cloud/*'},
        {'method': 'POST', 'path': '/cloud/*'},
        {'method': 'DELETE', 'path': '/cloud/*'},
    ]
    validation = client.request_consumerkey(access_rules)
    print("Your consumer key is {}".format(validation['consumerKey']))
    print("Please visit {} to validate".format(validation['validationUrl']))


def main():
    module = AnsibleModule(
        argument_spec = dict(
            description = dict(required=True),
            project_name = dict(required=True),
            name = dict(required=True),
            id = dict(required=True),
            state = dict(required=True),
        )
    )

    # Get parameters
    description = module.params.get('description')
    project_name = module.params.get('project_name')
    vlan_name = module.params.get('name')
    vlan_id = module.params.get('id')
    state = module.params.get('state')

    # Connect to OVH API
    client = ovh.Client()

    # Check that the project exists
    projects = client.get('/cloud/project')
    project_exist = False
    for project_id in projects:
        project = client.get('/cloud/project/{}'.format(project_id))
        if description == project['description']:
            project_exist = True
            break


    vracks = client.get('/vrack')
    vrack_exist= False
    if not vracks:
        exit
    else:
        vrack_exist= True
        for vracks_id in vracks:
            vrack_details = client.get('/vrack/{}'.format(vracks_id))
            vrack_id=vracks_id
            break

    # Get project vrack
    try:
        vrackch= client.get('/cloud/project/{}/vrack'.format(project_id))
        attach_vrack=True
    except:
        #print 'except! No vrack attached to project'
        vrackch=''
        attach_vrack=False
        #attack project to vrack
        result = client.post('/vrack/{}/cloudProject'.format(vrack_id), project=project_id)
        task_id=result['id']
        service_name=result['serviceName']
        # Check task status
        time.sleep(40)
        #result = client.get('/vrack/{}/task/{}'.format(vrack_id, task_id))
        #while result['status']!='doing':
        #    result = client.get('/vrack/{}/task/{}'.format(vrack_id, task_id))
        #   print ('attach to vrack status:{}'.format(result['status']))
    stat='OK'
    stat_nok='vLan exist or Error'
    vlan_id2=int(vlan_id)
    # VLAN CREATION
    try:
        vlan = client.post('/cloud/project/{}/network/private'.format(project_id),
         name=vlan_name,
         vlanId=vlan_id2
        )
        module.exit_json(changed=True, vlan=vlan)
    except Exception as ex:
        module.exit_json(changed=False, output=stat_nok)


# import module snippets
from ansible.module_utils.basic import *
main()
