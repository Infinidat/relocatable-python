TRICK = """
# isolated-python trick
import sys
prefix = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.prefix  # virtualenv
old_prefix = build_time_vars.get("prefix", "_some_path_that_does_not_exist")

for key, value in build_time_vars.items():
    build_time_vars[key] = value.replace(old_prefix, prefix) if isinstance(value, basestring) else value
"""

def get_sysconfigdata_files(environ):
    from glob import glob
    from os import path
    dist = path.join(environ.get("PWD"), path.abspath(path.join('.',  # Python-2.7.6
                                                                path.pardir,  # python__compile__,
                                                                path.pardir,  # parts,
                                                                path.pardir,  # python-build
                                                                "dist")))
    print 'dist = {0}'.format(dist)
    print 'sysconfig = {0!r}'.format(glob(path.join(dist, "*", "*", "_sysconfigdata.py")))
    for _sysconfigdata in glob(path.join(dist, "*", "*", "_sysconfigdata.py")):
        yield _sysconfigdata


def purge_sysconfigdata(path):
    with open(path, 'a') as fd:
        fd.write(TRICK)


def fix_linker_rpath(path):
    # we want to link against the .so files in python/lib, but in Solaris
    # $ORIGIN may point to the package .so file location (instead of the python
    # binary location), and these files may be deep under site-packages
    # (e.g. python/lib/python2.7/site-packages/lxml-3.4.1-py2.7-linux-i686.egg/lxml)
    # so we add some $ORIGIN/../../../.... to rpath in linker options
    src_str = r"-Wl,-rpath,\\$ORIGIN/../.."
    rpaths = ''.join([",-rpath,\\$ORIGIN" + ("/.." * i) for i in range(3, 8)])
    dst_str = src_str + rpaths
    with open(path, 'r') as fd:
        data = fd.read()
    data = data.replace(src_str, dst_str)
    with open(path, 'w') as fd:
        fd.write(data)


def fix_sysconfigdata(options, buildout, environ):
    for path in get_sysconfigdata_files(environ):
        purge_sysconfigdata(path)
        fix_linker_rpath(path)
