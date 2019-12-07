"""Parse and validate the main cfg and project configs"""

import json
import os
import re

import yaml

import gws
import gws.types
import gws.types.spec
import gws.tools.misc
import gws.tools.chartreux
import gws.tools.slon

from . import error, spec

config_path_pattern = r'\bconfig\.(py|json|yaml)$'
config_function_name = 'config'


def parse(dct, type_name, source_path=''):
    """Parse a dictionary according to the klass spec and return a config (Data) object"""

    try:
        return spec.validator().read_value(dct, type_name, source_path)
    except gws.types.spec.Error as e:
        raise error.ParseError(*e.args)


def parse_main(path):
    """Read and parse the main config file"""

    dct = _read(path) or {}

    with open(gws.VAR_DIR + '/config/config.parsed.json', 'wt') as fp:
        json.dump(dct, fp, indent=4, ensure_ascii=False)

    prj_configs = []
    for pc in dct.pop('projects', []):
        prj_configs.append([pc, path])

    gws.log.info('parsing main configuration...')
    cfg = parse(dct, 'gws.common.application.Config', path)

    prj_paths = cfg.get('projectPaths') or []
    for dirname in cfg.get('projectDirs') or []:
        prj_paths.extend(gws.tools.misc.find_files(dirname, config_path_pattern))

    for prj_path in sorted(set(prj_paths)):
        pcs = _read(prj_path)
        if not isinstance(pcs, list):
            pcs = [pcs]
        for pc in pcs:
            prj_configs.append([pc, prj_path])

    cfg.projects = []

    for pc, prj_path in prj_configs:
        try:
            uid = pc.get('uid') or pc.get('title')
        except:
            uid = 'unknown'
        gws.log.info(f'parsing project {uid!r}...')
        if pc.get('multi'):
            cfg.projects.extend(_parse_multi_project(pc, prj_path))
        else:
            cfg.projects.append(parse(pc, 'gws.common.project.Config', path))

    return cfg


def _read(path):
    if not os.path.exists(path):
        raise error.ParseError('file not found', path, '', '')
    try:
        return _read2(path)
    except Exception as e:
        raise error.ParseError('read error: %s' % e, path, '', '') from e


def _read2(path):
    if path.endswith('.py'):
        mod_name = 'gws.cfg.' + gws.as_uid(path)
        mod = gws.tools.misc.load_source(path, mod_name)
        fn = getattr(mod, config_function_name)
        return fn()

    if path.endswith('.json'):
        with open(path, encoding='utf8') as fp:
            return json.load(fp)

    if path.endswith('.yaml'):
        with open(path, encoding='utf8') as fp:
            return yaml.load(fp)

    if path.endswith('.cx'):
        return _parse_cx_config(path)


def _parse_cx_config(path):
    try:
        tpl = gws.tools.chartreux.compile_path(
            path,
            syntax={'start': '{{', 'end': '}}'},
        )
    except gws.tools.chartreux.compiler.Error as e:
        with open(e.path) as fp:
            _display_syntax_error(fp.read(), e.message, e.line)
        raise ValueError('syntax error')

    def err(exc, path, line):
        with open(path) as fp:
            _display_syntax_error(fp.read(), repr(exc), line)
        raise ValueError('syntax error')

    src = gws.tools.chartreux.call(
        tpl,
        context={'true': True, 'false': False},
        error=err)

    with open(gws.VAR_DIR + '/config/config.parsed.slon', 'wt') as fp:
        fp.write(src)

    try:
        return gws.tools.slon.loads(src, as_object=True)
    except gws.tools.slon.DecodeError as e:
        _display_syntax_error(src, e.args[0], e.args[1])
        raise ValueError('syntax error')


def _display_syntax_error(src, message, line, context=10):
    gws.log.error('CONFIGURATION SYNTAX ERROR')
    gws.log.error(message)
    gws.log.error('-' * 40)
    for n, t in enumerate(src.splitlines(), 1):
        if n < line - context:
            continue
        if n > line + context:
            break
        t = str(n) + ': ' + t
        if n == line:
            t = '>>>' + t
        gws.log.error(t)


def _parse_multi_project(cfg, path):
    mm = cfg.pop('multi')
    pfx = re.match(r'^/([\w-]+/)*', mm)
    if pfx:
        # absolute multi match like /foo/bar.*/baz? - try to extract the base path
        dirname = pfx.group(0)
        if dirname == '/':
            raise error.ParseError('multi-project: pattern cannot be root', path, '', mm)
    else:
        dirname = os.path.dirname(path)

    if not os.path.isdir(dirname):
        raise error.ParseError(f'multi-project: {dirname!r} not found', path, '', mm)

    res = []

    for index, p in enumerate(sorted(gws.tools.misc.find_files(dirname, mm))):
        gws.log.info(f'multi-project: found {p!r}')
        m = re.search(mm, p)
        args = {'$' + str(n): s for n, s in enumerate(m.groups(), 1)}
        args['$0'] = p
        args['index'] = str(index)
        args.update(gws.tools.misc.parse_path(p))
        dct = _deep_format(cfg, args)
        res.append(parse(dct, 'gws.common.project.Config', path))

    if not res:
        gws.log.warn(f'multi-project: no files found for {mm!r}')

    return res


_multi_placeholder_re = r'{{(.+?)}}'


def _deep_format(x, a):
    if isinstance(x, dict):
        return {k: _deep_format(v, a) for k, v in x.items()}
    if isinstance(x, list):
        return [_deep_format(v, a) for v in x]
    if isinstance(x, str):
        return re.sub(_multi_placeholder_re, lambda m: a.get(m.group(1), m.group(0)), x)
    return x
