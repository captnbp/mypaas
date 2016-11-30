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
short_description: Manage OVH Cloud volumes
description:
    - Manage OVH (French European hosting provider) Cloud volumes
requirements: [ "ovh" ]
options:
    name:
        required: true
        description:
            - SSH key name
    project_name:
        required: true
        description:
            - OVH Cloud Project description
    publicKey:
        required: false
        description:
            - SSH public key
    region:
        required: false
        default: None
        description:
            - Region to create SSH key
    state:
        required: false
        default: present
        choices: ['present', 'absent']
        description:
            - Determines wether the public key is to be created or deleted
'''

EXAMPLES = '''
# Create a typical A record
- ovh_dns: state=present domain=mydomain.com name=db1 value=10.10.10.10

# Create a CNAME record
- ovh_dns: state=present domain=mydomain.com name=dbprod type=cname value=db1

# Delete an existing record, must specify all parameters
- ovh_dns: state=absent domain=mydomain.com name=dbprod type=cname value=db1
'''

import os
import sys

try:
    import ovh
except importerror:
    print "failed=true msg='ovh required for this module'"
    sys.exit(1)

try:
    import sshpubkeys
except importerror:
    print "failed=true msg='sshpubkeys required for this module'"
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
            publicKey = dict(required=True),
            region = dict(default=None),
            state = dict(default='present', choices=['present', 'absent']),
        )
    )

    # Get parameters
    name = module.params.get('name')
    project_name = module.params.get('project_name')
    publicKey = module.params.get('publicKey')
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
	
    # Check if the volume exists
    volumes = client.get('/cloud/project/{}/volume'.format(project_id))
    volume_exist = False
    volume_identical = False
    for volume in volumes:
        volume = client.get('/cloud/project/{}/volume/{}'.format(project_id, volume['id']))
        if name == volume['name']:
            volume_exist = True
            if publicKey == volume['publicKey']:
                volume_identical = True
                break
            else:
                break

    # Remove a volume
    if state == 'absent':
        if not volume_exist:
            module.exit_json(changed=False)
        else:
            # Remove the volume
            client.delete('/cloud/project/{}/volume/{}'.format(project_id, volume['id']))
            module.exit_json(changed=True)

    # Add / modify a volume (modify doesn't handle region update)
    if state == 'present':
        if not volume_exist:
            client.post('/cloud/project/{}/volume'.format(project_id), name=name, publicKey=publicKey, region=region)
            module.exit_json(changed=True)
        elif volume_exist and not volume_identical:
            client.delete('/cloud/project/{}/volume/{}'.format(project_id, volume['id']))
            client.post('/cloud/project/{}/volume'.format(project_id), name=name, publicKey=publicKey, region=region)
            module.exit_json(changed=True)
        elif volume_exist and volume_identical:
            module.exit_json(changed=False)

# import module snippets
from ansible.module_utils.basic import *

main()
