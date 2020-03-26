from setuptools import setup, find_packages

setup(
    name="taskfarm",
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['nose2', 'flask-testing'],
    install_requires=[
        "sqlalchemy",
        "flask>=1.0",
        "flask_sqlalchemy",
        "itsdangerous",
        "passlib",
        "flask-httpauth",
    ],
    entry_points={
        'console_scripts': [
            'taskfarm=taskfarm.app:main',
            'adminTF=taskfarm.manage:main',
            ]
        },
    test_suite='nose2.collector.collector',
    author="Magnus Hagdorn",
    description="database backed taskfarm controller",
)
