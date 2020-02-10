#!/usr/bin/env python
from setuptools import setup

setup(
    name='solo_agent',
    version='0.10.0',
    description='Using Solo as hardware SSH/GPG agent',
    author='Roman Zeyde',
    author_email='roman.zeyde@gmail.com',
    url='http://github.com/romanz/trezor-agent',
    scripts=['solo_agent.py'],
    install_requires=[
        'libagent>=0.13.0',
        'solo-python>=0.0.23'
    ],
    platforms=['POSIX'],
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Communications',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    entry_points={'console_scripts': [
        'solo-agent = solo_agent:ssh_agent',
        'solo-gpg = solo_agent:gpg_tool',
        'solo-gpg-agent = solo_agent:gpg_agent',
    ]},
)
