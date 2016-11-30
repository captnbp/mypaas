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
        required: false
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

try:
    import ovh
except importerror:
    print "failed=true msg='ovh required for this module'"
    sys.exit(1)

# TODO: Try to automate this in case the supplied credentials are not valid
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
            name = dict(required=False),
            project_name = dict(required=True),
            description = dict(required=False),
            state = dict(default='present', choices=['present', 'absent', 'reset']),
        )
    )

    # Get parameters
    name = module.params.get('name')
    project_name = module.params.get('project_name')
    description = module.params.get('description')
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

    # Remove a user
    if state == 'absent':
        if not user_exist: 
            module.exit_json(changed=False)
        elif user_exist: 
            # Remove the user
            client.delete('/cloud/project/{}/user/{}'.format(project_id, user['id']))
            module.exit_json(changed=True)

    # Add / modify a user (modify doesn't handle region update)
    if state == 'present':
        if not description and name:
            description = name
        if not user_exist:
            newuser = client.post('/cloud/project/{}/user'.format(project_id), description=description)
            module.exit_json(changed=True, user=newuser)
        elif user_exist:
            module.exit_json(changed=False, user=user)

    if state == 'reset':
        if not user_exist: 
            module.exit_json(changed=False)
        elif user_exist: 
            newuser = client.post('/cloud/project/{}/user/{}/regeneratePassword'.format(project_id, user['id']))
            module.exit_json(changed=True, user=newuser)

# import module snippets
from ansible.module_utils.basic import *

main()
