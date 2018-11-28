from setuptools import setup, find_packages

setup(
    name = "taskfarm",
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "sqlalchemy",
        "flask",
        "flask_sqlalchemy",
        "itsdangerous",
        "passlib",
        "flask-httpauth",
    ],
    entry_points={
        'console_scripts': [
            'taskfarm = taskfarm.app:main',
            'manageTF = taskfarm.manage:main',
            ]
        },
    author = "Magnus Hagdorn",
    description = "database backed taskfarm controller",
)
