#!/bin/env python3

from distutils.core import setup
import py2exe

setup(name='pmp3',
      version='1.0b',
      description='Fetch Music files from Palco MP3.',
      author='Victor A. Santos',
      author_email='victoraur.santos@gmail.com',
      url='https://github.com/hotvic/pmp3',
      py_modules=['src.pmp3'],
      console=['src/pmp3.py']
      )