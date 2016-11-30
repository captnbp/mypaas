#!/usr/bin/python

# Copyright 2015 Cornelius Keller

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
DOCUMENTATION = '''
---
module: ovh
short_description: Ansible module to access ovh, kimsufi, soyoustart and runabove apis
options:
   endpoint: 
     - The ovh api endpoint. Must be one of 'ovh-eu', 'ovh-ca', 'soyoustart-eu', 'soyoustart-ca', 'kimsufi-eu', 'kimsufi-ca', 'runabove-ca'.
   application_key:
     - Your ovh api application_key
   application_secret: 
     - Your ovh api application_secret
   consumer_key: 
     - Your ovh api consumer_key
   method: 
     - The request method
   uri:
     - The uri to call
   args: 
     - the args for post or put requests
author:
   - Cornelius Keller
notes: 
   - Requires python ovh api. Install with pip install ovh
'''

EXAMPLES = '''
      - name:  get servers
        ovh:
          method: get
          endpoint: kimsufi-eu
          application_key: < application_key >
          application_secret: < application secret >
          consumer_key: < consumer key >
          uri: /dedicated/server

      - name:  set rescue boot
        ovh:
          method: put
          endpoint: kimsufi-eu
          application_key: < application_key >
          application_secret: < application secret >
          consumer_key: < consumer key >
          uri: /dedicated/server/< server name >
          args:
              bootId: 22

'''


from ansible.module_utils.basic import *


module = AnsibleModule(
    argument_spec = dict(
        endpoint     = dict(required=True, choices=['ovh-eu', 'ovh-ca', 'soyoustart-eu', 'soyoustart-ca', 'kimsufi-eu', 'kimsufi-ca', 'runabove-ca']),
        application_key      = dict(required=True),
        application_secret   = dict(required=True),
        consumer_key = dict(required=True),
        method = dict(required=True, choices=['get','put','post','delete']),
        uri = dict(required=True),
        args = dict(default={})
    )
)

from ovh import Client

def main():
    client = Client(endpoint=module.params['endpoint'], application_key=module.params['application_key'], application_secret=module.params['application_secret'], consumer_key=module.params['consumer_key'])
    method = getattr(client, module.params['method'])

    if module.params['args'] == {}:
       res =  method(module.params['uri']) # module.params['args'])
    else:
       res =  method(module.params['uri'], **module.params['args'])

    module.exit_json(changed=True, result=res)

if __name__ == '__main__':
    main()
