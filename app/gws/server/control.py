import time

import psutil

import gws
import gws.config.loader
import gws.gis.mpx.config
import gws.tools.date
import gws.tools.json2
import gws.tools.misc as misc
import gws.tools.shell as sh
import gws.types
from . import ini

commands_path = gws.VAR_DIR + '/server.sh'
pid_dir = misc.ensure_dir('pids', '/tmp')


def start():
    stop()

    cfg = configure()
    gws.tools.date.set_system_time_zone(cfg.get('timeZone'))

    for p in misc.find_files(gws.SERVER_DIR, '.*'):
        sh.unlink(p)

    commands = ini.create(gws.SERVER_DIR, pid_dir)

    with open(commands_path, 'wt') as fp:
        fp.write('\n'.join(commands))


def stop():
    for p in misc.find_files(pid_dir, 'uwsgi'):
        _kill(p)
    for p in misc.find_files(pid_dir, 'nginx'):
        _kill(p)

    time.sleep(1)

    while _is_running('uwsgi'):
        gws.log.info('waiting for uwsgi to quit...')
        time.sleep(1)

    while _is_running('nginx'):
        gws.log.info('waiting for nginx to quit...')
        time.sleep(1)


def reload():
    _reload(True)


def reset(module):
    _reload(False, module)


def reload_uwsgi(module):
    pattern = f'({module}).uwsgi.pid'
    for p in misc.find_files(pid_dir, pattern):
        gws.log.info(f'reloading {p}...')
        sh.run(['uwsgi', '--reload', p])


def configure():
    cfg = gws.config.loader.parse_and_activate()
    if gws.config.var('server.mapproxy.enabled'):
        gws.gis.mpx.config.create_and_save(ini.MAPPROXY_YAML_PATH)
    gws.config.loader.store()
    gws.log.info('CONFIGURATION OK')
    return cfg


def _reload(reconfigure, module=None):
    if not _is_running('uwsgi'):
        gws.log.info('server not running, starting...')
        return start()

    if reconfigure:
        configure()

    for m in ('qgis', 'mapproxy', 'web'):
        if not module or m == module:
            reload_uwsgi(m)


def _kill(pidfile):
    gws.log.info(f'stopping {pidfile}...')
    with open(pidfile, 'rt') as fp:
        pid = fp.read().strip()
    sh.run(['kill', '-INT', pid])


def _is_running(s):
    for proc in psutil.process_iter():
        cmd = str(proc.cmdline()).lower()
        if s in cmd:
            return True
