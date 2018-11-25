#!/usr/bin/env python

from setuptools import setup

setup(name='NameService',
      version='0.8',
      install_requires=[],
      description='Yet another CosNamong Service for OpenRTM-aist',
      author='Isao Hara, AIST',
      author_email='isao-hara@aist.go.jp',
      license='The MIT License',
      url='https://github.com/haraisao/NameServer/',
      packages=['NameService'],
      entry_points="""
      [console_scripts]
      NameServer = NameService.main:name_server
      """,
    ) 
