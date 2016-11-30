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
module: ovh_cloud_project
author: Benoît Pourre
short_description: Manage OVH Cloud projects
description:
    - Manage OVH (French European hosting provider) Cloud projects
requirements: [ "ovh" ]
options:
    description:
        required: true
        description:
            - Name or description of the project
    voucher:
        required: false
        description:
            - Voucher for the project
    state:
        required: false
        default: present
        choices: ['present', 'absent']
        description:
            - Determines wether the project is to be created or deleted
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
except ImportError:
    print "failed=True msg='ovh required for this module'"
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
            description = dict(required=True),
            voucher = dict(required=False),
            state = dict(default='present', choices=['present', 'absent']),
        )
    )

    # Get parameters
    description = module.params.get('description')
    voucher = module.params.get('voucher')
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
	
    # Remove a project
    if state == 'absent':
        if not project_exist:
            module.exit_json(changed=False)
        else:
            # Remove the project
            client.delete('/cloud/project/{}'.format(project_id))
            module.exit_json(changed=True)

    # Add a project, no update
    if state == 'present':
        if not project_exist:
            newproject = client.post('/cloud/createProject'.format(project), description=description, voucher=voucher)
            module.exit_json(changed=True, project=newproject)
        else:
            module.exit_json(changed=False, project=project)

# import module snippets
from ansible.module_utils.basic import *

main()
