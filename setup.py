from setuptools import setup

setup(
    name='netbox-portal-access',
    version='0.2.0',
    description='NetBox plugin to track multi-vendor portal access & roles.',
    author='William Bunce',
    license='MIT',
    packages=['netbox_portal_access'],
    install_requires=[
        'netbox>=4.4.1',
    ],
)
