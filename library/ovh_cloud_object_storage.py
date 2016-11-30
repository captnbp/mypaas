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
module: ovh_public_key
author: Benoît Pourre
short_description: Manage OVH Cloud Container Object Storage
description:
    - Manage OVH (French European hosting provider) Cloud Container Object Storage
requirements: [ "ovh" ]
options:
    name:
        required: true
        description:
            - Container name
    project_name:
        required: true
        description:
            - OVH Cloud Project description / name
    region:
        required: true
        description:
            - Region to create the container
    state:
        required: false
        default: present
        choices: ['present', 'absent']
        description:
            - Determines wether the public key is to be created or deleted
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
            name = dict(required=True),
            project_name = dict(required=True),
            region = dict(required=True),
            state = dict(default='present', choices=['present', 'absent']),
        )
    )

    # Get parameters
    name = module.params.get('name')
    project_name = module.params.get('project_name')
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
	
    # Check if the storage exists
    storages = client.get('/cloud/project/{}/storage'.format(project_id))
    storage_exist = False
    storage_same_region = False
    for storage in storages:
        if name == storage['name']:
            storage_exist = True
            if region == storage['region']:
                storage_same_region = True
                break
            else:
                break

    # Remove a storage
    if state == 'absent':
        if not storage_exist and not storage_same_region:
            module.exit_json(changed=False)
        elif storage_exist and storage_same_region:
            # Remove the storage
            client.delete('/cloud/project/{}/storage/{}'.format(project_id, storage['id']))
            module.exit_json(changed=True)

    # Add / modify a storage (modify doesn't handle region update)
    if state == 'present':
        if not storage_exist:
            client.post('/cloud/project/{}/storage'.format(project_id), containerName=name, region=region)
            module.exit_json(changed=True)
        elif storage_exist and not storage_same_region:
            client.post('/cloud/project/{}/storage'.format(project_id), containerName=name, region=region)
            module.exit_json(changed=True)
        elif storage_exist and storage_same_region:
            module.exit_json(changed=False)

# import module snippets
from ansible.module_utils.basic import *

main()
