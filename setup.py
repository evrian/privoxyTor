from setuptools import setup

setup(name='privoxyTor',
    version='0.1.0',
    description='Spawn multiple tor circuits',
    url='http://givedaps.com',
    author='gaysoda',
    author_email='gaysoda@givedaps.com',
    license='MIT',
    packages=['privoxytor'],
    package_data={'privoxytor': ['bin/torrc', 'bin/config_multi']},
    zip_safe=False)
