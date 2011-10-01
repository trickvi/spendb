import os
from setuptools import setup, find_packages

from openspending.version import __version__

PKG_ROOT = '.'

def files_in_pkgdir(pkg, dirname):
    pkgdir = os.path.join(PKG_ROOT, *pkg.split('.'))
    walkdir = os.path.join(pkgdir, dirname)
    walkfiles = []
    for dirpath, _, files in os.walk(walkdir):
        fpaths = (os.path.relpath(os.path.join(dirpath, f), pkgdir)
                  for f in files)
        walkfiles += fpaths
    return walkfiles

def package_filter(pkg):
    if pkg in ['openspending.test', 'openspending.test.helpers']:
        return True
    elif (pkg.startswith('openspending.test') or
          pkg.startswith('openspending.ui.test')):
        return False
    else:
        return True

setup(
    name='openspending',
    version=__version__,
    description='OpenSpending',
    author='Open Knowledge Foundation',
    author_email='okfn-help at lists okfn org',
    url='http://github.com/okfn/openspending',

    install_requires=[
        "WebOb==1.0.8", # Explicitly specify WebOb 1.0.8, as with 1.1
                        # integration with Pylons is broken:
                        # see https://gist.github.com/1214075
        "Pylons==1.0",
        "Genshi==0.6",
        "pymongo==1.11",
        "repoze.who==2.0b1",
        "repoze.who-friendlyform==1.0.8",
        "Unidecode==0.04.7",
        "python-dateutil==1.5",
        "solrpy==0.9.4",
        "pyutilib.component.core==4.3.1",
        "Babel==0.9.6",
        "colander==0.9.3",
        "distribute>=0.6.10",
        "mock==0.7.2",
        "sphinx==1.0.7",
        "argparse==1.2.1"
    ],
    setup_requires=[
        "PasteScript==1.7.4.2",
        "nose==1.1.2"
    ],

    packages=filter(package_filter, find_packages()),
    namespace_packages=['openspending', 'openspending.plugins'],
    package_data={
        'openspending.model': files_in_pkgdir('openspending.model', 'serverside_js'),
        'openspending.ui': (
            files_in_pkgdir('openspending.ui', 'public') +
            files_in_pkgdir('openspending.ui', 'templates')
        )
    },
    test_suite='nose.collector',

    zip_safe=False,

    paster_plugins=['PasteScript', 'Pylons'],

    entry_points={
        'paste.app_factory': [
            'main = openspending.ui.config.middleware:make_app'
        ],
        'paste.app_install': [
            'main = pylons.util:PylonsInstaller'
        ],
        'console_scripts': [
            'ostool = openspending.command:main'
        ]
    }
)
