"""Parse and validate the main cfg and project configs"""

import json
import os
import re

import yaml

import gws
import gws.core.spec
import gws.tools.misc
import gws.tools.os2
import gws.tools.vendor.chartreux as chartreux
import gws.tools.vendor.slon as slon

from . import error, spec

config_path_pattern = r'\bconfig\.(py|json|yaml|cx)$'
config_function_name = 'config'


def parse(dct, type_name, source_path=''):
    """Parse a dictionary according to the klass spec and return a config (Data) object"""

    try:
        return spec.validator().read_value(dct, type_name, source_path)
    except gws.core.spec.Error as e:
        raise error.ParseError(*e.args)


def parse_main(path):
    """Read and parse the main config file"""

    dct, cfg_paths = _read(path)

    prj_configs = []

    for pc in dct.pop('projects', []):
        prj_configs.append([pc, path])

    gws.log.info('parsing main configuration...')
    app = parse(dct, 'gws.common.application.Config', path)

    app.projectPaths = app.projectPaths or []
    app.projectDirs = app.projectDirs or []

    prj_paths = app.projectPaths
    for dirname in app.projectDirs:
        prj_paths.extend(gws.tools.os2.find_files(dirname, config_path_pattern))

    for prj_path in sorted(set(prj_paths)):
        prj_cfg, prj_cfg_paths = _read(prj_path)
        cfg_paths.extend(prj_cfg_paths)

        if not isinstance(prj_cfg, list):
            prj_cfg = [prj_cfg]
        for pc in prj_cfg:
            prj_configs.append([pc, prj_path])

    app.projects = []

    for pc, prj_path in prj_configs:
        uid = pc.get('uid') or pc.get('title') or '???'
        gws.log.info(f'parsing project {uid!r}...')
        if pc.get('multi'):
            app.projects.extend(_parse_multi_project(pc, prj_path))
        else:
            app.projects.append(parse(pc, 'gws.common.project.Config', prj_path))

    return app, cfg_paths


def _read(path):
    if not os.path.isfile(path):
        raise error.ParseError('file not found', path, '', '')
    try:
        dct, paths = _read2(path)
    except Exception as e:
        raise error.ParseError('read error: %s' % e, path, '', '') from e

    _save_intermediate(path, json.dumps(dct, indent=4), 'json')
    return dct, paths


def _read2(path):
    if path.endswith('.py'):
        mod_name = 'gws.cfg.' + gws.as_uid(path)
        mod = gws.tools.misc.load_source(path, mod_name)
        fn = getattr(mod, config_function_name)
        dct = fn()
        return dct, [path]

    if path.endswith('.json'):
        with open(path, encoding='utf8') as fp:
            dct = json.load(fp)
        return dct, [path]

    if path.endswith('.yaml'):
        with open(path, encoding='utf8') as fp:
            dct = yaml.load(fp)
        return dct, [path]

    if path.endswith('.cx'):
        return _parse_cx_config(path)


def _parse_cx_config(path):
    paths = {path}

    def _err(exc, path, line):
        return _syntax_error(gws.read_file(path), repr(exc), line)

    def _finder(cur_path, p):
        if not os.path.isabs(p):
            d = os.path.dirname(cur_path)
            p = os.path.abspath(os.path.join(d, p))
        paths.add(p)
        return p

    try:
        tpl = chartreux.compile_path(
            path,
            syntax={'start': '{{', 'end': '}}'},
            finder=_finder
        )
    except chartreux.compiler.Error as e:
        return _syntax_error(gws.read_file(path), e.message, e.line)

    src = chartreux.call(
        tpl,
        context={'true': True, 'false': False},
        error=_err)

    _save_intermediate(path, src, 'slon')

    try:
        dct = slon.loads(src, as_object=True)
    except slon.DecodeError as e:
        return _syntax_error(src, e.args[0], e.args[1])

    return dct, list(paths)


def _syntax_error(src, message, line, context=10):
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
    raise ValueError('syntax error')


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

    for index, p in enumerate(sorted(gws.tools.os2.find_files(dirname, mm))):
        gws.log.info(f'multi-project: found {p!r}')
        m = re.search(mm, p)
        args = {'$' + str(n): s for n, s in enumerate(m.groups(), 1)}
        args['$0'] = p
        args['index'] = str(index)
        args.update(gws.tools.os2.parse_path(p))
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


def _save_intermediate(path, txt, ext):
    p = gws.tools.os2.parse_path(path)
    d = gws.VAR_DIR + '/config'
    gws.write_file(f"{d}/{p['name']}.parsed.{ext}", txt)
