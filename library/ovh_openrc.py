#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ovh_dns, an Ansible module for managing OVH DNS records
# Copyright (C) 2014, Carlos Izquierdo <gheesh@gheesh.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

DOCUMENTATION = '''
---
module: ovh_user
author: Benoît Pourre
short_description: Manage OVH Cloud users
description:
    - Manage OVH (French European hosting provider) Cloud users
requirements: [ "ovh" ]
options:
    name:
        required: fasle
        description:
            - Container name
    project_name:
        required: true
        description:
            - OVH Cloud Project description / name
    description:
        required: false
        description:
            - Project's user's description. We will use it to identify the user.
    region:
        required: true
        description:
            - Project's region.
    state:
        required: false
        default: present
        choices: ['present', 'absent', 'reset']
        description:
            - Determines wether the user is to be created or deleted, or password reset
'''

EXAMPLES = '''
'''

import os
import sys
import json

try:
    import ovh
except importerror:
    print "failed=true msg='ovh required for this module'"
    sys.exit(1)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(required=False),
            project_name = dict(required=True),
            description = dict(required=False),
            region = dict(required=True),
            state = dict(default='present', choices=['present', 'absent', 'reset']),
        )
    )

    # Get parameters
    name = module.params.get('name')
    project_name = module.params.get('project_name')
    description = module.params.get('description')
    region = module.params.get('region')
    state = module.params.get('state')

    # Connect to OVH API
    client = ovh.Client()

    # Check that the project exists and get its id
    projects = client.get('/cloud/project')
    project_exist = False
    for project_id in projects:
        project = client.get('/cloud/project/{}'.format(project_id))
        if project_name == project['description']:
            project_exist = True
            break
    if not project_exist:
        module.fail_json(msg='Project {} does not exist'.format(project))
	
    # Check if the user exists
    users = client.get('/cloud/project/{}/user'.format(project_id))
    user_exist = False
    for user in users:
        if name == user['username']:
            user_exist = True
            break
        elif description == user['description']:
            user_exist = True
            break
    if user_exist:
        openrc = client.get('/cloud/project/{}/user/{}/openrc'.format(project_id,user['id']), region=region )
        os_auth_url = re.search('export OS_AUTH_URL=(.*)\n', openrc['content'], re.IGNORECASE).group(1)
        os_tenant_id = re.search('export OS_TENANT_ID=(.*)\n', openrc['content'], re.IGNORECASE).group(1)
        os_tenant_name = re.search('export OS_TENANT_NAME=\"(.*)\"\n', openrc['content'], re.IGNORECASE).group(1)
        os_username = re.search('export OS_USERNAME=\"(.*)\"\n', openrc['content'], re.IGNORECASE).group(1)
        os_region = re.search('export OS_REGION_NAME=\"(.*)\"\n', openrc['content'], re.IGNORECASE).group(1)
        module.exit_json(changed=False, openrc={ 'os_auth_url': os_auth_url, 'os_tenant_id': os_tenant_id, 'os_tenant_name': os_tenant_name, 'os_username': os_username, 'os_region': os_region })
    else:
        module.fail_json(msg="User {} with description {} not found".format(name, description))

# import module snippets
from ansible.module_utils.basic import *

main()
