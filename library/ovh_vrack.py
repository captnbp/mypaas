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
module: ovh_vrack
author: Yanis BELLAL
short_description: Manage OVH vRacks

'''

import os
import sys

try:
    import ovh
except ImportError:
    print "failed=True msg='ovh required for this module'"
    sys.exit(1)


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
            state = dict(required=True),
        )
    )

    # Get parameters
    description = module.params.get('description')
    project_name = module.params.get('project_name')
    state = module.params.get('state')

    # Connect to OVH API
    client = ovh.Client()
   #checking Cloud projects
    result2 = client.get('/cloud/project')
    project_exist = False
    for project_id in result2:
	    project = client.get('/cloud/project/{}'.format(project_id))
	    if project_name == project['description']:
	        project_exist = True
		break
    #get vrack
    vrack_exist = False
    result2 = client.get('/vrack')
    if not result2:
        # create vrack
        create_vrack= client.post('/order/vrack/new')
        orderid=create_vrack['orderId']
        #pay vrack order by order Id
        vrack_pay = client.post('/me/order/{}/payWithRegisteredPaymentMean'.format(orderid),paymentMean='fidelityAccount')
        # check vrack order status
        order_stat_vrack = client.get('/me/order/{}/status'.format(orderid))
        counter=0
        while (order_stat_vrack!='delivered') and (counter!=4):  # This constructs an infinite loop
           counter+=1
	   order_stat_vrack = client.get('/me/order/{}/status'.format(orderid))
           time.sleep(40)

        if counter == 4:
           print 'Vrack creation timeout'
           exit
        if order_stat_vrack=='delivered':
            vrack_status='DONE'
            vrack_id = client.get('/vrack')
            vrack_details = client.get('/vrack/{}'.format(vracks_id))
            module.exit_json(changed=True, vrack=vrack_id)
    else:
        vrack_exist= True
        #check vrack details
        for vracks_id in result2:
            vrack_details = client.get('/vrack/{}'.format(vracks_id))
            vrack_id=vracks_id
    	    print ('There is an available vrack:{}'.format(vrack_id))
            module.exit_json(changed=False, vrack=vrack_id)
    	    break
# import module snippets
from ansible.module_utils.basic import *
main()
