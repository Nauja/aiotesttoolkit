from setuptools import find_packages, setup

version = __import__('testtoolkit').__version__

setup(
    name='testtoolkit',
    version=version,
    url='https://github.com/Nauja/testtoolkit/',
    author='Jeremy Morosi',
    author_email='jeremy.morosi.dev@gmail.com',
    description=('A lightweight toolkit for unit testing.'),
    classifiers=[
        'Framework :: TestToolkit',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    packages=find_packages()
)