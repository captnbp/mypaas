# mypaas
MyPaas by D2-SI is an Ansible playbook for startups or small companies which want to build a modern and fully automated infrastructure.

This infrastructure will be composed by :
 - Ubuntu 16.04 VPS VMs on OVH Public Cloud
 - Docker Swarm
 - A software factory
  - Gitlab
  - Jenkins
 - Monitoring with DatadogHQ
 - Team chat with Slack
 - Productivity tools 
  - Odoo
  - Owncloud
  - Dokuwiki (soon)
  - Team password manager (soon)
 - Automatic encrypted backup with Duplicity and OVH Cloud Storage
 - Security
  - Let's Encrypt
  - OpenLDAP
  - OpenVPN
  - Fail2ban
  - Log management with OVH PaaS Logs (soon)
  - Vulnerability scanner with OpenVAS and CoreOS Clair (soon)
 - And more !
 
## Preparation

 1. Create a free account on DatadogHQ and get the api key, and the app key (`datadog.api_key` and `datadog.app_key`)
 2. Create an account on Slack and get a token (`slack.team` and `slack.token`)
 3. Create 2 sets of SSH keys for Gitlab (`jenkins.gitlab_webhook_publickey`, `jenkins.gitlab_webhook_privatekey`) and Jenkins Slave (`jenkins.jenkins_slave_privatekey`)
 4. Create a password for Docker Registry and generate its htpasswd string with http://www.htaccesstools.com/htpasswd-generator/ (`registry.pass` and `registry.htpasswd_pass`)
 5. Create an OVH account, create a Cloud project with paiement options
 6. Create your OVH API tokens with all permissions on cloud and domain endpoints : https://eu.api.ovh.com/createToken/ (o`vh.project`, `ovh.region`, `ovh.application_key`, `ovh.application_secret`, `ovh.endpoint`, `ovh.consumer_key`)
 7. Create your OVH domain name (`tld_hostname` and `top_dn)`
 8. Create an admin mail account on your domain name (`mail.*`)
 9. Generate many passwords, passphrases, secret keys, encrypting keys with `pwgen 64 20`
 10. Rename `vars.yml-template` to `vars.yml`
 11. Fill every field in `vars.yml` with everything we just generated
 
 ## Install
 
 1. Create all elements of your cloud project : `ansible-playbook -i ansible_hosts --ask-sudo-pass main.yml`
 2. Create your VMs and install all the tools : `ansible-playbook -i ansible_hosts --ask-sudo-pass deploy.yml`
  

