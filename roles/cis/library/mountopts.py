from ansible.module_utils.basic import AnsibleModule
import os.path

try:
    import fstab
    HAS_FSTAB_LIB = True
except:
    HAS_FSTAB_LIB = False


def find_mount(ft, directory):
    for l in ft.lines:
        if l.has_filesystem() and l.directory == directory:
            return l


def parse_options(options):
    parsed = {}

    for opt in options:
        if '=' in opt:
            opt = opt.split('=')
            parsed[opt[0]] = opt[1]
        else:
            parsed[opt] = None

    return parsed


def dump_options(options):
    dumped = []

    for opt, val in options.iteritems():
        if val is None:
            dumped.append(opt)
        else:
            dumped.append("{}={}".format(opt, val))

    return dumped


def main():
    module = AnsibleModule(
        argument_spec = dict(
            fstab  = dict(default='/etc/fstab', type='path'),
            name   = dict(required=True, type='path'),
            state  = dict(default='present', choices=['present', 'absent']),
            option = dict(required=True),
            value  = dict(),
        )
    )

    if not HAS_FSTAB_LIB:
        module.fail_json(msg='missing the `fstab` python module')

    if not os.path.exists(module.params['fstab']):
        module.fail_json(msg='given fstab file does not exist: ' + module.params['fstab'])

    changed = None

    ft = fstab.Fstab()
    ft.read(module.params['fstab'])

    line = find_mount(ft, module.params['name'])

    if not line:
        odule.fail_json(msg='given mountpoint does not exist: {}. You can create it using the mount-module.'.format(module.params['name']))

    opts = parse_options(line.get_options())

    if module.params['state'] == 'present':
        if module.params['value']:
            changed = (opts.get(module.params['option'], None) != module.params['value'])
            opts[module.params['option']] = module.params['value']
        else:
            changed = (module.params['option'] not in opts)
            opts[module.params['option']] = None
    elif module.params['state'] == 'absent':
        if module.params['option'] in opts:
            del opts[module.params['option']]
            changed = True
        else:
            changed = False
    else:
        raise module.fail_json(msg='parameter "state": unknown value')

    line.set_options(dump_options(opts))
    ft.write(module.params['fstab'])

    if changed is None:
        raise module.fail_json(msg='bug: no changed value was set')

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
