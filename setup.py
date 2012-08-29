from distutils.core import setup
import os

setup(
    name='libscampi',
    version='4.1',
    py_modules=['contrib','core','utils'],
    url='https://github.com/azpm/django-scampi-cms',
    package_dir={'libscampi': 'libscampi'},
    packages=packages,
    package_data={'libscampi': data_files},
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
