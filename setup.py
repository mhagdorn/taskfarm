from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc

name = 'taskfarm'
version = '0.2'
release = '0.2.0'
author = 'Magnus Hagdorn'

setup(
    name=name,
    packages=find_packages(),
    version=release,
    include_package_data=True,
    cmdclass={'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'copyright': ('setup.py', author),
            'source_dir': ('setup.py', 'docs')}},
    setup_requires=['sphinx'],
    install_requires=[
        "sqlalchemy",
        "flask>=1.0",
        "flask_sqlalchemy",
        "itsdangerous",
        "passlib",
        "flask-httpauth",
    ],
    extras_require={
        'docs': [
            'sphinx<4.0',
            'sphinx_rtd_theme',
            'sphinxcontrib.httpdomain',
        ],
        'lint': [
            'flake8>=3.5.0',
        ],
        'testing': [
            'nose2',
            'flask-testing',
        ],
    },
    entry_points={
        'console_scripts': [
            'taskfarm=taskfarm.app:main',
            'adminTF=taskfarm.manage:main',
        ]
    },
    test_suite='nose2.collector.collector',
    author=author,
    description="database backed taskfarm controller",
)
